# Changelog

All notable changes to **LusoSupport-PT** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses dataset-style versioning: the dataset release version is
tracked separately from tooling changes. The current dataset release is **v1.1**.

## [Unreleased] - 2026-08-28

### Changed
- **Strategic pivot:** repositioned the project around specializing [AMALIA](https://amaliallm.pt/) — Portugal's open-source, government-backed pt-PT LLM — for customer support, rather than leading with the raw dataset as the primary product. The dataset itself, its pricing, and its licensing are unchanged; only the framing and target audience shifted. Full rationale in `docs/superpowers/specs/2026-08-28-amalia-pivot-strategy.md`. Updated README, HF dataset card, Gumroad landing pages, `docs/use-cases.md`, `docs/integration.md` (added an AMALIA fine-tuning walkthrough), `docs/datasheet.md`, and `docs/launch/announcement-templates.md` accordingly. An AMALIA fine-tuning spike (producing an actual fine-tuned checkpoint) remains gated on Stage-0 buyer-outreach validation (issue #64).

## [1.1] - 2026-08-09

### Changed
- Scaled the dataset from 5,162 to 10,828 rows (issue #51, item 1a). Note: the
  final published count is 10,828, not the 10,831 figure originally quoted
  from an earlier simulation run — legitimate run-to-run variance in
  `generate.py`; all docs/product pages now reference the true 10,828 figure.
- Added `scripts/responses_expansion_v2.py`: a second wave of hand-written pt-PT
  templates (4 more per (task_type, intent) cell for email_reply,
  response_generation, faq_answer, next_action_suggestion,
  rewrite_professional, summarization) and 5 more urgency_classification
  reason variants per intent, to keep every task_type above the 40%
  unique-output diversity gate at the larger scale.
- Expanded `TONE_MESSAGES` customer-message pools in `scripts/scenarios.py`
  from ~3-4 to >=5 messages per (intent, tone) cell.
- Re-exported all formats (CSV, Alpaca JSONL, Parquet) and refreshed the
  free 200-row Hugging Face Lite sample.
- Updated Gumroad Individual (`vkjsx`) and Commercial product files/description
  to the v1.1 (10,828-row) dataset; both custom landing pages (`landing.html`,
  `landing-commercial.html`) refreshed with current stats, "Who this is built
  for" and "Integrate in minutes" sections, and republished live.
- **Privatized the content-generation modules** (`scripts/scenarios.py`,
  `templates.py`, `responses.py`, `responses_expansion.py`,
  `responses_expansion_v2.py`, and their dedicated tests): these are no
  longer distributed with the public repo and have been scrubbed from all
  git history (history rewritten and force-pushed), since they contain the
  hand-tuned pt-PT message/response content that is the dataset's actual
  commercial value. Pipeline tooling (validate, dedupe, export, quality
  report, schema) remains fully open source. See `NOTICE.md`.
- Fixed a data-exposure issue on the Hugging Face repo: the full paid
  10,828-row dataset (`processed/lusosupport_pt_v1.{jsonl,csv,parquet}`,
  `_alpaca.jsonl`) had been accidentally uploaded alongside the free sample
  and was publicly downloadable — removed, along with a stale duplicate
  `hf-lite/` sample folder; only the canonical 200-row free sample remains.

### Added
- `NOTICE.md` — clarifies that the Apache-2.0 licence covers pipeline
  tooling only, not the (private) content-generation modules or the sold
  dataset itself.
- `scripts/simulate_scale.py` — dry-run calibration tool to check the
  diversity gate before committing to a real generation run at a new scale.

## [Unreleased]

### Added
- `CHANGELOG.md` (this file) to track dataset and tooling history.
- `.github/workflows/ci.yml` — CI that runs the test suite and dataset validation on every push and pull request.
- `docs/datasheet.md` — a "Datasheet for Datasets" (Gebru et al.) describing motivation, composition, collection, and recommended uses.
- `docs/superpowers/specs/2026-08-07-project-roadmap.md` — prioritised roadmap for future versions and companion products.
- `docs/pt-pt-style-guide.md` — documents the pt-BR → pt-PT vocabulary policy: agent `output` always uses pt-PT terms; customer `input` may intentionally include pt-BR-influenced code-switching (resolves #55).
- README "Quality at a glance" section with reproducible diversity/validation metrics.
- A small set of intentional pt-BR-influenced customer message examples in `scripts/scenarios.py` (covering `celular`, `senha`, `nota fiscal`, `contato`) so the dataset demonstrates the agent responding in correct pt-PT to code-switched input.

### Changed
- **Pricing:** Individual €39 → €59 (early adopter), €79 (standard); Commercial €149 → €229 (early adopter), €329 (standard) — aligned with market research on comparable verified-quality niche instruction datasets (€185–460), adjusted down €20/tier from an initial higher proposal per user feedback. Both Gumroad listings updated live via API.
- Dataset regenerated fresh: 5,149 → 5,162 rows (includes new pt-BR-code-switch example rows).

### Fixed
- **Banned-vocabulary false positives (#55):** removed `assinatura` and `código de rastreio` from the banned pt-BR word list — both are standard European Portuguese, not pt-BR-exclusive. The list is now `celular`, `senha`, `nota fiscal`, `contato`.
- **Banned-vocabulary scope:** the banned list is now enforced only on agent `output`, never on customer `input`. Real pt-PT speakers sometimes use pt-BR-influenced vocabulary; the dataset should teach a model to understand it while always responding in correct pt-PT.
- Corrected stale row-count references (5,163 → 5,149) across README, USAGE, HF card, launch templates, and the commercial licence.
- Corrected stale test-count (54 → 113) and dependency list (`faker` → `pandas, pyarrow, datasets, tqdm, rich, pytest`) in the README.
- Corrected stale export paths (`datasets/exports/` → `datasets/processed/`) in the README and integration guide.
- Corrected the intent count (17 → 18) in the Copilot instructions.
- Removed unused imports (`generate_dataset`, `to_csv`, `to_alpaca_jsonl`) from `scripts/pipeline.py`.

## [1.0.0] — 2026-08-07 — Dataset quality overhaul

### Fixed
- **Placeholder subdomain bug:** 1,275 of 5,163 rows carried the literal string `subdomain: "placeholder"`. Every row now derives a real subdomain via `metadata.py`; 0 placeholder rows remain.
- **Seed examples never merged:** the 64 hand-crafted rows in `datasets/raw/seed_examples.jsonl` were documented as an "always included quality floor" but were not actually present in the processed dataset. `pipeline.py --fresh` now merges all 64/64.
- **Low output diversity:** unique-output ratio was 6–18% per task type. Added ~270 hand-written pt-PT templates (`scripts/responses_expansion.py`) plus a `{domain_label}` substitution retrofit. Unique-output ratio is now 42–77% across all 8 task types, enforced by a 40% gate in `scripts/quality_report.py`.

### Added
- `scripts/quality_report.py` output-diversity gate (`_check_output_diversity()`).
- Regenerated all export formats (`.csv`, `.parquet`, `_alpaca.jsonl`) and the 200-row HF Lite sample.

### Dataset
- Final processed dataset: **5,149 rows** (post-dedup), 100% passing `validate.py`.

## [0.4.0] — 2026-08-07 — Launch preparation (M4)

### Added
- Hugging Face Lite tier: 200-row free sample + dataset card (`datasets/hf-lite/`).
- Commercial and personal-use licence texts (`LICENCE-COMMERCIAL.md`, CC BY 4.0 for Lite).
- Gumroad product pages (Individual + Commercial) and pricing section in the README.
- `docs/USAGE.md` buyer quick-start guide; launch checklist, announcement templates, and metrics-tracking docs under `docs/launch/`.
- `.github/FUNDING.yml` for GitHub Sponsors.

## [0.3.0] — 2026-07-04 — Validation hardening + scale (Phase 3)

### Added
- Scaled the processed dataset past 5,000 rows.
- Hardened `validate.py` rule set and expanded the pytest suite.

## [0.2.0] — 2026-07-04 — Metadata correctness + parametric diversity (Phase 1–2)

### Added
- Parametric instruction/input/output templates.
- Tone derivation, escalation, subdomain, and confidence metadata.
- Browser-based review UI (`make review-browser`) and full quality loop (`make flag` / `make review` / `make quality`).

## [0.1.0] — 2026-05 — Foundations

### Added
- JSONL schema, folder structure, seed examples, and the initial Python generation pipeline.
- Canonical enum taxonomy (`scripts/config.py`, `docs/taxonomy.yaml`).

[Unreleased]: https://github.com/ariazevedopt/pt-ai-instruction-dataset/commits/main
