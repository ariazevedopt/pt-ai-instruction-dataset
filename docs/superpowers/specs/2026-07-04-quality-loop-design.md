# Quality Loop System — Design Spec

**Date:** 2026-07-04  
**Status:** Approved  
**Goal:** Increase dataset reliability and introduce a human-in-the-loop validation mechanism that improves output quality iteratively.

---

## Problem Statement

The current pipeline generates rows using fixed templates but lacks:
1. Sufficient input diversity (11% unique inputs across 1,096 rows)
2. Sufficient output diversity for non-classification tasks (18–45% unique)
3. A way for the maintainer to review, reject, and correct individual rows
4. Actionable quality signals to identify which templates need improvement
5. A validation layer deep enough to catch structural, vocabulary, and semantic issues

---

## Architecture

```
datasets/raw/seed_examples.jsonl   ← always included, never excluded
        │
        ▼
scripts/pipeline.py
  [1] generate (generate.py)
  [2] validate (validate.py — upgraded)
  [3] deduplicate (dedupe.py)
  [4] exclude flagged + rejected rows       ← NEW: reads from datasets/feedback/
  [5] merge with existing processed set
        │
        ▼
datasets/processed/lusosupport_pt_v1.jsonl

─────── Quality Loop (runs separately) ───────────────────────────────────────

make flag       → scripts/flag.py
                  reads processed dataset
                  runs validate.py + extra heuristics
                  writes datasets/feedback/flagged.jsonl

make review     → scripts/review.py
                  interactive terminal UI (rich)
                  presents rows one at a time (random / flagged / filtered)
                  user: [a]pprove / [r]eject / [f]ix inline / [s]kip / [q]uit
                  writes to datasets/feedback/{approved,rejected,corrections}.jsonl

make quality    → scripts/quality_report.py
                  reads feedback files
                  groups rejections by domain × task_type
                  prints rich table of weakest template areas
```

---

## Feedback Directory

```
datasets/feedback/
  flagged.jsonl       auto-flagged rows (rule violations + heuristics)
  rejected.jsonl      human-rejected rows
  approved.jsonl      human-approved rows (quality anchors)
  corrections.jsonl   inline corrections provided during review
```

Each JSONL entry schema:

```json
// flagged.jsonl
{"id": "lusosupport_pt_000234", "reason": "pt-br_vocab:assinatura", "row": {...}}

// rejected.jsonl
{"id": "lusosupport_pt_000234", "reason": "output too generic", "timestamp": "..."}

// approved.jsonl
{"id": "lusosupport_pt_000234", "timestamp": "..."}

// corrections.jsonl
{"id": "lusosupport_pt_000234", "original_output": "...", "corrected_output": "...", "timestamp": "..."}
```

**Seed protection:** Row IDs from `datasets/raw/seed_examples.jsonl` are always included in the processed dataset and cannot be excluded via feedback files. Seeds represent the highest-quality examples.

---

## Component: `validate.py` — Upgraded

Return type changes from `bool` to `(bool, str)` — `(is_valid, reason)`. Existing callers updated.

### Rule Set (15 checks)

| # | Category | Rule |
|---|---|---|
| 1 | Structure | `id` field present and non-empty |
| 2 | Structure | `language == "pt"` |
| 3 | Structure | `variant == "pt-PT"` |
| 4 | Structure | `task_type` is a valid value from `config.TASK_TYPES` |
| 5 | Structure | `domain` is a valid value from `config.DOMAINS` |
| 6 | Input | Input contains `"Mensagem do cliente:"` prefix |
| 7 | Input | Input length ≥ 15 characters |
| 8 | Output — length | `response_generation`, `email_reply`: output ≥ 80 chars |
| 9 | Output — length | `summarization`: output ≥ 40 chars |
| 10 | Output — length | `intent_classification`, `urgency_classification`: output ≥ 20 chars |
| 11 | Output — length | All other task types: output ≥ 30 chars |
| 12 | Output — stubs | Output must not contain `[sem template` or `Resposta gerada` |
| 13 | PT-PT vocabulary | Banned words: `celular`, `senha`, `nota fiscal`, `assinatura`, `código de rastreio`, `contato` (without 'c') |
| 14 | JSON integrity | For `intent_classification`: output must parse as JSON with keys `intent`, `urgency`, `domain`, `confidence`; `domain` must equal row's `domain` field |
| 15 | JSON integrity | For `urgency_classification`: output must parse as JSON with keys `urgency`, `reason`, `escalate` (or `rationale`) |

