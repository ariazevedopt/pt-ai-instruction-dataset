"""quality_report.py — Template health report for LusoSupport-PT.

Reads feedback files and the processed dataset to surface the weakest
domain × task_type combinations based on rejection and flag rates.

Usage:
    python3 quality_report.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from rich.console import Console
from rich.rule import Rule
from rich.table import Table

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")

console = Console()


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def run_report() -> None:
    rows = _load_jsonl(PROCESSED_PATH)
    flagged = _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
    rejected = _load_jsonl(FEEDBACK_DIR / "rejected.jsonl")
    approved = _load_jsonl(FEEDBACK_DIR / "approved.jsonl")
    corrections = _load_jsonl(FEEDBACK_DIR / "corrections.jsonl")

    flagged_ids = {e["id"] for e in flagged}
    rejected_ids = {e["id"] for e in rejected}
    approved_ids = {e["id"] for e in approved}

    console.print(Rule("[bold]LusoSupport-PT — Quality Report[/bold]"))
    console.print(
        f"  [bold]{len(rows)}[/bold] total rows  |  "
        f"[yellow]{len(flagged_ids)}[/yellow] flagged  |  "
        f"[red]{len(rejected_ids)}[/red] rejected  |  "
        f"[green]{len(approved_ids)}[/green] approved  |  "
        f"[blue]{len(corrections)}[/blue] corrections"
    )
    console.print()

    # Flag reason breakdown
    if flagged:
        reason_counts = Counter(e["reason"] for e in flagged)
        console.print("[bold]Flag reasons:[/bold]")
        for reason, count in reason_counts.most_common(10):
            console.print(f"  {reason:<45} {count}")
        console.print()

    # Build per-row lookup (include rows embedded in flagged entries)
    row_lookup = {r["id"]: r for r in rows}
    for entry in flagged:
        if entry["id"] not in row_lookup and "row" in entry:
            row_lookup[entry["id"]] = entry["row"]

    # Domain × task_type buckets
    bucket_total: dict = defaultdict(int)
    bucket_rejected: dict = defaultdict(int)
    bucket_flagged: dict = defaultdict(int)

    for r in rows:
        key = (r.get("domain", "?"), r.get("task_type", "?"))
        bucket_total[key] += 1

    for entry in rejected:
        row = row_lookup.get(entry["id"])
        if row:
            key = (row.get("domain", "?"), row.get("task_type", "?"))
            bucket_rejected[key] += 1

    for entry in flagged:
        row = row_lookup.get(entry["id"])
        if row:
            key = (row.get("domain", "?"), row.get("task_type", "?"))
            bucket_flagged[key] += 1

    problem_buckets = set(bucket_rejected.keys()) | set(bucket_flagged.keys())
    if problem_buckets:
        table = Table(title="Weakest domain × task_type areas", show_lines=True)
        table.add_column("domain × task_type", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Rejected", justify="right", style="red")
        table.add_column("Flagged", justify="right", style="yellow")
        table.add_column("Issue rate", justify="right")

        rows_sorted = sorted(
            problem_buckets,
            key=lambda k: (bucket_rejected[k] + bucket_flagged[k]) / max(bucket_total[k], 1),
            reverse=True,
        )
        for key in rows_sorted[:15]:
            domain, task = key
            total = bucket_total[key]
            rej = bucket_rejected[key]
            flag = bucket_flagged[key]
            rate = (rej + flag) / total if total else 0
            bar = "▓" * int(rate * 10)
            table.add_row(
                f"{domain} × {task}",
                str(total),
                str(rej) if rej else "—",
                str(flag) if flag else "—",
                f"{rate:.0%} {bar}",
            )
        console.print(table)

        top = rows_sorted[0]
        console.print(
            f"\n[bold]→ Fix priority:[/bold] "
            f"responses.py templates for "
            f"[cyan]{top[0]}[/cyan] / [green]{top[1]}[/green]"
        )
    else:
        console.print("[green]No rejected or flagged rows found yet.[/green]")
        console.print(
            "Run [bold]make flag[/bold] then [bold]make review[/bold] "
            "to populate feedback."
        )


if __name__ == "__main__":
    run_report()
