"""simulate_scale.py — dry-run a pipeline.py accumulation to check the
diversity gate BEFORE committing to a real generation run. Does not write
to datasets/processed/ — everything happens in memory / a temp file.

Usage:
    cd scripts && python3 simulate_scale.py --n 5700
"""
import argparse
import json
import random
from collections import defaultdict

from generate import generate_row
from dedupe import deduplicate

PROCESSED_PATH = "../datasets/processed/lusosupport_pt_v1.jsonl"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5700)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    random.seed(args.seed)

    with open(PROCESSED_PATH, encoding="utf-8") as f:
        existing = [json.loads(line) for line in f if line.strip()]
    start_id = max(int(r["id"].split("_")[-1]) for r in existing) + 1

    new_rows = [generate_row(start_id + i) for i in range(args.n)]
    new_unique = deduplicate(new_rows)
    merged = deduplicate(existing + new_unique)

    print(f"Existing: {len(existing)} | New batch (post self-dedupe): {len(new_unique)} "
          f"| Final merged total: {len(merged)}")

    by_task = defaultdict(list)
    for r in merged:
        by_task[r["task_type"]].append(r["output"])

    print("\nOutput diversity by task_type (simulated):")
    all_ok = True
    for tt, outs in sorted(by_task.items()):
        uniq = len(set(outs))
        ratio = uniq / len(outs) * 100
        status = "OK" if ratio >= 40 else "FAIL"
        if ratio < 40:
            all_ok = False
        print(f"  {tt:25s} rows={len(outs):5d} unique={uniq:5d} ratio={ratio:5.1f}% {status}")

    if not all_ok:
        raise SystemExit("Simulation shows at least one task_type below the 40% diversity gate.")
    print("\nAll task_types pass the 40% diversity gate in simulation.")


if __name__ == "__main__":
    main()
