# Design Spec: Phase 1 — Parametric Template Diversity

**Date:** 2026-07-04  
**Status:** Approved  
**GitHub issue:** #44  
**Scope:** `templates.py`, `scenarios.py`, `responses.py`, `generate.py`, `tests/`

---

## Problem

The dataset has an effective repetition ceiling that limits fine-tuning quality:

| Metric | Current | Target |
|---|---|---|
| Unique instructions | 12 / 1275 rows | ~800+ |
| Unique input messages | 79 unique (max 24× repeats) | ~270 |
| Repeated output values | 315 distinct values appear 2+ times | <50 |

Root cause: `agent_tone`, `domain`, and `channel` are generated for every row but never used to shape instruction or output content. Templates are static strings, not parametric.

---

## Design

### Core principle

Replace static string selection with **parametric templates**: base strings containing `{domain_label}`, `{agent_tone}`, `{channel}` placeholders that are filled at generation time by `generate_row()`. 

The row schema does not change. No new fields. All existing validation rules continue to apply.

---

### 1. `templates.py` — parametric instructions

**Replace** the single-dispatch `build_instruction()` function with a template-pool approach.

```python
# New structure
DOMAIN_LABELS: dict[str, str]         # enum → pt-PT label
CHANNEL_LABELS: dict[str, str]        # enum → pt-PT label  
AGENT_TONE_LABELS: dict[str, str]     # enum → pt-PT adjective
INSTRUCTION_TEMPLATES: dict[str, list[str]]  # task_type → list of parametric templates

def build_instruction(task_type: str, agent_tone: str, domain: str, channel: str) -> str
```

**Content targets per task_type:**

| task_type | Base templates | Variables used |
|---|---|---|
| `response_generation` | 7 | tone, domain_label, channel |
| `email_reply` | 6 | tone, domain_label |
| `summarization` | 5 | domain_label, channel |
| `intent_classification` | 5 | domain_label |
| `urgency_classification` | 5 | domain_label |
| `rewrite_professional` | 5 | channel |
| `next_action_suggestion` | 6 | domain_label, tone |
| `faq_answer` | 5 | domain_label |

**Example templates (`response_generation`):**
```python
"Responde ao cliente em português de Portugal, com tom {agent_tone}.",
"Elabora uma resposta de suporte em pt-PT para uma questão de {domain_label}. Tom: {agent_tone}.",
"Como agente de {domain_label}, redige uma resposta {agent_tone} ao cliente pelo {channel}.",
"Responde a esta mensagem com um registo {agent_tone}. Contexto: {domain_label}.",
"Escreve uma resposta em português europeu, adequada ao canal {channel}, com tom {agent_tone}.",
```

**`build_instruction()` implementation:**
1. Pick a random template from `INSTRUCTION_TEMPLATES[task_type]`
2. Fill `{domain_label}`, `{agent_tone}`, `{channel}` via `.format()`
3. Return filled string — no unfilled `{...}` placeholders allowed

---

### 2. `scenarios.py` — expanded message pool

**Expand** `INTENT_MESSAGES` from 3-5 entries per intent to **12-15 entries**, covering:
- Short terse messages ("A encomenda não chegou.")
- Longer, detailed messages with context
- Formal register (business context)
- Emotionally charged phrasing (frustrated, urgent)
- Questions vs. statements

No structural change — same `dict[str, list[str]]` shape. `generate_row()` still uses `random.choice(INTENT_MESSAGES[intent])`.

Target: **~270 unique inputs** (18 intents × 15 messages) vs. 79 today.

---

### 3. `responses.py` — parametric outputs

**Extend** `get_output()` signature:

```python
def get_output(task_type: str, intent: str, domain: str = None, agent_tone: str = None) -> str
```

Add two new maps:

```python
DOMAIN_LABELS: dict[str, str]    # imported from templates.py (single source of truth)
TONE_PHRASES: dict[str, dict]    # tone → {opener, closer, style_note}
```

**Template variable injection:** Non-classification templates gain `{domain_label}` where natural:
```python
# Before
"Compreendemos a sua questão relativamente ao valor faturado."
# After  
"Compreendemos a sua questão de {domain_label} relativamente ao valor faturado."
```

**Tone-aware phrasing:** `TONE_PHRASES` drives opener/closer variation:
```python
TONE_PHRASES = {
    "empathetic": {"opener": "Lamentamos sinceramente a situação descrita.", ...},
    "concise":    {"opener": "Recebemos o seu pedido.", ...},
    "formal":     {"opener": "Acusamos a recepção da sua comunicação.", ...},
    ...
}
```

Templates for `response_generation`, `email_reply`, and `next_action_suggestion` inject tone-aware openers. Classification tasks (`intent_classification`, `urgency_classification`) are not affected — their outputs are structured JSON, not prose.

**Target:** each `(task_type, intent)` key has 6-10 templates using domain/tone variables → ~1200+ unique output combinations.

---

### 4. `generate.py` — wire up parameters

```python
# Before
"instruction": build_instruction(task, agent_tone),
"output": generate_output(task, intent, domain=domain),

# After
"instruction": build_instruction(task, agent_tone, domain, channel),
"output": generate_output(task, intent, domain=domain, agent_tone=agent_tone),
```

No other changes to `generate_row()`.

---

### 5. Tests

Three new tests in `tests/test_generate.py` (new file):

1. **No unfilled placeholders:** generate 200 rows; assert no field contains `{` or `}` characters
2. **Instruction diversity:** generate 200 rows; assert `len(set(r["instruction"] for r in rows)) >= 50`
3. **Domain in output:** for non-classification rows, assert `domain_label` term appears in output at least 30% of the time across 200 rows

All 54 existing tests must continue to pass.

---

## Sequence diagram

```
generate_row(i)
  │
  ├─ domain, channel, agent_tone, intent = (random choices)
  │
  ├─ build_instruction(task, agent_tone, domain, channel)
  │     └─ pick template → fill {vars} → return string
  │
  ├─ random.choice(INTENT_MESSAGES[intent])   ← expanded pool
  │
  └─ get_output(task, intent, domain, agent_tone)
        ├─ classification tasks: structured JSON (unchanged)
        └─ prose tasks: pick template → fill {domain_label}, {tone_phrase} → return string
```

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Template variable not filled → `{domain_label}` appears in output | New test asserts no `{`/`}` in any field |
| Domain label sounds unnatural in some templates | Review all (task_type, domain) combinations before commit; prefer generic phrasing where specific is awkward |
| Tone phrase feels forced in short outputs | Apply tone opener only to `email_reply` and longer `response_generation` templates; keep short templates plain |
| Existing tests break due to signature change | `build_instruction()` and `get_output()` new params default to `None` — backward compatible |

---

## Out of scope (Phase 2)

- Deriving `customer_tone` from message content
- Computing `requires_escalation` from intent + tone
- Real `subdomain` assignment
- `difficulty` derivation
- `confidence` calibration by difficulty

---

## Acceptance criteria

- [ ] All 54 existing tests pass
- [ ] New test: no `{...}` placeholders in any generated field
- [ ] New test: unique instruction count ≥ 50 across 200 generated rows
- [ ] New test: domain label present in outputs (≥30% of prose rows)
- [ ] `make pipeline --n 500` runs clean, `make validate` passes
- [ ] `make stats` shows task_type distribution still within 8-25% per type
