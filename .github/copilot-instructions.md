# LusoSupport-PT — Copilot Instructions

## Project Overview

This is a **European Portuguese (pt-PT) customer support instruction dataset** for LLM fine-tuning, prompting experiments, and support automation. All generated content must be in **pt-PT only** — never mix in pt-BR.

---

## Running Scripts

Use `make` from the repo root for all common tasks:

```bash
pip install -r requirements.txt   # pandas, pyarrow, datasets, tqdm, rich, pytest

make test        # run pytest suite (validate + dedupe coverage)
make pipeline    # generate → validate → deduplicate → save (tqdm progress + rich output)
make stats       # rich table breakdown of dataset composition
make export      # CSV + Alpaca JSONL + Parquet
make validate    # validate processed dataset
make dedupe      # deduplicate processed dataset in-place
make clean       # remove generated export files
```

Or run individual scripts from `scripts/`:

```bash
cd scripts
python3 generate.py --n 100     # generate rows → ../datasets/interim/
python3 pipeline.py --n 500 --stats
python3 dedupe.py <input> <output>
python3 export_formats.py <input> --csv out.csv --alpaca out.jsonl --parquet out.parquet
```

---

## Architecture

```
scripts/        # dataset generation and processing pipeline
  config.py          # single source of truth for all enum values
  scenarios.py       # INTENT_MESSAGES: customer intent → PT-PT sample messages (17 intents)
  templates.py       # build_instruction(task_type, agent_tone) → instruction strings
  generate.py        # generate_row(), generate_dataset(n), save_jsonl()
  validate.py        # is_valid_row() — enforces language, structure, PT-PT vocabulary
  dedupe.py          # SHA-256 fingerprint deduplication on instruction+input+output
  export_formats.py  # to_csv(), to_parquet(), to_alpaca_jsonl(), print_stats() [rich]
  pipeline.py        # end-to-end runner with tqdm + rich output

datasets/
  raw/           # hand-crafted seed examples (seed_examples.jsonl)
  interim/       # script-generated drafts (generated.jsonl)
  processed/     # release-ready: .jsonl, .csv, _alpaca.jsonl, .parquet

docs/
  schema.md           # full JSON schema documentation
  taxonomy.yaml       # authoritative enum definitions
  examples.md         # annotated example rows
  tech-stack.md       # tech choices and rationale
  superpowers/specs/  # design specs and business plan

tests/
  test_validate.py    # pytest coverage for is_valid_row()
  test_dedupe.py      # pytest coverage for deduplicate()
```

Data flows: `raw` → `interim` → `processed`.

---

## Key Conventions

### Language
- All `instruction`, `input`, and `output` fields must be in **pt-PT**.
- Banned words in outputs: `celular`, `senha`, `nota fiscal` (these are pt-BR terms — `validate.py` enforces this).
- Use pt-PT equivalents: `palavra-passe` (not `senha`), `telemóvel` (not `celular`), `fatura` (not `nota fiscal`), `encomenda` for orders.

### Row Structure
- IDs follow the pattern `lusosupport_pt_000001` (zero-padded to 6 digits).
- Every row must have `"language": "pt"` and `"variant": "pt-PT"`.
- `metadata.synthetic` is always `true` for generated rows; `metadata.source_type` is `"template_generated"` (scripts) or `"manual_seed"` (hand-written).
- No real PII; no regulated advice (medical, legal, tax, investment).

### Validation rules (`validate.py`)
- `id` must be present
- `language` must be `"pt"`, `variant` must be `"pt-PT"`
- `output` must be ≥ 10 characters
- `output` must not contain any banned pt-BR words

### config.py is the canonical enum source
Add new domains, task types, intents, tones, channels, or difficulty levels to `config.py` first, then update `docs/taxonomy.yaml` to keep them in sync.

### Content safety
Do not generate rows containing: real personal data, regulated professional advice, company-specific policies stated as facts, abusive content, or content requiring specialist certification.
