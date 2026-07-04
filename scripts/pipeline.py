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

from dedupe import deduplicate
from export_formats import print_stats, to_alpaca_jsonl, to_csv
from generate import generate_dataset, save_jsonl
from validate import is_valid_row

INTERIM_PATH = "../datasets/interim/generated.jsonl"
PROCESSED_PATH = "../datasets/processed/lusosupport_pt_v1.jsonl"


def run(n=100, stats=False):
    print(f"[1/4] Generating {n} synthetic rows...")
    rows = generate_dataset(n)

    print(f"[2/4] Validating...")
    valid = [r for r in rows if is_valid_row(r)]
    print(f"      {len(valid)}/{len(rows)} rows passed validation")

    print(f"[3/4] Deduplicating...")
    deduped = deduplicate(valid)
    print(f"      {len(deduped)} unique rows ({len(valid) - len(deduped)} duplicates removed)")

    print(f"[4/4] Saving...")
    save_jsonl(deduped, INTERIM_PATH)

    # Merge with existing processed rows (seed + generated), then dedupe again
    existing = []
    if os.path.exists(PROCESSED_PATH):
        with open(PROCESSED_PATH, encoding="utf-8") as f:
            existing = [json.loads(line) for line in f if line.strip()]

    merged = deduplicate(existing + deduped)
    save_jsonl(merged, PROCESSED_PATH)
    print(f"      Interim  → {INTERIM_PATH} ({len(deduped)} rows)")
    print(f"      Processed → {PROCESSED_PATH} ({len(merged)} rows total)")

    if stats:
        print_stats(merged)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full LusoSupport-PT generation pipeline.")
    parser.add_argument("--n", type=int, default=100, help="Rows to generate (default: 100)")
    parser.add_argument("--stats", action="store_true", help="Print dataset stats after run")
    args = parser.parse_args()

    run(n=args.n, stats=args.stats)
