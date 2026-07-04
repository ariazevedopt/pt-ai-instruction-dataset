# Tech Stack — LusoSupport-PT

A concise explanation of every technical choice in this project and why it serves the goal of publishing a high-quality, saleable PT-PT instruction dataset.

---

## Language: Python 3

**Why:** The entire ML/NLP tooling ecosystem lives in Python. Pandas, HuggingFace datasets, PyArrow, and all fine-tuning libraries (Axolotl, LLaMA-Factory, Unsloth) are Python-native. No other language gets you this ecosystem.

**Version:** 3.9+ (standard macOS system Python). No newer syntax is used, so any Python ≥ 3.9 works.

---

## Primary format: JSONL

**Why:** JSONL (JSON Lines) is the lingua franca of instruction datasets. Every major fine-tuning library reads it. It's human-readable, git-diffable, and easy to validate line by line. Each row is one self-contained JSON object — exactly what `is_valid_row()` needs.

---

## Core dependencies

### `pandas` — data manipulation & CSV export
Used in `export_formats.py` to flatten nested JSON rows into tabular CSV format. Chosen because it's the standard data library, already familiar to the target audience (ML practitioners), and handles encoding correctly.

### `pyarrow` — Parquet export
Parquet is Hugging Face's **preferred storage format** for datasets. It's column-oriented, ~3-5× smaller than JSONL, and loads ~10× faster in the `datasets` library. Required for professional HF publishing.

### `datasets` (Hugging Face) — HF publishing & loading
The official library for interacting with the HF Hub. Used to:
- Push the dataset to HF with `dataset.push_to_hub()`
- Load it with `load_dataset("ariazevedopt/LusoSupport-PT")`
- Add proper metadata, tags, and splits

This is what makes the dataset work seamlessly for buyers who use the standard HF workflow.

### `tqdm` — progress bars
When generating 1,000+ rows, the pipeline runs silently without it. `tqdm` adds a real-time progress bar to the generation and validation steps in `pipeline.py`. Tiny dependency, large UX improvement — especially important when sharing the workflow publicly.

### `rich` — terminal output
Powers the styled tables in `print_stats()` and the coloured pipeline output. Makes `make stats` and `make pipeline` look professional — which matters when the terminal output is part of the product's marketing materials (README screenshots, LinkedIn posts).

### `pytest` — test suite
Covers `validate.py` and `dedupe.py` — the two functions that define dataset correctness. For a product you charge money for, having a passing test suite is table stakes for credibility. Tests live in `tests/` and run with `make test`.

---

## Output generation: template library

**Why not an LLM API?** Calling OpenAI/Anthropic at generation time adds per-run costs, requires API key management, produces non-reproducible results, and introduces a runtime dependency. For a dataset product, **reproducibility and cost control matter more than marginal output quality**.

**The approach:** `scenarios.py` provides realistic PT-PT input messages per intent. `templates.py` builds the instruction string. A `responses.py` module (in progress, see issue #21) will provide 5-10 realistic PT-PT output variants per `(task_type, intent)` combination, sampled randomly.

This is sufficient for a paid product because:
- Outputs are hand-written by a human (higher trust than generated)
- Fully reproducible — same seed = same dataset
- Zero API cost — generate 10,000 rows for free
- Linguistically controlled — every output is reviewed before being added to the template library

---

## What is intentionally excluded

| Thing | Reason excluded |
|-------|----------------|
| Web framework (Flask, FastAPI) | Not a web product — no API needed |
| Database (SQLite, Postgres) | JSONL files are the database — simpler, portable, git-trackable |
| Docker | Solo project; adds complexity without benefit at this scale |
| Type hints / mypy | Acceptable omission for a solo data pipeline at this scope |
| LLM API (OpenAI, Anthropic) | Template approach is sufficient; avoids cost and reproducibility issues |

---

## Running the full stack

```bash
# Install everything
pip install -r requirements.txt

# Verify tests pass
make test

# Generate 1,000 rows → validate → deduplicate → save
make pipeline

# Export all formats (CSV, Alpaca JSONL, Parquet)
make export

# View dataset composition
make stats
```
