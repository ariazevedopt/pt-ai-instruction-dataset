# Phase 2: Metadata Correctness — Design Spec

**Date:** 2026-07-04  
**Issue:** #45  
**Status:** Approved  

---

## Problem

Five metadata fields in the generated dataset carry values that actively contradict the training signal:

| Field | Current state | Impact |
|---|---|---|
| `customer_tone` | Randomly assigned, 0% keyword correlation with message text | Model learns conflicting tone labels |
| `requires_escalation` | Always `False` (hardcoded) | Escalation logic never trained |
| `subdomain` | Always `"placeholder"` | Taxonomy value wasted |
| `difficulty` | Randomly assigned, no content correlation | Difficulty signal is noise |
| `intent_classification.confidence` | `None` for all rows | Field not populated |

---

## Approach: Option B — New `metadata.py` module

Extract all derivation logic into `scripts/metadata.py`. Each function is pure, independently testable, and called by `generate_row()` in `generate.py`. `scenarios.py` is restructured to a nested `TONE_MESSAGES[intent][tone]` dict so messages are selected *from* tone, not labeled after selection.

---

## Architecture

```
generate.py
  └─ calls metadata.py:
       ├─ derive_customer_tone(intent) → str
       ├─ pick_message(intent, tone) → str
       ├─ derive_subdomain(intent, domain) → str
       ├─ derive_escalation(intent, tone) → bool
       ├─ derive_difficulty(intent) → str
       └─ derive_confidence(difficulty) → float
```

```
scenarios.py  ← restructured: TONE_MESSAGES[intent][tone] = list[str]
metadata.py   ← new module: derivation functions + lookup tables
generate.py   ← ~8-line change: imports + wires new functions
tests/test_metadata.py        ← new
tests/test_scenarios_tones.py ← new (or extended test_templates.py)
tests/test_generate.py        ← 3 new invariant tests added
```

---

## Module: `scripts/metadata.py`

### Lookup Tables

```python
# Intent → 2-3 plausible subdomains (within its natural domain)
INTENT_SUBDOMAINS: dict[str, list[str]] = {
    "refund_request":      ["returns_refunds", "payment_confirmation", "invoice_request"],
    "return_request":      ["returns_refunds", "exchange_request", "damaged_item"],
    "order_status":        ["order_status", "delivery_delay"],
    "delivery_delay":      ["delivery_delay", "order_status"],
    "damaged_item":        ["damaged_item", "returns_refunds", "exchange_request"],
    "billing_question":    ["billing_question", "invoice_request", "duplicate_charge"],
    "invoice_request":     ["invoice_request", "billing_question"],
    "cancel_subscription": ["cancel_subscription", "change_plan"],
    "change_plan":         ["change_plan", "cancel_subscription", "renewal_question"],
    "technical_issue":     ["bug_report", "feature_question", "account_access"],
    "password_reset":      ["password_reset", "account_access"],
    "account_access":      ["account_access", "password_reset"],
    "complaint":           ["complaint", "invoice_clarification", "account_update"],
    "escalation_request":  ["complaint", "seller_buyer_dispute", "account_update"],
    "booking_change":      ["booking_change", "cancellation"],
    "booking_cancellation":["cancellation", "refund_status"],
    "payment_failure":     ["payment_failure", "billing_question", "duplicate_charge"],
    "duplicate_charge":    ["duplicate_charge", "payment_confirmation", "invoice_request"],
}

# Intent → inherent difficulty
INTENT_DIFFICULTY: dict[str, str] = {
    "order_status":        "easy",
    "invoice_request":     "easy",
    "password_reset":      "easy",
    "delivery_delay":      "easy",
    "booking_change":      "easy",
    "return_request":      "medium",
    "damaged_item":        "medium",
    "cancel_subscription": "medium",
    "change_plan":         "medium",
    "billing_question":    "medium",
    "account_access":      "medium",
    "booking_cancellation":"medium",
    "refund_request":      "hard",
    "technical_issue":     "hard",
    "complaint":           "hard",
    "escalation_request":  "hard",
    "payment_failure":     "hard",
    "duplicate_charge":    "hard",
}

# Intents that directly require escalation
ESCALATION_INTENTS: set[str] = {"escalation_request", "complaint"}

# Tones that trigger escalation (regardless of intent)
ESCALATION_TONES: set[str] = {"frustrated", "urgent"}

# Confidence calibrated to difficulty
CONFIDENCE_RANGES: dict[str, tuple[float, float]] = {
    "easy":   (0.90, 0.99),
    "medium": (0.78, 0.92),
    "hard":   (0.62, 0.82),
}
```

### Functions

