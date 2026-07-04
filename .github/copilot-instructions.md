# LusoSupport-PT — Copilot Instructions

## Project Overview

This is a **European Portuguese (pt-PT) customer support instruction dataset** for LLM fine-tuning, prompting experiments, and support automation. All generated content must be in **pt-PT only** — never mix in pt-BR.

---

## Running Scripts

Scripts live in `scripts/` and are run from that directory:

```bash
cd scripts
python generate.py     # generate synthetic JSONL rows → ../datasets/interim/
python validate.py     # validate a dataset file
python dedupe.py       # deduplicate rows
```

Install dependencies first:
```bash
pip install -r requirements.txt
```

---

## Architecture

```
scripts/        # dataset generation and processing pipeline
  config.py     # single source of truth for all enum values (domains, task_types, intents, tones, channels, difficulty)
  scenarios.py  # INTENT_MESSAGES dict: customer intent → sample pt-PT messages
  templates.py  # build_instruction(task_type, agent_tone) → instruction strings
  generate.py   # generate_row(), generate_dataset(n), save_jsonl()
  validate.py   # is_valid_row() — validation rules applied before saving
  dedupe.py     # deduplication (stub)
  export_formats.py  # export helpers (stub)

datasets/
  raw/           # hand-crafted seed examples (seed_examples.jsonl)
  interim/       # script-generated drafts (generated.jsonl)
  processed/     # cleaned, validated, release-ready (lusosupport_pt_v1.jsonl)

docs/
  schema.md      # full JSON schema documentation
  taxonomy.yaml  # authoritative list of domains, subdomains, task_types, intents, tones, channels
  examples.md    # annotated example rows
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
