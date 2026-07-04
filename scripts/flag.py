"""flag.py — Automated quality scanner for LusoSupport-PT dataset.

Reads the processed dataset, applies validate.py rules and heuristics,
and writes datasets/feedback/flagged.jsonl.

Usage:
    python3 flag.py [--processed PATH] [--feedback PATH]
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from validate import is_valid_row

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")

# Task types that produce free text (not JSON)
_TEXT_TASK_TYPES = {
    "response_generation", "email_reply", "summarization",
    "rewrite_professional", "next_action_suggestion", "faq_answer",
}


def _load_approved_ids(feedback_dir: Path) -> set:
    path = feedback_dir / "approved.jsonl"
    if not path.exists():
        return set()
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(json.loads(line)["id"])
    return ids


def _heuristic_flags(row: dict, bucket_outputs: dict) -> list:
    """Return list of heuristic reason strings; empty if none apply."""
    reasons = []
    task_type = row.get("task_type", "")
    output = row.get("output", "")
    domain = row.get("domain", "")
    bucket_key = (domain, task_type)

    # Heuristic 1: duplicate output within same domain × task_type bucket
    if output in bucket_outputs[bucket_key]:
        reasons.append("duplicate_in_bucket")
    else:
        bucket_outputs[bucket_key].add(output)

    if task_type in _TEXT_TASK_TYPES:
        # Heuristic 2: output-to-input length ratio < 0.5
        input_len = len(row.get("input", ""))
        if input_len > 0 and len(output) / input_len < 0.5:
            reasons.append("low_output_input_ratio")

        # Heuristic 3: single sentence for email_reply or response_generation
        if task_type in {"email_reply", "response_generation"}:
            sentences = [s.strip() for s in output.split(".") if s.strip()]
            if len(sentences) <= 1:
                reasons.append("single_sentence_email")

    return reasons


def scan_dataset(processed_path: Path, feedback_dir: Path,
                 approved_ids: set = None) -> list:
    """Scan the processed dataset and return a list of flagged entries.

    Each entry: {"id": str, "reason": str, "row": dict}
    Also writes flagged.jsonl to feedback_dir.
    """
    if approved_ids is None:
        approved_ids = _load_approved_ids(feedback_dir)

    rows = []
    for line in processed_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))

    flagged = []
    bucket_outputs = defaultdict(set)

    for row in rows:
        row_id = row.get("id", "")
        if row_id in approved_ids:
            continue

        # Pass 1: validate.py rules
        ok, reason = is_valid_row(row)
        if not ok:
            flagged.append({"id": row_id, "reason": reason, "row": row})
            continue  # don't also run heuristics on already-failed rows

        # Pass 2: heuristics (only first hit per row)
        heuristic_reasons = _heuristic_flags(row, bucket_outputs)
        if heuristic_reasons:
            flagged.append({"id": row_id, "reason": heuristic_reasons[0], "row": row})

    # Write flagged.jsonl
    feedback_dir.mkdir(parents=True, exist_ok=True)
    out_path = feedback_dir / "flagged.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for entry in flagged:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return flagged


def _print_summary(flagged: list) -> None:
    from rich.console import Console
    from rich.rule import Rule

    console = Console()
    console.print(Rule("[bold]LusoSupport-PT — Flag Report[/bold]"))

    if not flagged:
        console.print("[green]✓ No rows flagged.[/green]")
        return

    counts = Counter(entry["reason"] for entry in flagged)
    console.print(f"\n[yellow]Flagged {len(flagged)} rows across {len(counts)} rules:[/yellow]\n")
    for reason, count in counts.most_common():
        console.print(f"  [bold]{reason:<45}[/bold] {count} rows")
    console.print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-scan dataset for quality issues.")
    parser.add_argument("--processed", default=str(PROCESSED_PATH))
    parser.add_argument("--feedback", default=str(FEEDBACK_DIR))
    args = parser.parse_args()

    processed_path = Path(args.processed)
    feedback_dir = Path(args.feedback)
    approved_ids = _load_approved_ids(feedback_dir)

    flagged = scan_dataset(processed_path, feedback_dir, approved_ids)
    _print_summary(flagged)
