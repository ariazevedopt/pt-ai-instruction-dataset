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
from pathlib import Path

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
SEEDS_PATH = Path("../datasets/raw/seed_examples.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")

console = Console()


def load_seed_ids(seeds_path: Path = SEEDS_PATH) -> set:
    """Return the set of IDs from the seed file (always protected from exclusion)."""
    if not seeds_path.exists():
        return set()
    ids = set()
    for line in seeds_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(json.loads(line)["id"])
    return ids


def load_exclusion_ids(feedback_dir: Path = FEEDBACK_DIR,
                       seed_ids: set = None) -> set:
    """Return IDs from flagged.jsonl and rejected.jsonl, excluding seed IDs."""
    if seed_ids is None:
        seed_ids = load_seed_ids()
    excluded = set()
    for fname in ["flagged.jsonl", "rejected.jsonl"]:
        path = feedback_dir / fname
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    row_id = json.loads(line)["id"]
                    if row_id not in seed_ids:
                        excluded.add(row_id)
    return excluded


def load_corrections(feedback_dir: Path = FEEDBACK_DIR) -> dict:
    """Return a dict mapping row_id -> corrected_output from corrections.jsonl."""
    path = feedback_dir / "corrections.jsonl"
    if not path.exists():
        return {}
    corrections = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            corrections[entry["id"]] = entry["corrected_output"]
    return corrections


def run(n=100, stats=False):
    console.rule("[bold blue]LusoSupport-PT Pipeline")

    console.print(f"\n[1/4] Generating [bold]{n}[/bold] synthetic rows...")
    rows = []
    for i in tqdm(range(n), desc="  Generating", unit="row"):
        rows.append(generate_row(i))

    console.print(f"[2/5] Validating...")
    valid = [r for r in tqdm(rows, desc="  Validating", unit="row") if is_valid_row(r)[0]]
    console.print(f"      [green]{len(valid)}/{len(rows)}[/green] rows passed validation")

    console.print(f"[3/5] Deduplicating...")
    unique_rows = deduplicate(valid)
    removed = len(valid) - len(unique_rows)
    console.print(f"      [green]{len(unique_rows)}[/green] unique rows "
                  f"([yellow]{removed}[/yellow] duplicates removed)")

    console.print(f"[4/5] Applying exclusions and corrections...")
    seed_ids = load_seed_ids()
    excluded = load_exclusion_ids(seed_ids=seed_ids)
    corrections = load_corrections()
    if excluded:
        before = len(unique_rows)
        unique_rows = [r for r in unique_rows if r["id"] not in excluded]
        console.print(f"      {len(excluded)} IDs in exclusion list, {before - len(unique_rows)} rows removed")
    if corrections:
        for r in unique_rows:
            if r["id"] in corrections:
                r["output"] = corrections[r["id"]]
        console.print(f"      {len(corrections)} corrections applied")
    if not excluded and not corrections:
        console.print(f"      No exclusions or corrections to apply")

    console.print(f"[5/5] Saving...")
    save_jsonl(unique_rows, INTERIM_PATH)

    existing = []
    if os.path.exists(PROCESSED_PATH):
        with open(PROCESSED_PATH, encoding="utf-8") as f:
            existing = [json.loads(line) for line in f if line.strip()]

    merged = deduplicate(existing + unique_rows)
    save_jsonl(merged, PROCESSED_PATH)

    console.print(Panel(
        f"[bold]Interim[/bold]   → {INTERIM_PATH} ([cyan]{len(unique_rows)}[/cyan] rows)\n"
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
