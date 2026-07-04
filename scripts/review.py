"""review.py — Interactive human review for LusoSupport-PT dataset.

Usage:
    python3 review.py [--mode random|flagged|all] [--n 20]
                      [--domain DOMAIN] [--task TASK_TYPE]

Keys during review:
    a  approve row   r  reject row   f  fix output inline
    s  skip          q  quit and save progress
"""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")
CHECKPOINT_FILE = FEEDBACK_DIR / ".review_checkpoint"

console = Console()


# ── I/O helpers ────────────────────────────────────────────────────────────────

def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def _append_jsonl(path: Path, entry: dict) -> None:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── feedback sets ──────────────────────────────────────────────────────────────

def _load_reviewed_ids() -> set:
    """IDs already reviewed (approved, rejected, or corrected) in any prior session."""
    ids = set()
    for fname in ["approved.jsonl", "rejected.jsonl", "corrections.jsonl"]:
        for entry in _load_jsonl(FEEDBACK_DIR / fname):
            ids.add(entry["id"])
    return ids


def _save_checkpoint(row_id: str) -> None:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(row_id, encoding="utf-8")


# ── row selection ──────────────────────────────────────────────────────────────

def _load_all_rows() -> list:
    return _load_jsonl(PROCESSED_PATH)


def _select_rows(mode: str, n: int, domain, task) -> list:
    if mode == "flagged":
        flagged = _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
        ids = {e["id"] for e in flagged}
        rows = [r for r in _load_all_rows() if r["id"] in ids]
    elif mode == "random":
        rows = _load_all_rows()
        random.shuffle(rows)
    else:  # all
        rows = _load_all_rows()

    if domain:
        rows = [r for r in rows if r.get("domain") == domain]
    if task:
        rows = [r for r in rows if r.get("task_type") == task]

    reviewed = _load_reviewed_ids()
    rows = [r for r in rows if r["id"] not in reviewed]
    return rows[:n]


# ── display ────────────────────────────────────────────────────────────────────

def _display_row(row: dict, index: int, total: int,
                 flag_reason=None) -> None:
    header = (
        f"Row {index}/{total}  ──  "
        f"[cyan]{row.get('domain','?')}[/cyan] / "
        f"[green]{row.get('task_type','?')}[/green] / "
        f"[yellow]{row.get('customer_intent','?')}[/yellow]"
    )
    if flag_reason:
        header += f"  ⚑ [red]{flag_reason}[/red]"

    body = (
        f"[bold]INPUT[/bold]\n{row.get('input', '')}\n\n"
        f"[bold]OUTPUT[/bold]\n{row.get('output', '')}"
    )

    console.print()
    console.print(Panel(body, title=header, border_style="blue", padding=(1, 2)))
    console.print(
        "  [bold][a][/bold]pprove  "
        "[bold][r][/bold]eject  "
        "[bold][f][/bold]ix inline  "
        "[bold][s][/bold]kip  "
        "[bold][q][/bold]uit"
    )


# ── actions ────────────────────────────────────────────────────────────────────

def _approve(row: dict) -> None:
    _append_jsonl(FEEDBACK_DIR / "approved.jsonl",
                  {"id": row["id"], "timestamp": _now()})
    console.print("[green]✓ Approved[/green]")


def _reject(row: dict) -> None:
    reason = input("  Rejection reason (optional, Enter to skip): ").strip()
    _append_jsonl(FEEDBACK_DIR / "rejected.jsonl",
                  {"id": row["id"], "reason": reason, "timestamp": _now()})
    console.print("[red]✗ Rejected[/red]")


def _fix(row: dict) -> None:
    console.print(
        "\n  Type the corrected output below. "
        "Press Enter twice (blank line) when done:\n"
    )
    lines = []
    while True:
        line = input("  > ")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    corrected = "\n".join(lines).strip()
    if corrected:
        _append_jsonl(FEEDBACK_DIR / "corrections.jsonl", {
            "id": row["id"],
            "original_output": row.get("output", ""),
            "corrected_output": corrected,
            "timestamp": _now(),
        })
        console.print("[blue]✎ Correction saved[/blue]")
    else:
        console.print("[yellow]Empty correction — skipped[/yellow]")


# ── main loop ──────────────────────────────────────────────────────────────────

def run_review(mode: str, n: int, domain, task) -> None:
    rows = _select_rows(mode, n, domain, task)
    if not rows:
        console.print(Rule())
        console.print("[yellow]No unreviewed rows found for the given filters.[/yellow]")
        return

    flag_reasons = {
        e["id"]: e["reason"]
        for e in _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
    }

    console.print(Rule("[bold]LusoSupport-PT — Review Session[/bold]"))
    console.print(
        f"Mode: [cyan]{mode}[/cyan]  |  "
        f"Rows to review: [cyan]{len(rows)}[/cyan]"
        + (f"  |  domain: [cyan]{domain}[/cyan]" if domain else "")
        + (f"  |  task: [cyan]{task}[/cyan]" if task else "")
    )

    for i, row in enumerate(rows, start=1):
        _save_checkpoint(row["id"])
        _display_row(row, i, len(rows), flag_reasons.get(row["id"]))

        while True:
            key = input("  > ").strip().lower()[:1]
            if key == "a":
                _approve(row)
                break
            elif key == "r":
                _reject(row)
                break
            elif key == "f":
                _fix(row)
                break
            elif key == "s":
                console.print("[dim]Skipped[/dim]")
                break
            elif key == "q":
                console.print("\n[bold]Session saved. Resume with the same command.[/bold]")
                sys.exit(0)
            else:
                console.print("  Invalid key. Use a / r / f / s / q")

    console.print(Rule())
    console.print(f"[green]Session complete — {len(rows)} reviewed.[/green]")
    CHECKPOINT_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive dataset review.")
    parser.add_argument("--mode", choices=["random", "flagged", "all"],
                        default="flagged")
    parser.add_argument("--n", type=int, default=20,
                        help="Max rows to review per session")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--task", default=None)
    args = parser.parse_args()

    run_review(args.mode, args.n, args.domain, args.task)
