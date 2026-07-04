"""End-to-end pipeline: generate → validate → deduplicate → export.

Usage:
    python pipeline.py               # default: 100 rows, saves to datasets/
    python pipeline.py --n 200
    python pipeline.py --stats       # print composition stats after run
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel

from dedupe import deduplicate
from export_formats import print_stats, to_alpaca_jsonl, to_csv
from generate import generate_row, generate_dataset, save_jsonl
from validate import is_valid_row

INTERIM_PATH = "../datasets/interim/generated.jsonl"
PROCESSED_PATH = "../datasets/processed/lusosupport_pt_v1.jsonl"

console = Console()


def run(n=100, stats=False):
    console.rule("[bold blue]LusoSupport-PT Pipeline")

    console.print(f"\n[1/4] Generating [bold]{n}[/bold] synthetic rows...")
    rows = []
    for i in tqdm(range(n), desc="  Generating", unit="row"):
        rows.append(generate_row(i))

    console.print(f"[2/4] Validating...")
    valid = [r for r in tqdm(rows, desc="  Validating", unit="row") if is_valid_row(r)]
    console.print(f"      [green]{len(valid)}/{len(rows)}[/green] rows passed validation")

    console.print(f"[3/4] Deduplicating...")
    deduped = deduplicate(valid)
    removed = len(valid) - len(deduped)
    console.print(f"      [green]{len(deduped)}[/green] unique rows "
                  f"([yellow]{removed}[/yellow] duplicates removed)")

    console.print(f"[4/4] Saving...")
    save_jsonl(deduped, INTERIM_PATH)

    existing = []
    if os.path.exists(PROCESSED_PATH):
        with open(PROCESSED_PATH, encoding="utf-8") as f:
            existing = [json.loads(line) for line in f if line.strip()]

    merged = deduplicate(existing + deduped)
    save_jsonl(merged, PROCESSED_PATH)

    console.print(Panel(
        f"[bold]Interim[/bold]   → {INTERIM_PATH} ([cyan]{len(deduped)}[/cyan] rows)\n"
        f"[bold]Processed[/bold] → {PROCESSED_PATH} ([cyan]{len(merged)}[/cyan] rows total)",
        title="✅ Done", border_style="green"
    ))

    if stats:
        print_stats(merged)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full LusoSupport-PT generation pipeline.")
    parser.add_argument("--n", type=int, default=100, help="Rows to generate (default: 100)")
    parser.add_argument("--stats", action="store_true", help="Print dataset stats after run")
    args = parser.parse_args()

    run(n=args.n, stats=args.stats)
