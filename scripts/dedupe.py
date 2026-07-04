import hashlib
import json


def _row_fingerprint(row):
    """Create a stable hash from the semantically unique parts of a row."""
    key = json.dumps({
        "instruction": row.get("instruction", ""),
        "input": row.get("input", ""),
        "output": row.get("output", ""),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def deduplicate(rows):
    """Return a list of rows with duplicates removed (first occurrence kept)."""
    seen = set()
    unique = []
    for row in rows:
        fp = _row_fingerprint(row)
        if fp not in seen:
            seen.add(fp)
            unique.append(row)
    return unique


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deduplicate a LusoSupport-PT JSONL file.")
    parser.add_argument("input", help="Input JSONL path")
    parser.add_argument("output", help="Output JSONL path")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    deduped = deduplicate(rows)
    removed = len(rows) - len(deduped)

    with open(args.output, "w", encoding="utf-8") as f:
        for row in deduped:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Input: {len(rows)} rows -> Output: {len(deduped)} rows ({removed} duplicates removed)")
