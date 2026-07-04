#!/usr/bin/env python3
"""Browser-based dataset review server for LusoSupport-PT.

Serves a self-contained HTML UI at GET / and provides JSON API endpoints
for sampling rows, generating new rows, rating rows, and exporting ratings.

Run from the project root:
    python3 scripts/review_server.py [--port 8765] [--open]
"""
import json
import os
import random
import sys
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

# Resolve project root and add scripts to sys.path when imported as module
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from config import DOMAINS, TASK_TYPES, CUSTOMER_INTENTS
from responses import get_output
from templates import build_instruction

# ---------------------------------------------------------------------------
# Paths (relative to project root — server chdirs to root on startup)
# ---------------------------------------------------------------------------

PROCESSED_PATH = Path("datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR   = Path("datasets/feedback")
SEEDS_PATH     = Path("datasets/raw/seed_examples.jsonl")


# ---------------------------------------------------------------------------
# Helper functions (importable for tests)
# ---------------------------------------------------------------------------

def load_rows(path: Path = PROCESSED_PATH) -> list:
    """Return all rows from a JSONL file. Returns [] if file is missing."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_reviewed_ids(feedback_dir: Path = FEEDBACK_DIR) -> set:
    """Return set of row IDs already present in approved, rejected, or browser_ratings."""
    ids = set()
    for fname in ("approved.jsonl", "rejected.jsonl", "browser_ratings.jsonl"):
        p = feedback_dir / fname
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    if "id" in entry:
                        ids.add(entry["id"])
    return ids


def sample_row(rows: list, reviewed_ids: set, mode: str = "random") -> Optional[dict]:
    """Return one unreviewed row. mode='flagged' restricts to flagged.jsonl IDs."""
    if mode == "flagged":
        flagged_path = FEEDBACK_DIR / "flagged.jsonl"
        flagged_ids: set = set()
        if flagged_path.exists():
            for line in flagged_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    flagged_ids.add(json.loads(line)["id"])
        candidates = [r for r in rows if r["id"] in flagged_ids and r["id"] not in reviewed_ids]
    else:
        candidates = [r for r in rows if r["id"] not in reviewed_ids]
    return random.choice(candidates) if candidates else None


def build_generated_row(domain: str, task_type: str, intent: str, message: str) -> dict:
    """Build a synthetic row from user-supplied parameters."""
    ts_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "id": f"browser_generated_{ts_ms}",
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "subdomain": "placeholder",
        "task_type": task_type,
        "customer_intent": intent,
        "customer_tone": "formal",
        "agent_tone": "professional",
        "channel": "web_form",
        "difficulty": "medium",
        "instruction": build_instruction(task_type, "professional"),
        "input": f"Mensagem do cliente: {message}",
        "output": get_output(task_type, intent, domain=domain),
        "metadata": {
            "requires_escalation": False,
            "contains_pii": False,
            "synthetic": True,
            "source_type": "browser_generated",
        },
    }


def rate_row(row_id: str, rating: str, comment: str, row: dict,
             feedback_dir: Path = FEEDBACK_DIR) -> None:
    """Append rating to the appropriate feedback JSONL file."""
    feedback_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    if rating == "good":
        entry = {"id": row_id, "timestamp": ts}
        path = feedback_dir / "approved.jsonl"
    elif rating == "bad":
        entry = {"id": row_id, "reason": comment if comment else "browser:bad", "timestamp": ts}
        path = feedback_dir / "rejected.jsonl"
    else:  # unclear
        entry = {"id": row_id, "rating": "unclear", "comment": comment, "timestamp": ts, "row": row}
        path = feedback_dir / "browser_ratings.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# HTTP handler placeholder (completed in Task 2)
# ---------------------------------------------------------------------------

_HTML = "<html><body>UI coming in Task 2</body></html>"


class ReviewHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress request logs
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(_HTML.encode())

    def do_POST(self):
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LusoSupport-PT browser review server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open browser tab on start")
    args = parser.parse_args()

    # Always run relative to project root
    os.chdir(_ROOT)

    server = HTTPServer(("", args.port), ReviewHandler)
    url = f"http://localhost:{args.port}"
    print(f"Browser review → {url}  (Ctrl-C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