```python
def derive_customer_tone(intent: str) -> str:
    """Pick a random tone from the tones available for this intent in TONE_MESSAGES."""
    from scenarios import TONE_MESSAGES
    return random.choice(list(TONE_MESSAGES[intent].keys()))

def pick_message(intent: str, tone: str) -> str:
    """Pick a random message from TONE_MESSAGES[intent][tone]."""
    from scenarios import TONE_MESSAGES
    return random.choice(TONE_MESSAGES[intent][tone])

def derive_subdomain(intent: str, domain: str) -> str:
    """Pick a random valid subdomain for this intent (2-3 options)."""
    options = INTENT_SUBDOMAINS.get(intent, [domain])
    return random.choice(options)

def derive_escalation(intent: str, tone: str) -> bool:
    """True if intent is escalation/complaint OR tone is frustrated/urgent."""
    return intent in ESCALATION_INTENTS or tone in ESCALATION_TONES

def derive_difficulty(intent: str) -> str:
    """Return difficulty level from intent lookup table."""
    return INTENT_DIFFICULTY.get(intent, "medium")

def derive_confidence(difficulty: str) -> float:
    """Return a confidence score calibrated to difficulty."""
    lo, hi = CONFIDENCE_RANGES[difficulty]
    return round(random.uniform(lo, hi), 4)
```

---

## Module: `scripts/scenarios.py` — Restructured

`INTENT_MESSAGES` (flat `dict[str, list[str]]`) → `TONE_MESSAGES` (nested `dict[str, dict[str, list[str]]]`).

All 18 intents × 6 tones = 108 pools, each with 3-5 PT-PT messages. Total message count ≥ 324 (vs 228 today).

Existing callers of `INTENT_MESSAGES[intent]` in `generate.py` are replaced by `pick_message(intent, tone)` from `metadata.py`.

`INTENT_DOMAINS` dict remains unchanged.

---

## Module: `scripts/generate.py` — Changes

| Before | After |
|---|---|
| `customer_tone = random.choice(CUSTOMER_TONES)` | `customer_tone = derive_customer_tone(intent)` |
| `message = random.choice(INTENT_MESSAGES[intent])` | (moved after tone derivation) `message = pick_message(intent, customer_tone)` |
| `"subdomain": "placeholder"` | `"subdomain": derive_subdomain(intent, domain)` |
| `"difficulty": random.choice(DIFFICULTY_LEVELS)` | `"difficulty": derive_difficulty(intent)` |
| `"requires_escalation": False` | `"requires_escalation": derive_escalation(intent, customer_tone)` |
| no `intent_classification` field | `"intent_classification": {"intent": intent, "confidence": derive_confidence(difficulty)}` |

Import line added: `from metadata import derive_customer_tone, pick_message, derive_subdomain, derive_escalation, derive_difficulty, derive_confidence`

---

## Testing

### `tests/test_metadata.py` (new)
- `derive_escalation("escalation_request", "calm")` → `True`
- `derive_escalation("complaint", "formal")` → `True`
- `derive_escalation("order_status", "calm")` → `False`
- `derive_escalation("order_status", "frustrated")` → `True`
- `derive_difficulty("escalation_request")` → `"hard"`
- `derive_difficulty("order_status")` → `"easy"`
- `derive_confidence("easy")` always in `[0.90, 0.99]` (50 samples)
- `derive_confidence("hard")` always in `[0.62, 0.82]` (50 samples)
- `derive_subdomain("account_access", "saas")` always in `["account_access", "password_reset"]`
- All 18 intents have entries in `INTENT_DIFFICULTY` and `INTENT_SUBDOMAINS`

### `tests/test_scenarios_tones.py` (new)
- All 18 intents present in `TONE_MESSAGES`
- All 6 tones present for every intent
- Every pool has ≥ 3 messages
- No pool contains banned pt-BR words
- `pick_message(intent, tone)` returns a string for all 18×6 combinations

### `tests/test_generate.py` — 3 new invariants
- Generate 100 rows: `customer_tone` always one of the 6 valid tones
- Generate 100 rows: all `escalation_request` rows have `requires_escalation == True`
- Generate 100 rows: all `intent_classification.confidence` values are floats in `[0.62, 0.99]`

### Backward compatibility
- Existing 71 tests must continue to pass
- `INTENT_MESSAGES` can be kept as an alias for flat access (`{k: [m for pool in v.values() for m in pool] for k,v in TONE_MESSAGES.items()}`) to avoid breaking any direct references

---

## Scope Boundaries

**In scope:**
- `scripts/metadata.py` (new)
- `scripts/scenarios.py` (restructured)
- `scripts/generate.py` (~8 lines changed)
- Tests: `test_metadata.py`, `test_scenarios_tones.py`, 3 new invariants in `test_generate.py`

**Out of scope (Phase 3):**
- `validate.py` enum checks
- Banned-word check on `input` field
- `booking_cancellation` in taxonomy.yaml / config.py alignment
- Scaling to 5000+ rows

---

## Success Criteria

After Phase 2:
1. Zero rows with `subdomain == "placeholder"`
2. Zero rows with `requires_escalation == None` or hardcoded `False` for `escalation_request` intent
3. `customer_tone` correlated 100% with message text (derived from tone pool)
4. `difficulty` correlated with intent complexity map
5. `intent_classification.confidence` populated for all rows, calibrated to difficulty
6. All existing 71 tests still pass; new tests bring total to ~95+
