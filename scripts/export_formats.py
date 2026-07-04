"""Export helpers for LusoSupport-PT dataset."""
import json

import pandas as pd


def to_csv(rows, path):
    """Export rows to a flat CSV file."""
    flat = []
    for row in rows:
        flat_row = {k: v for k, v in row.items() if k != "metadata"}
        meta = row.get("metadata", {})
        flat_row.update({f"meta_{k}": v for k, v in meta.items()})
        flat.append(flat_row)
    df = pd.DataFrame(flat)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Exported {len(df)} rows to {path}")


def to_alpaca_jsonl(rows, path):
    """Export rows in Alpaca instruction format (instruction / input / output).

    This is a widely-used format for LLM fine-tuning with libraries such as
    Axolotl, LLaMA-Factory, and Unsloth.
    """
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            alpaca_row = {
                "instruction": row.get("instruction", ""),
                "input": row.get("input", ""),
                "output": row.get("output", ""),
            }
            f.write(json.dumps(alpaca_row, ensure_ascii=False) + "\n")
    print(f"Exported {len(rows)} rows to {path} (Alpaca format)")


def print_stats(rows):
    """Print a quick summary of dataset composition."""
    from collections import Counter

    if not rows:
        print("No rows.")
        return

    print(f"\n=== LusoSupport-PT dataset stats ({len(rows)} rows) ===")
    for field in ("domain", "task_type", "customer_intent", "difficulty", "channel"):
        counts = Counter(r.get(field, "?") for r in rows)
        print(f"\n{field}:")
        for val, n in sorted(counts.items(), key=lambda x: -x[1]):
            bar = "█" * n
            print(f"  {val:<30} {n:>3}  {bar}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export LusoSupport-PT dataset to other formats.")
    parser.add_argument("input", help="Input JSONL path")
    parser.add_argument("--csv", help="Output CSV path")
    parser.add_argument("--alpaca", help="Output Alpaca JSONL path")
    parser.add_argument("--stats", action="store_true", help="Print dataset statistics")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    if args.csv:
        to_csv(rows, args.csv)
    if args.alpaca:
        to_alpaca_jsonl(rows, args.alpaca)
    if args.stats:
        print_stats(rows)
