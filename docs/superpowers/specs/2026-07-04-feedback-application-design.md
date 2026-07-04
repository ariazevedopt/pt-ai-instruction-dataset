# Feedback Application — Design Spec

**Date:** 2026-07-04  
**Status:** Approved  
**Goal:** Apply human review feedback from the browser UI to (1) clean the dataset, and (2) improve response generation templates to eliminate presumptuous outputs.

---

## Problem Statement

After running the browser review UI, the following feedback was collected:

| File | Count | Status |
|---|---|---|
| `approved.jsonl` | 51 | Quality anchors — no action needed |
| `rejected.jsonl` | 2 | Must be removed from processed dataset |
| `browser_ratings.jsonl` | 13 | 9 are false positives (classification tasks); 3 are actionable; 1 is smoke test |
| `flagged.jsonl` | 29 | Pre-existing flags — not in scope for this change |

**Root template issue:** `response_generation` templates jump to conclusions (assume account is blocked, assume wrong intent, assume recovery email arrived) instead of asking clarifying questions when the customer's exact situation is ambiguous.

---

## Scope

Three parts, executed in this order:

1. **Feedback cleanup** — mark false-positive "unclear" ratings as dismissed
2. **Dataset cleanup + re-generation** — remove 2 rejected rows, replace with 2 fresh rows built from improved templates
3. **Template improvements** — add cautious/clarifying variants to 3 `response_generation` intents in `responses.py`

Out of scope: `flagged.jsonl` processing, `corrections.jsonl`, changes to `summarization` templates, changes to classification task templates (they are correct).

---

## Part 1 — Feedback Cleanup

### What and Why

9 entries in `browser_ratings.jsonl` were marked "unclear" because the reviewer misread classification task outputs as bad response formats. These entries are factually wrong — `intent_classification` and `urgency_classification` outputs are supposed to be JSON. Acting on these would incorrectly exclude valid rows.

### Change

Add `"dismissed": true` and `"dismiss_reason": "classification_task_correct"` to each of the 9 affected entries. No deletions — entries stay for audit trail. Any future pipeline or report step filters on `dismissed != true`.

**Affected IDs:**
```
lusosupport_pt_000107   (intent_classification)
lusosupport_pt_000242   (urgency_classification)
lusosupport_pt_001165   (intent_classification)
lusosupport_pt_000164   (intent_classification)
lusosupport_pt_000115   (urgency_classification)
lusosupport_pt_001402   (urgency_classification)
lusosupport_pt_000970   (intent_classification)
lusosupport_pt_000513   (urgency_classification)
lusosupport_pt_000412   (intent_classification)
```

The remaining 3 non-dismissed, non-smoke entries stay as actionable signals:
- `lusosupport_pt_000390` — summarization output looks like internal note (informational; summarization behavior is correct but worth monitoring)
- `lusosupport_pt_001745` — response_generation assumes too much for damaged_item
- `lusosupport_pt_001003` — response_generation assumes account is blocked for account_access

---

## Part 2 — Dataset Cleanup and Re-generation

### Step 1 — Remove rejected rows

Remove 2 rows from `datasets/processed/lusosupport_pt_v1.jsonl`:

| ID | Rejection reason |
|---|---|
| `lusosupport_pt_000266` | Misidentified intent (`change_plan` vs. clarification request) |
| `lusosupport_pt_001685` | Response ignored actual problem (missing recovery email); jumped to wrong solution |

Result: 1275 → 1273 rows.

### Step 2 — Re-generate 2 replacement rows

After Part 3 (template improvements) is applied, run:
```bash
cd scripts && python3 generate.py --n 2
```

Then validate, dedupe, and append to the processed dataset → back to 1275 rows.

The newly generated rows will use the improved templates, so the rejected patterns will not recur for those intents.

---

## Part 3 — Template Improvements (`responses.py`)

### Principle

`response_generation` templates must include **at least one cautious variant** per intent — one that asks the customer for more details before asserting a solution. This mirrors real support agent behaviour: when the exact problem is unclear, ask first.

Existing templates are **kept** (they remain as action-oriented variants for cases where the situation is clear). New variants are **added**.

### Changes by Intent

#### `account_access`

**Current issue:** All variants assume the account is blocked and proceed to unlock/verify.  
**Fix:** Add 2 variants that ask for clarification first:

```
"Para melhor compreender a situação, pode descrever o que acontece quando tenta aceder à sua conta? Recebe alguma mensagem de erro específica?"

"Antes de prosseguirmos, precisamos de perceber em que passo está a encontrar dificuldade. Está a tentar aceder pelo site, aplicação, ou outro canal?"
```

#### `password_reset`

**Current issue:** All variants assume the recovery email arrived in the inbox.  
**Fix:** Add 2 variants that confirm the registered email and suggest checking spam:

```
"Para auxiliar com a recuperação da palavra-passe, pode confirmar o endereço de e-mail associado à conta? Por vezes, o e-mail de recuperação pode chegar à pasta de spam ou lixo."

"Verificou a pasta de spam ou de lixo do seu e-mail? O e-mail de recuperação pode ter sido filtrado. Se confirmar o endereço registado, podemos reenviar."
```

#### `change_plan`

**Current issue:** Some variants immediately process a plan change instead of first presenting options.  
**Fix:** Add 2 variants that offer plan information before acting:

```
"Posso ajudá-lo a explorar as opções de plano disponíveis. Qual é a sua principal prioridade — reduzir o custo mensal, aumentar o armazenamento, ou adicionar utilizadores?"

"Antes de efectuarmos qualquer alteração, gostaria de apresentar as opções actuais para que possa escolher o plano mais adequado. Qual é a sua necessidade principal?"
```

### Verification

After adding the variants, run:
```bash
make test
```

All 54 existing tests should still pass. No new tests are strictly required for template content (they are prose, not logic), but a quick sanity check via `make stats` after re-generation is recommended.

---

## Execution Order

```
1. Patch browser_ratings.jsonl  (dismiss 9 false-positive entries)
2. Update responses.py          (add 6 new template variants)
3. Remove 2 rejected IDs        (filter lusosupport_pt_v1.jsonl in-place)
4. Run generate.py --n 2        (replace with fresh rows using new templates)
5. Validate + dedupe + append   (keep dataset at 1275 rows)
6. Run make test                (verify nothing broken)
7. Commit all changes
```

---

## Files Changed

| File | Change |
|---|---|
| `datasets/feedback/browser_ratings.jsonl` | Add `dismissed`/`dismiss_reason` to 9 entries |
| `scripts/responses.py` | Add 6 new template strings across 3 intents |
| `datasets/processed/lusosupport_pt_v1.jsonl` | Remove 2 rejected rows, append 2 regenerated rows |
