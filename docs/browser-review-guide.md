# Browser Review Guide

The browser review UI lets you rate dataset rows as **Good**, **Unclear**, or **Bad** from any web browser, with no terminal interaction required.

## Starting the server

```bash
make review-browser
```

This opens `http://localhost:8765` in your default browser. Stop it with **Ctrl-C** in the terminal.

## Browse tab

Shows one dataset row at a time — the instruction, the customer input, and the agent output.

| Button | Meaning | Saved to |
|--------|---------|----------|
| ✅ Good | Output is correct PT-PT, on-topic, well-formed | `datasets/feedback/approved.jsonl` |
| ❓ Unclear | Borderline or ambiguous — needs more thought | `datasets/feedback/browser_ratings.jsonl` |
| ❌ Bad | Wrong domain/intent, bad PT-PT, stub, or hallucinated output (comment required) | `datasets/feedback/rejected.jsonl` |
| Skip → | Move to next row without rating | nothing |

**Flagged Only mode** — shows only the rows that `make flag` identified as problematic.

## Generate & Test tab

Type a customer message in Portuguese, choose a domain, task type, and intent, then click **Generate** to see what the system would output. Rate the result the same way as the Browse tab.

Generated rows get a `browser_generated_<timestamp>` ID and are saved to `browser_ratings.jsonl`.

## Feeding ratings back into the pipeline

After a review session:

```bash
# Refresh the flag list (approved rows are excluded)
make flag

# Rebuild the processed dataset (rejected rows are excluded)
make pipeline

# Check the updated quality report
make quality
```

## Exporting ratings

Click the **⬇ Export** button in the header to download `browser_ratings.jsonl` — this contains all Unclear ratings with the full row data.

## Ports

To use a different port:

```bash
python3 scripts/review_server.py --port 9000 --open
```