---

## Component: `flag.py` — Automated Pre-Scanner

**Input:** `datasets/processed/lusosupport_pt_v1.jsonl`  
**Output:** `datasets/feedback/flagged.jsonl`  

Runs two passes:
1. **Rule-based:** Apply all `validate.py` checks and flag any that fail
2. **Heuristic-based** (beyond validate.py):
   - Duplicate output within same domain×task_type bucket
   - Output-to-input length ratio < 0.5 for text tasks
   - Output contains only one sentence for `email_reply` or `response_generation`

Skips rows already in `approved.jsonl` (human has verified them).

Prints summary:
```
Flagged 47 rows across 6 rules:
  pt-br_vocab:assinatura        18 rows
  json_domain_mismatch           12 rows
  output_too_short               9 rows
  duplicate_in_bucket            6 rows
  single_sentence_email          2 rows
```

---

## Component: `review.py` — Interactive Human Review

**Interface:**
```
python3 review.py [--mode random|flagged|all] [--n 20] [--domain telecom] [--task email_reply]
```

**Display** (using `rich.Panel`):
```
─────────── Row 3/20 ── telecom / email_reply ── billing_question ──────────────
 INPUT
 Mensagem do cliente: "Exmos. Senhores, venho por este meio contestar..."

 OUTPUT
 Assunto: Re: Contestação da Fatura...

[a]pprove  [r]eject  [f]ix inline  [s]kip  [q]uit
```

**Actions:**
- `a` → append to `approved.jsonl`, continue
- `r` → prompt for optional reason → append to `rejected.jsonl`, continue
- `f` → open multiline prompt → append original + correction to `corrections.jsonl`, continue
- `s` → skip (no feedback written), continue
- `q` → save progress, exit (resume resumes from last unreviewed row)

**Progress tracking:** Writes a `.review_checkpoint` file with last-reviewed ID so sessions can be resumed.

---

## Component: `quality_report.py` — Template Health Report

**Input:** All feedback files  
**Output:** Rich terminal report

```
────────── LusoSupport-PT Quality Report ──────────
  1,096 total rows  |  32 flagged  |  14 rejected  |  87 approved

  Weakest areas (by rejection rate):
  ┌─────────────────────────────┬────────┬──────────┬───────────┐
  │ domain × task_type          │ Total  │ Rejected │   Rate    │
  ├─────────────────────────────┼────────┼──────────┼───────────┤
  │ telecom × urgency_classif.  │  12    │  6       │  50%  ▓▓▓ │
  │ utilities × response_gen.   │  28    │  8       │  29%  ▓▓  │
  └─────────────────────────────┴────────┴──────────┴───────────┘

  → Fix priority: responses.py templates for telecom/urgency_classification
```

---

## Pipeline Integration

`pipeline.py` step 4 (new — runs after dedup):

```python
def load_exclusion_ids(feedback_dir):
    excluded = set()
    seed_ids = load_seed_ids()  # always protected
    for fname in ["flagged.jsonl", "rejected.jsonl"]:
        path = feedback_dir / fname
        if path.exists():
            for line in path.read_text().splitlines():
                entry = json.loads(line)
                if entry["id"] not in seed_ids:
                    excluded.add(entry["id"])
    return excluded
```

Corrections from `corrections.jsonl` are injected into the processed dataset (replacing the original output with the corrected one).

---

## Makefile Targets

```makefile
flag:       cd scripts && python3 flag.py
review:     cd scripts && python3 review.py --mode flagged
quality:    cd scripts && python3 quality_report.py
```

Full loop: `make flag && make review && make pipeline`

---

## Testing

New tests in `tests/test_validate.py`:
- Each of the 15 validation rules tested in isolation (pass + fail case)
- `test_flag.py` — verify flag.py correctly identifies known-bad rows
- `test_pipeline_exclusions.py` — verify excluded IDs don't appear in output, seeds always appear

---

## Out of Scope

- Automated template updates from corrections (corrections are stored for manual review)
- Web UI for review
- Multi-user / team review workflow
- GitHub Issues integration

---

## Success Criteria

- `make flag && make review` produces measurable feedback (≥ 10 rows reviewed per session)
- After 2 review sessions, `quality_report.py` identifies at least 1 template area to improve
- Pipeline correctly excludes all rejected/flagged rows and injects all corrections
- `validate.py` catches the domain-mismatch bug class that existed before this work
- All 18 existing tests continue to pass; new tests bring coverage to ≥ 30 test cases
