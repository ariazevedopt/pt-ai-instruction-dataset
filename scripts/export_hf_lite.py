"""export_hf_lite.py — Curate the free-tier HF Lite slice (~200 rows).

Sampling strategy:
  1. Prioritise rows from approved.jsonl (human-reviewed quality anchors).
  2. Fill remaining budget by sampling evenly across all (domain, task_type)
     combinations, then across all customer_intents, to ensure coverage.
  3. Reject any row whose ID appears in rejected.jsonl.

Usage:
    python3 export_hf_lite.py [--n 200] [--out ../datasets/hf-lite/lusosupport_pt_lite.jsonl]
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

PROCESSED = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
APPROVED = Path("../datasets/feedback/approved.jsonl")
REJECTED = Path("../datasets/feedback/rejected.jsonl")
DEFAULT_OUT = Path("../datasets/hf-lite/lusosupport_pt_lite.jsonl")

random.seed(42)


def load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_id_set(path: Path) -> set:
    return {r["id"] for r in load_jsonl(path)}


def curate(n: int = 200) -> list:
    rows = load_jsonl(PROCESSED)
    approved_ids = load_id_set(APPROVED)
    rejected_ids = load_id_set(REJECTED)

    eligible = [r for r in rows if r["id"] not in rejected_ids]
    by_id = {r["id"]: r for r in eligible}

    selected: list = []
    seen_ids: set = set()

    # 1 — Seed with approved rows (up to n//3 of budget)
    approved_rows = [r for r in eligible if r["id"] in approved_ids]
    random.shuffle(approved_rows)
    for r in approved_rows[: n // 3]:
        selected.append(r)
        seen_ids.add(r["id"])

    # 2 — Fill by (domain, task_type) round-robin
    bucket: dict = defaultdict(list)
    for r in eligible:
        if r["id"] not in seen_ids:
            key = (r.get("domain", ""), r.get("task_type", ""))
            bucket[key].append(r)

    for lst in bucket.values():
        random.shuffle(lst)

    keys = sorted(bucket.keys())
    i = 0
    while len(selected) < n and any(bucket[k] for k in keys):
        k = keys[i % len(keys)]
        if bucket[k]:
            r = bucket[k].pop()
            if r["id"] not in seen_ids:
                selected.append(r)
                seen_ids.add(r["id"])
        i += 1

    # 3 — Top up with intent-balanced sampling if still under budget
    intent_bucket: dict = defaultdict(list)
    for r in eligible:
        if r["id"] not in seen_ids:
            intent_bucket[r.get("customer_intent", "")].append(r)

    for lst in intent_bucket.values():
        random.shuffle(lst)

    keys2 = sorted(intent_bucket.keys())
    j = 0
    while len(selected) < n and any(intent_bucket[k] for k in keys2):
        k = keys2[j % len(keys2)]
        if intent_bucket[k]:
            r = intent_bucket[k].pop()
            if r["id"] not in seen_ids:
                selected.append(r)
                seen_ids.add(r["id"])
        j += 1

    return selected[:n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    rows = curate(args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    print(f"✓ HF Lite slice: {len(rows)} rows → {out}")

    # Coverage summary
    domains = {r.get("domain") for r in rows}
    task_types = {r.get("task_type") for r in rows}
    intents = {r.get("customer_intent") for r in rows}
    print(f"  Domains: {len(domains)}/8  Task types: {len(task_types)}/8  Intents: {len(intents)}/18")


if __name__ == "__main__":
    main()
