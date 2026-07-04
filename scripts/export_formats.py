"""Export helpers for LusoSupport-PT dataset."""
import json

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


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
    console.print(f"  [green]✓[/green] CSV  → {path} ({len(df)} rows)")


def to_parquet(rows, path):
    """Export rows to Parquet format (preferred by Hugging Face datasets).

    Parquet is column-oriented, smaller than JSONL, and loads faster in
    the HF datasets library.
    """
    flat = []
    for row in rows:
        flat_row = {k: v for k, v in row.items() if k != "metadata"}
        meta = row.get("metadata", {})
        flat_row.update({f"meta_{k}": v for k, v in meta.items()})
        flat.append(flat_row)
    df = pd.DataFrame(flat)
    df.to_parquet(path, index=False)
    console.print(f"  [green]✓[/green] Parquet → {path} ({len(df)} rows)")


def to_alpaca_jsonl(rows, path):
    """Export rows in Alpaca instruction format (instruction / input / output).

    Compatible with Axolotl, LLaMA-Factory, Unsloth, and most fine-tuning
    frameworks that accept the Alpaca instruction format.
    """
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            alpaca_row = {
                "instruction": row.get("instruction", ""),
                "input": row.get("input", ""),
                "output": row.get("output", ""),
            }
            f.write(json.dumps(alpaca_row, ensure_ascii=False) + "\n")
    console.print(f"  [green]✓[/green] Alpaca → {path} ({len(rows)} rows)")


def print_stats(rows):
    """Print a rich table summary of dataset composition."""
    if not rows:
        console.print("[yellow]No rows.[/yellow]")
        return

    from collections import Counter
    console.rule(f"[bold]LusoSupport-PT — {len(rows)} rows[/bold]")

    for field in ("domain", "task_type", "customer_intent", "difficulty", "channel"):
        counts = Counter(r.get(field, "?") for r in rows)
        table = Table(title=field, show_header=True, header_style="bold cyan", min_width=50)
        table.add_column("Value", style="white")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Bar", style="green")
        for val, n in sorted(counts.items(), key=lambda x: -x[1]):
            table.add_row(val, str(n), "█" * n)
        console.print(table)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export LusoSupport-PT dataset to other formats.")
    parser.add_argument("input", help="Input JSONL path")
    parser.add_argument("--csv", help="Output CSV path")
    parser.add_argument("--parquet", help="Output Parquet path")
    parser.add_argument("--alpaca", help="Output Alpaca JSONL path")
    parser.add_argument("--stats", action="store_true", help="Print dataset statistics")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    if args.csv:
        to_csv(rows, args.csv)
    if args.parquet:
        to_parquet(rows, args.parquet)
    if args.alpaca:
        to_alpaca_jsonl(rows, args.alpaca)
    if args.stats:
        print_stats(rows)
