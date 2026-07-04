# Phase 2: Metadata Correctness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix five metadata fields (`customer_tone`, `requires_escalation`, `subdomain`, `difficulty`, `intent_classification.confidence`) that are currently random/hardcoded and actively contradict the training signal.

**Architecture:** A new `scripts/metadata.py` module owns all derivation logic as pure functions. `scripts/scenarios.py` is restructured from a flat `INTENT_MESSAGES[intent]` dict to a nested `TONE_MESSAGES[intent][tone]` dict so messages are selected *from* the correct tone pool. `generate.py` wires both modules together with ~8-line changes.

**Tech Stack:** Python 3.9+, pytest, existing scripts/ import conventions (`sys.path.insert(0, "scripts/")`).

## Global Constraints

- All message content must be European Portuguese (pt-PT) only — no pt-BR
- Banned words forbidden in all string literals: `celular`, `senha`, `nota fiscal`, `assinatura`, `código de rastreio`, `contato`
- Use pt-PT vocabulary: `palavra-passe`, `telemóvel`, `fatura`, `encomenda`, `contacto`, `actualização`, `subscrição`
- Row schema: no new top-level fields except `intent_classification` (already referenced in existing code); no renaming of existing fields
- `INTENT_MESSAGES` flat-dict alias must be preserved in `scenarios.py` for backward compatibility with existing tests
- All 71 existing tests must continue to pass after every task
- Run tests with: `python3 -m pytest tests/ -q` from repo root (`/Users/ariazevedo/repos/pt-ai-instruction-dataset`)
- Commit after each task with descriptive message
- Repo root: `/Users/ariazevedo/repos/pt-ai-instruction-dataset`
- Scripts import path: tests do `sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `scripts/metadata.py` | **Create** | Lookup tables + 6 pure derivation functions |
| `scripts/scenarios.py` | **Modify** | Replace flat INTENT_MESSAGES with nested TONE_MESSAGES; keep INTENT_MESSAGES alias |
| `scripts/generate.py` | **Modify** | Wire metadata functions; add intent_classification field |
| `tests/test_metadata.py` | **Create** | Unit tests for all metadata derivation functions |
| `tests/test_scenarios_tones.py` | **Create** | Coverage tests: all 18 intents × 6 tones populated, PT-PT only |
| `tests/test_generate.py` | **Modify** | Add 3 new integration invariant tests |

---

## Task 1: Create `scripts/metadata.py` with lookup tables and derivation functions

**Files:**
- Create: `scripts/metadata.py`
- Create: `tests/test_metadata.py`

**Interfaces:**
- Consumes: `scripts/scenarios.py:TONE_MESSAGES` (lazy import inside functions — Task 2 provides this)
- Produces:
  - `derive_customer_tone(intent: str) -> str`
  - `pick_message(intent: str, tone: str) -> str`
  - `derive_subdomain(intent: str, domain: str) -> str`
  - `derive_escalation(intent: str, tone: str) -> bool`
  - `derive_difficulty(intent: str) -> str`
  - `derive_confidence(difficulty: str) -> float`
  - `INTENT_SUBDOMAINS: dict[str, list[str]]`
  - `INTENT_DIFFICULTY: dict[str, str]`
  - `CONFIDENCE_RANGES: dict[str, tuple[float, float]]`

- [ ] **Step 1: Write failing tests for `metadata.py`**

Create `tests/test_metadata.py`:

```python
import os
import sys
import random
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import metadata as M


# --- derive_escalation ---

def test_escalation_escalation_request_calm():
    assert M.derive_escalation("escalation_request", "calm") is True

def test_escalation_complaint_formal():
    assert M.derive_escalation("complaint", "formal") is True

def test_escalation_order_status_calm():
    assert M.derive_escalation("order_status", "calm") is False

def test_escalation_order_status_frustrated():
    assert M.derive_escalation("order_status", "frustrated") is True

def test_escalation_order_status_urgent():
    assert M.derive_escalation("order_status", "urgent") is True


# --- derive_difficulty ---

def test_difficulty_escalation_request_is_hard():
    assert M.derive_difficulty("escalation_request") == "hard"

def test_difficulty_order_status_is_easy():
    assert M.derive_difficulty("order_status") == "easy"

def test_difficulty_return_request_is_medium():
    assert M.derive_difficulty("return_request") == "medium"

def test_difficulty_unknown_intent_defaults_medium():
    assert M.derive_difficulty("nonexistent_intent") == "medium"

def test_difficulty_all_18_intents_covered():
    intents = [
        "refund_request", "return_request", "order_status", "delivery_delay",
        "damaged_item", "billing_question", "invoice_request", "cancel_subscription",
        "change_plan", "technical_issue", "password_reset", "account_access",
        "complaint", "escalation_request", "booking_change", "booking_cancellation",
        "payment_failure", "duplicate_charge",
    ]
    for intent in intents:
        result = M.derive_difficulty(intent)
        assert result in ("easy", "medium", "hard"), f"{intent} → {result!r}"


# --- derive_confidence ---

def test_confidence_easy_in_range():
    random.seed(99)
    for _ in range(50):
        c = M.derive_confidence("easy")
        assert 0.90 <= c <= 0.99, f"easy confidence out of range: {c}"

def test_confidence_medium_in_range():
    random.seed(99)
    for _ in range(50):
        c = M.derive_confidence("medium")
        assert 0.78 <= c <= 0.92, f"medium confidence out of range: {c}"

def test_confidence_hard_in_range():
    random.seed(99)
    for _ in range(50):
        c = M.derive_confidence("hard")
        assert 0.62 <= c <= 0.82, f"hard confidence out of range: {c}"

def test_confidence_is_float():
    assert isinstance(M.derive_confidence("easy"), float)

def test_confidence_rounded_to_4dp():
    random.seed(42)
    c = M.derive_confidence("medium")
    assert c == round(c, 4)


# --- derive_subdomain ---

def test_subdomain_account_access_valid():
    random.seed(0)
    valid = {"account_access", "password_reset"}
    for _ in range(20):
        result = M.derive_subdomain("account_access", "saas")
        assert result in valid, f"unexpected subdomain: {result}"

def test_subdomain_all_18_intents_covered():
    intents = [
        "refund_request", "return_request", "order_status", "delivery_delay",
        "damaged_item", "billing_question", "invoice_request", "cancel_subscription",
        "change_plan", "technical_issue", "password_reset", "account_access",
        "complaint", "escalation_request", "booking_change", "booking_cancellation",
        "payment_failure", "duplicate_charge",
    ]
    for intent in intents:
        result = M.derive_subdomain(intent, "ecommerce")
        assert isinstance(result, str) and len(result) > 0, f"{intent} returned empty subdomain"

def test_subdomain_fallback_for_unknown_intent():
    result = M.derive_subdomain("unknown_intent", "saas")
    assert result == "saas"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_metadata.py -q 2>&1 | head -10
```

Expected: `ModuleNotFoundError: No module named 'metadata'`

- [ ] **Step 3: Create `scripts/metadata.py`**

```python
"""
metadata.py — derivation functions for LusoSupport-PT metadata fields.

All functions are pure (no side effects) and use lazy imports from
scenarios.py to avoid circular dependencies.
"""
import random

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

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

ESCALATION_INTENTS: set[str] = {"escalation_request", "complaint"}
ESCALATION_TONES: set[str] = {"frustrated", "urgent"}

CONFIDENCE_RANGES: dict[str, tuple[float, float]] = {
    "easy":   (0.90, 0.99),
    "medium": (0.78, 0.92),
    "hard":   (0.62, 0.82),
}

# ---------------------------------------------------------------------------
# Derivation functions
# ---------------------------------------------------------------------------

def derive_customer_tone(intent: str) -> str:
    """Pick a random tone from the tones available for this intent."""
    from scenarios import TONE_MESSAGES
    return random.choice(list(TONE_MESSAGES[intent].keys()))


def pick_message(intent: str, tone: str) -> str:
    """Pick a random PT-PT message from the correct tone pool for this intent."""
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
    """Return difficulty level from intent lookup table. Defaults to 'medium'."""
    return INTENT_DIFFICULTY.get(intent, "medium")


def derive_confidence(difficulty: str) -> float:
    """Return a confidence score calibrated to difficulty, rounded to 4 dp."""
    lo, hi = CONFIDENCE_RANGES[difficulty]
    return round(random.uniform(lo, hi), 4)
```

- [ ] **Step 4: Run tests — expect most to pass, `derive_customer_tone`/`pick_message` will fail until Task 2**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_metadata.py -q
```

Expected: all tests in `test_metadata.py` pass (none of them call `derive_customer_tone` or `pick_message` — those are tested in Task 3). Also run full suite:

```bash
python3 -m pytest tests/ -q
```

Expected: 71 + new test_metadata tests all pass (the 2 functions that import TONE_MESSAGES are not called yet).

- [ ] **Step 5: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/metadata.py tests/test_metadata.py
git commit -m "feat(metadata): add metadata.py derivation functions and unit tests (issue #45)"
```

---

## Task 2: Restructure `scenarios.py` — TONE_MESSAGES nested dict

**Files:**
- Modify: `scripts/scenarios.py`
- Create: `tests/test_scenarios_tones.py`

**Interfaces:**
- Consumes: nothing new
- Produces:
  - `TONE_MESSAGES: dict[str, dict[str, list[str]]]` — 18 intents × 6 tones × ≥3 PT-PT messages each
  - `INTENT_MESSAGES: dict[str, list[str]]` — backward-compat alias (flat union of all tone pools per intent)
  - `INTENT_DOMAINS: dict[str, list[str]]` — unchanged

**Important:** `INTENT_MESSAGES` must remain exported (used by existing tests). Implement it as a computed alias at the bottom of the file:
```python
INTENT_MESSAGES = {
    intent: [msg for pool in tones.values() for msg in pool]
    for intent, tones in TONE_MESSAGES.items()
}
```

The 6 tones are: `calm`, `confused`, `frustrated`, `urgent`, `formal`, `informal`.

Each message pool must have **at least 3** PT-PT messages that clearly reflect the labeled tone.

- [ ] **Step 1: Write failing tests for TONE_MESSAGES coverage**

Create `tests/test_scenarios_tones.py`:

```python
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from scenarios import TONE_MESSAGES, INTENT_MESSAGES, INTENT_DOMAINS

TONES = ["calm", "confused", "frustrated", "urgent", "formal", "informal"]
INTENTS = [
    "refund_request", "return_request", "order_status", "delivery_delay",
    "damaged_item", "billing_question", "invoice_request", "cancel_subscription",
    "change_plan", "technical_issue", "password_reset", "account_access",
    "complaint", "escalation_request", "booking_change", "booking_cancellation",
    "payment_failure", "duplicate_charge",
]
BANNED = ["celular", "senha", "nota fiscal", "assinatura", "código de rastreio", "contato"]


def test_tone_messages_has_all_18_intents():
    for intent in INTENTS:
        assert intent in TONE_MESSAGES, f"Missing intent: {intent}"


def test_tone_messages_has_all_6_tones_per_intent():
    for intent in INTENTS:
        for tone in TONES:
            assert tone in TONE_MESSAGES[intent], f"Missing tone {tone!r} for intent {intent!r}"


def test_tone_messages_minimum_3_messages_per_pool():
    for intent in INTENTS:
        for tone in TONES:
            pool = TONE_MESSAGES[intent][tone]
            assert len(pool) >= 3, f"{intent}/{tone} has only {len(pool)} message(s)"


def test_tone_messages_no_banned_words():
    for intent in INTENTS:
        for tone in TONES:
            for msg in TONE_MESSAGES[intent][tone]:
                for banned in BANNED:
                    assert banned not in msg.lower(), (
                        f"Banned word {banned!r} in {intent}/{tone}: {msg!r}"
                    )


def test_intent_messages_alias_is_flat_union():
    for intent in INTENTS:
        flat = INTENT_MESSAGES[intent]
        all_msgs = [m for pool in TONE_MESSAGES[intent].values() for m in pool]
        assert set(flat) == set(all_msgs), f"INTENT_MESSAGES alias mismatch for {intent!r}"


def test_intent_messages_alias_has_all_intents():
    for intent in INTENTS:
        assert intent in INTENT_MESSAGES


def test_intent_domains_unchanged():
    for intent in INTENTS:
        assert intent in INTENT_DOMAINS, f"INTENT_DOMAINS missing {intent!r}"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_scenarios_tones.py -q 2>&1 | head -5
```

Expected: `AttributeError: module 'scenarios' has no attribute 'TONE_MESSAGES'`

- [ ] **Step 3: Restructure `scripts/scenarios.py`**

Replace the entire `INTENT_MESSAGES` dict with `TONE_MESSAGES` (keep `INTENT_DOMAINS` intact at the top). Then add the `INTENT_MESSAGES` alias at the bottom.

The full `TONE_MESSAGES` dict below contains all 18 intents × 6 tones. Each pool has 3-5 PT-PT messages clearly reflecting the tone:

```python
TONE_MESSAGES: dict[str, dict[str, list[str]]] = {
    "refund_request": {
        "calm": [
            "Gostaria de solicitar o reembolso relativo à minha encomenda.",
            "Seria possível processar o reembolso do valor pago?",
            "Venho solicitar, de forma cordial, a devolução do montante pago.",
            "Gostaria de saber como proceder para obter o reembolso da encomenda.",
        ],
        "confused": [
            "Não percebo bem como funciona o processo de reembolso — podem ajudar-me?",
            "Fiz uma devolução mas não sei se o reembolso já foi processado.",
            "Não sei se tenho direito ao reembolso — alguém me pode explicar?",
            "Recebi uma mensagem sobre o reembolso mas não entendi o que fazer a seguir.",
        ],
        "frustrated": [
            "Já pedi o reembolso há semanas e ainda não recebi nada — isto é inaceitável!",
            "Exijo o reembolso imediato — não vou continuar a esperar por uma resposta.",
            "Já contactei o apoio três vezes e o reembolso continua por resolver. Vergonha!",
            "O produto chegou com defeito e ainda estou à espera do dinheiro de volta. Absurdo!",
        ],
        "urgent": [
            "Preciso do reembolso com urgência — o valor é significativo para mim.",
            "É urgente que processem o reembolso hoje, caso contrário terei de escalar.",
            "Necessito que o reembolso seja efectuado imediatamente, por favor.",
            "Aguardo o reembolso com urgência — já passaram os prazos acordados.",
        ],
        "formal": [
            "Venho por este meio solicitar formalmente o reembolso referente à encomenda n.º [X].",
            "Requeiro a devolução do montante cobrado indevidamente, ao abrigo dos direitos do consumidor.",
            "Em cumprimento da legislação aplicável, solicito o reembolso no prazo legal previsto.",
        ],
        "informal": [
            "Olá, queria pedir o reembolso da encomenda, ok?",
            "Oi, podem devolver o dinheiro da compra que fiz?",
            "Tá, preciso do reembolso — como faço isso?",
            "Oi, devolvi o artigo e quero o dinheiro de volta, pode ser?",
        ],
    },
    "return_request": {
        "calm": [
            "Gostaria de devolver o produto que recebi — como devo proceder?",
            "Seria possível iniciar uma devolução para a encomenda recente?",
            "Quero devolver o artigo e gostaria de conhecer o processo.",
            "Podem indicar-me os passos para efectuar a devolução, por favor?",
        ],
        "confused": [
            "Não sei bem como funciona a política de devoluções — podem explicar?",
            "Tentei perceber como devolver o artigo mas não encontrei a informação.",
            "Não estou a perceber se posso devolver — qual é o prazo?",
            "Tenho dúvidas sobre se o artigo é elegível para devolução.",
        ],
        "frustrated": [
            "O produto não corresponde ao que encomendei e quero devolvê-lo já!",
            "Já tentei devolver este artigo duas vezes sem sucesso — é inaceitável.",
            "A qualidade é péssima e exijo poder devolver sem complicações.",
            "Fui enganado com a descrição do produto e quero a devolução imediata.",
        ],
        "urgent": [
            "Preciso de devolver o produto urgentemente — está dentro do prazo?",
            "O prazo de devolução termina amanhã — precisam de processar isto hoje.",
            "Necessito de devolver com urgência antes que o prazo expire.",
        ],
        "formal": [
            "Solicito formalmente a devolução do produto, ao abrigo da garantia legal de conformidade.",
            "Venho requerer a devolução do artigo adquirido, por não estar em conformidade com o descrito.",
            "Requeiro a activação do processo de devolução no prazo regulamentar.",
        ],
        "informal": [
            "Olá, quero devolver este produto — como faço?",
            "Oi, não gostei do artigo e quero devolvê-lo.",
            "Tá, o produto chegou errado — posso devolver?",
        ],
    },
    "order_status": {
        "calm": [
            "Gostaria de saber qual é o estado actual da minha encomenda.",
            "Podem informar-me sobre a situação da encomenda que efectuei?",
            "Gostaria de consultar o estado de entrega da minha encomenda.",
        ],
        "confused": [
            "Não estou a perceber onde está a minha encomenda — alguém me pode ajudar?",
            "Recebi um e-mail de confirmação mas não sei o que aconteceu a seguir.",
            "Não encontrei o número de rastreamento — como posso saber onde está?",
            "A aplicação mostra estados diferentes — qual é o correcto?",
        ],
        "frustrated": [
            "A minha encomenda deveria ter chegado há dias e não há qualquer actualização!",
            "Ninguém me informa sobre a encomenda — isto é um serviço péssimo.",
            "Já passaram duas semanas e ainda não sei onde está o meu pedido.",
        ],
        "urgent": [
            "Preciso urgentemente de saber se a encomenda chega hoje.",
            "É urgente — preciso da encomenda para amanhã cedo.",
            "Necessito confirmar o estado de entrega com urgência.",
        ],
        "formal": [
            "Solicito informação sobre o estado actual da encomenda efectuada.",
            "Venho solicitar a confirmação do estado de processamento da minha encomenda.",
            "Requeiro uma actualização formal sobre o ponto de situação da entrega.",
        ],
        "informal": [
            "Olá, onde está a minha encomenda?",
            "Oi, já fiz o pedido há uns dias — quando chega?",
            "Tá, queria saber quando chega a minha encomenda.",
        ],
    },
    "delivery_delay": {
        "calm": [
            "A minha encomenda ainda não chegou — podem verificar o que se passa?",
            "O prazo de entrega já passou — podem ajudar-me a perceber a situação?",
            "Gostaria de perceber o motivo do atraso na entrega, por favor.",
        ],
        "confused": [
            "O tracking mostra 'em trânsito' há vários dias — é normal?",
            "Não percebo porque é que a encomenda está atrasada.",
            "O prazo indicado já passou mas não recebi nenhuma comunicação.",
        ],
        "frustrated": [
            "O equipamento que encomendei devia ter chegado esta semana e ainda nada!",
            "Já estou à espera há demasiado tempo — este atraso é inadmissível.",
            "Ninguém me avisou do atraso e eu precisava urgentemente do produto.",
        ],
        "urgent": [
            "Preciso da encomenda com urgência — o atraso está a causar problemas sérios.",
            "É urgente que me informem quando chegará — tenho um compromisso amanhã.",
            "O atraso na entrega está a prejudicar o meu trabalho — precisam de resolver já.",
        ],
        "formal": [
            "Verifico que a entrega não foi efectuada no prazo contratualmente acordado.",
            "Solicito esclarecimentos formais sobre o atraso na entrega da encomenda.",
            "Venho exigir uma justificação para o incumprimento do prazo de entrega.",
        ],
        "informal": [
            "Olá, a encomenda ainda não chegou — o que se passa?",
            "Oi, deveria ter recebido ontem mas ainda nada.",
            "Tá atrasado — quando chega mesmo?",
        ],
    },
    "damaged_item": {
        "calm": [
            "Recebi um produto danificado e gostaria de saber como proceder.",
            "O artigo chegou com danos — podem ajudar-me com a resolução?",
            "A embalagem estava em mau estado e o produto veio danificado.",
        ],
        "confused": [
            "Não sei se devo fotografar o dano antes de contactar o apoio.",
            "O produto chegou partido — não sei se devo devolver ou pedir substituição.",
            "Tenho dúvidas sobre como reportar o artigo danificado.",
        ],
        "frustrated": [
            "A embalagem estava completamente destruída e o produto está inutilizável!",
            "Paguei muito dinheiro por este produto e chegou todo partido — vergonha!",
            "Já é a segunda vez que recebo um artigo danificado. É inaceitável!",
        ],
        "urgent": [
            "Preciso urgentemente de uma substituição — o produto danificado era essencial.",
            "O artigo danificado afecta o meu trabalho — preciso de solução imediata.",
            "Necessito de substituição urgente do produto danificado.",
        ],
        "formal": [
            "Venho comunicar que o produto recebido apresenta danos visíveis não imputáveis ao transporte.",
            "Solicito a substituição do produto danificado ao abrigo da garantia de conformidade.",
            "Requeiro a resolução formal da situação relativa ao artigo recebido com defeito.",
        ],
        "informal": [
            "Olá, o produto chegou partido — o que faço?",
            "Oi, recebi o artigo todo danificado.",
            "Tá, chegou partido mesmo — podem trocar?",
        ],
    },
    "billing_question": {
        "calm": [
            "Gostaria de esclarecer uma dúvida sobre o valor cobrado na última fatura.",
            "Podem explicar-me a composição da fatura deste mês?",
            "Tenho uma questão sobre a fatura — seria possível clarificá-la?",
        ],
        "confused": [
            "Não percebo um item na fatura — podem explicar o que representa?",
            "O montante cobrado não corresponde ao que esperava — como é calculado?",
            "Há um valor na fatura que não reconheço — o que é?",
        ],
        "frustrated": [
            "O montante debitado não corresponde ao que foi acordado — exijo explicações!",
            "Já é a terceira fatura com erros — isto é inaceitável!",
            "Continuam a cobrar valores incorrectos e ninguém resolve.",
        ],
        "urgent": [
            "Preciso de esclarecer urgentemente a cobrança — o débito automático é amanhã.",
            "É urgente verificar a fatura — tenho de pagar hoje.",
            "Necessito de confirmação urgente sobre o valor a pagar.",
        ],
        "formal": [
            "Venho solicitar esclarecimentos formais sobre os valores constantes da fatura.",
            "Solicito a rectificação da fatura referente ao período indicado.",
            "Requeiro informação detalhada sobre a composição da facturação.",
        ],
        "informal": [
            "Olá, não percebo a fatura — podem ajudar?",
            "Oi, tenho uma dúvida sobre o que me cobraram.",
            "Tá, há um valor esquisito na fatura.",
        ],
    },
    "invoice_request": {
        "calm": [
            "Gostaria de solicitar a fatura referente à compra efectuada.",
            "Podem enviar-me a fatura do serviço contratado?",
            "Necessito da fatura para efeitos de contabilidade.",
        ],
        "confused": [
            "Não recebi a fatura por e-mail — onde a posso encontrar?",
            "Não sei como solicitar a segunda via da fatura.",
            "Não estou a perceber onde estão as minhas faturas no portal.",
        ],
        "frustrated": [
            "Já pedi a fatura várias vezes e nunca a recebo — é impossível!",
            "Preciso da fatura há semanas e ninguém me envia — inaceitável.",
            "Sem fatura não consigo processar o reembolso fiscal — resolvam isto.",
        ],
        "urgent": [
            "Preciso da fatura urgentemente para entrega até ao fim do dia.",
            "É urgente — o prazo fiscal termina hoje e ainda não tenho a fatura.",
            "Necessito da fatura com carácter de urgência.",
        ],
        "formal": [
            "Venho solicitar a emissão da fatura referente ao serviço prestado.",
            "Requeiro a segunda via da fatura para efeitos de declaração fiscal.",
            "Solicito formalmente o envio da factura correspondente à encomenda.",
        ],
        "informal": [
            "Olá, podem mandar-me a fatura?",
            "Oi, preciso da fatura para a contabilidade.",
            "Tá, cadê a fatura do mês passado?",
        ],
    },
    "cancel_subscription": {
        "calm": [
            "Gostaria de cancelar a minha subscrição — podem indicar-me o processo?",
            "Desejo cancelar o plano actual — como devo proceder?",
            "Quero terminar a subscrição — podem ajudar-me?",
        ],
        "confused": [
            "Não estou a perceber como cancelar a subscrição na aplicação.",
            "Tentei cancelar mas continua a cobrar — o cancelamento foi efectuado?",
            "Não sei se o cancelamento afecta o serviço imediatamente.",
        ],
        "frustrated": [
            "Já tentei cancelar três vezes e o sistema não deixa — isto é ridículo!",
            "Continuam a cobrar depois de eu ter cancelado — exijo resolução.",
            "O cancelamento devia ser simples mas puseram obstáculos a tudo.",
        ],
        "urgent": [
            "Preciso de cancelar com urgência antes da próxima cobrança.",
            "O débito é amanhã — cancelem a subscrição hoje, por favor.",
            "Necessito de cancelamento imediato para evitar nova cobrança.",
        ],
        "formal": [
            "Venho formalizar o cancelamento da subscrição activa na minha conta.",
            "Solicito o término imediato do contrato de subscrição.",
            "Requeiro o cancelamento do plano subscrito, com efeitos imediatos.",
        ],
        "informal": [
            "Olá, quero cancelar a subscrição — como faço?",
            "Oi, não quero continuar — como cancelo?",
            "Tá, quero sair do plano.",
        ],
    },
    "change_plan": {
        "calm": [
            "Gostaria de mudar para um plano diferente — quais são as opções?",
            "Podem informar-me sobre como alterar o meu plano actual?",
            "Tenho interesse em fazer upgrade do plano — como proceder?",
        ],
        "confused": [
            "Não sei qual é o plano mais adequado para as minhas necessidades.",
            "Podem explicar as diferenças entre os planos disponíveis?",
            "Não entendo bem o que inclui cada plano — podem ajudar?",
        ],
        "frustrated": [
            "Já tentei mudar o plano mas o sistema não deixa — é uma confusão.",
            "Cada vez que peço a mudança de plano há um problema diferente.",
            "A mudança de plano deveria ser simples mas está a ser um pesadelo.",
        ],
        "urgent": [
            "Preciso de mudar de plano urgentemente — o actual não cobre as minhas necessidades.",
            "É urgente fazer o upgrade antes do fim do ciclo de facturação.",
            "Necessito da mudança de plano hoje para não perder acesso.",
        ],
        "formal": [
            "Solicito a alteração do plano actual para o plano superior disponível.",
            "Venho requerer a modificação do plano de serviço subscrito.",
            "Requeiro a transição para um plano com as funcionalidades adequadas às minhas necessidades.",
        ],
        "informal": [
            "Olá, quero mudar de plano — como faço?",
            "Oi, quero fazer upgrade do plano.",
            "Tá, preciso de um plano maior.",
        ],
    },
    "technical_issue": {
        "calm": [
            "Estou a ter um problema técnico com o serviço — podem ajudar-me?",
            "O serviço apresenta um comportamento inesperado — podem verificar?",
            "Gostaria de reportar uma anomalia técnica que encontrei.",
        ],
        "confused": [
            "Não sei se o problema é do meu lado ou do sistema — podem verificar?",
            "Aparece uma mensagem de erro mas não percebo o que significa.",
            "O serviço às vezes funciona e às vezes não — não sei o que se passa.",
        ],
        "frustrated": [
            "O serviço apresenta erros e não consigo completar as minhas tarefas — inaceitável!",
            "Já reportei este problema há uma semana e continua sem resolução.",
            "A aplicação está constantemente a falhar e perco trabalho por isso.",
        ],
        "urgent": [
            "É urgente — o sistema está em baixo e está a afectar operações críticas.",
            "Preciso de resolução imediata — o problema está a impedir o trabalho.",
            "Necessito de apoio técnico urgente — o serviço está inacessível.",
        ],
        "formal": [
            "Venho reportar uma falha técnica que impede a utilização normal do serviço.",
            "Solicito a análise e resolução do problema técnico identificado.",
            "Requeiro intervenção técnica urgente para resolver a anomalia detectada.",
        ],
        "informal": [
            "Olá, o sistema está a dar erro — podem ver?",
            "Oi, a aplicação não funciona bem.",
            "Tá com bug — precisam de arranjar.",
        ],
    },
    "password_reset": {
        "calm": [
            "Não consigo repor a palavra-passe — podem ajudar-me?",
            "Gostaria de redefinir a minha palavra-passe — como procedo?",
            "Preciso de alterar a palavra-passe e não consigo fazê-lo sozinho.",
        ],
        "confused": [
            "Não estou a receber o e-mail de reposição de palavra-passe.",
            "Não sei como alterar a palavra-passe na nova versão da aplicação.",
            "Tentei repor a palavra-passe mas diz que o link expirou.",
        ],
        "frustrated": [
            "Já pedi a reposição de palavra-passe cinco vezes e nunca recebo o e-mail!",
            "O sistema não me deixa repor a palavra-passe — é completamente absurdo.",
            "Estou bloqueado da conta por causa da palavra-passe há horas — inaceitável.",
        ],
        "urgent": [
            "Preciso de repor a palavra-passe urgentemente — tenho uma reunião daqui a pouco.",
            "É urgente — estou bloqueado da conta e preciso de aceder já.",
            "Necessito de resolução imediata para a reposição de palavra-passe.",
        ],
        "formal": [
            "Solicito o reset da palavra-passe da minha conta de forma segura.",
            "Venho requerer o procedimento formal de reposição de credenciais de acesso.",
            "Requeiro assistência para a redefinição da palavra-passe associada à conta.",
        ],
        "informal": [
            "Olá, esqueci a palavra-passe — como recupero?",
            "Oi, não consigo entrar — preciso de nova palavra-passe.",
            "Tá, preciso de repor a palavra-passe.",
        ],
    },
    "account_access": {
        "calm": [
            "Estou com dificuldades em aceder à minha conta — podem ajudar?",
            "Não consigo entrar na minha conta — podem verificar a situação?",
            "Gostaria de recuperar o acesso à minha conta, por favor.",
        ],
        "confused": [
            "Não percebo porque é que não consigo entrar na conta.",
            "A minha conta parece estar bloqueada mas não sei porquê.",
            "Já introduzi as credenciais correctas mas continua a dar erro.",
        ],
        "frustrated": [
            "A minha conta foi bloqueada sem aviso prévio — é completamente inaceitável!",
            "Perdi o acesso à conta e ninguém me ajuda a recuperar — que serviço péssimo.",
            "Já tentei entrar várias vezes e continuo bloqueado — exijo resolução imediata.",
        ],
        "urgent": [
            "Preciso de aceder à conta com urgência — tenho informação crítica lá dentro.",
            "É urgente — estou sem acesso à conta e isso está a bloquear o meu trabalho.",
            "Necessito de acesso imediato à conta — a situação é crítica.",
        ],
        "formal": [
            "Solicito o restabelecimento do acesso à minha conta de forma segura.",
            "Venho requerer a desbloqueio formal da conta de utilizador.",
            "Requeiro a verificação e reactivação da minha conta.",
        ],
        "informal": [
            "Olá, não consigo entrar na conta — ajudem-me?",
            "Oi, a minha conta está bloqueada.",
            "Tá, perdi o acesso — o que faço?",
        ],
    },
    "complaint": {
        "calm": [
            "Gostaria de registar uma reclamação relativamente ao serviço prestado.",
            "Tenho uma reclamação formal a apresentar — como procedo?",
            "Quero registar a minha insatisfação de forma construtiva.",
        ],
        "confused": [
            "Não sei qual é o processo correcto para apresentar uma reclamação.",
            "Não estou certo se devo reclamar aqui ou noutro canal.",
            "Tentei submeter a reclamação mas não sei se foi registada.",
        ],
        "frustrated": [
            "Quero apresentar uma queixa formal — o serviço que recebi foi inaceitável.",
            "Estou extremamente insatisfeito e exijo uma resposta escrita à minha reclamação.",
            "Já apresentei a reclamação e não recebi qualquer resposta — vou escalar.",
        ],
        "urgent": [
            "Preciso de registar uma reclamação urgente — o problema está a agravar-se.",
            "É urgente que a reclamação seja tratada hoje.",
            "Necessito de resolução imediata para a situação alvo de reclamação.",
        ],
        "formal": [
            "Venho por este meio apresentar reclamação formal nos termos legais aplicáveis.",
            "Requeiro o registo oficial da reclamação e resposta nos prazos legais.",
            "Solicito a abertura de processo de reclamação ao abrigo dos direitos do consumidor.",
        ],
        "informal": [
            "Olá, quero reclamar — como faço?",
            "Oi, não estou nada satisfeito com o serviço.",
            "Tá, quero queixar-me formalmente.",
        ],
    },
    "escalation_request": {
        "calm": [
            "Gostaria de escalar esta situação para um responsável, por favor.",
            "Solicito que o meu caso seja encaminhado para um nível superior de apoio.",
            "Gostaria de falar com um supervisor ou responsável da equipa.",
        ],
        "confused": [
            "Não sei a quem me devo dirigir para resolver esta situação.",
            "Já contactei o apoio básico mas não resolveram — a quem escalo?",
            "Não sei qual é o processo de escalada para situações complexas.",
        ],
        "frustrated": [
            "Exijo falar com um supervisor — o apoio de primeiro nível não resolve nada!",
            "Vou escalar esta situação se não receber resposta imediata.",
            "Já esperei demasiado — quero falar com a direcção agora.",
        ],
        "urgent": [
            "É urgente escalar — o problema está a causar prejuízos.",
            "Preciso de falar com um responsável imediatamente — a situação é crítica.",
            "Necessito de escalada urgente para resolver o problema hoje.",
        ],
        "formal": [
            "Solicito formalmente a escalada deste processo para o nível hierárquico superior.",
            "Venho requerer que o presente caso seja encaminhado para decisão superior.",
            "Requeiro o envolvimento de um responsável de nível sénior nesta situação.",
        ],
        "informal": [
            "Olá, quero falar com um supervisor.",
            "Oi, preciso de escalar este problema.",
            "Tá, quero falar com o chefe — isso não está resolvido.",
        ],
    },
    "booking_change": {
        "calm": [
            "Gostaria de alterar a data da minha reserva — é possível?",
            "Necessito de modificar os detalhes da reserva efectuada.",
            "Podem ajudar-me a alterar a minha reserva para outra data?",
        ],
        "confused": [
            "Não sei se posso alterar a reserva sem custos adicionais.",
            "Tentei alterar a reserva mas não sei se a alteração foi guardada.",
            "Não percebo quais são as condições para mudar a data.",
        ],
        "frustrated": [
            "Já tentei alterar a reserva online mas o sistema não deixa — que frustração!",
            "Paguei para mudar a reserva e ninguém confirmou a alteração.",
            "Ninguém me responde sobre a alteração da reserva — é inaceitável.",
        ],
        "urgent": [
            "Preciso de alterar a reserva urgentemente — mudei de planos.",
            "É urgente modificar a data — o check-in é amanhã.",
            "Necessito da alteração da reserva confirmada hoje.",
        ],
        "formal": [
            "Solicito a alteração da reserva para a data indicada, sem penalização.",
            "Venho requerer a modificação dos dados da reserva efectuada.",
            "Requeiro a confirmação da alteração da reserva nos termos acordados.",
        ],
        "informal": [
            "Olá, precisei de mudar a reserva — como faço?",
            "Oi, quero mudar a data da reserva.",
            "Tá, mudei de planos — podem alterar a reserva?",
        ],
    },
    "booking_cancellation": {
        "calm": [
            "Gostaria de cancelar a minha reserva — quais são as condições?",
            "Quero cancelar a reserva e saber se tenho direito a reembolso.",
            "Podem ajudar-me a cancelar a reserva efectuada?",
        ],
        "confused": [
            "Não sei se o cancelamento tem custos — podem esclarecer?",
            "Tentei cancelar a reserva mas não sei se foi efectuado.",
            "Não percebo a política de cancelamento — podem explicar?",
        ],
        "frustrated": [
            "Preciso de cancelar e não me deixam — a política é injusta!",
            "Já cancelei a reserva mas ainda não recebi o reembolso — inadmissível.",
            "O cancelamento devia ser gratuito nesta fase e estão a querer cobrar.",
        ],
        "urgent": [
            "Preciso de cancelar a reserva com urgência — emergência familiar.",
            "É urgente cancelar — o check-in é amanhã e mudei de planos.",
            "Necessito do cancelamento imediato com confirmação por escrito.",
        ],
        "formal": [
            "Venho solicitar o cancelamento da reserva ao abrigo das condições contratadas.",
            "Requeiro o cancelamento formal da reserva com reembolso integral.",
            "Solicito a rescisão da reserva, com devolução do valor pago.",
        ],
        "informal": [
            "Olá, quero cancelar a reserva — pode ser?",
            "Oi, preciso de cancelar — como faço?",
            "Tá, precisei de cancelar a reserva.",
        ],
    },
    "payment_failure": {
        "calm": [
            "Tentei efectuar o pagamento e não foi processado — podem ajudar?",
            "O pagamento falhou e não sei qual foi o motivo.",
            "Gostaria de perceber porque é que o meu pagamento não foi aceite.",
        ],
        "confused": [
            "O pagamento foi recusado mas tenho saldo suficiente — não percebo.",
            "Tentei várias vezes pagar e continua a dar erro — o que está errado?",
            "Não sei se o problema é do meu cartão ou do vosso sistema.",
        ],
        "frustrated": [
            "Tentei efectuar o pagamento várias vezes e continua a falhar — ridículo!",
            "O sistema rejeita o pagamento sem explicação — exijo que resolvam.",
            "Já perdi muito tempo a tentar pagar e nada funciona.",
        ],
        "urgent": [
            "Preciso de resolver a falha de pagamento urgentemente — o prazo é hoje.",
            "É urgente processar o pagamento — o serviço vai ser suspenso.",
            "Necessito de resolução imediata para a falha de pagamento.",
        ],
        "formal": [
            "Venho comunicar a falha no processamento do pagamento e solicitar assistência.",
            "Solicito análise da falha de pagamento e indicação de método alternativo.",
            "Requeiro esclarecimento sobre o motivo da recusa do pagamento efectuado.",
        ],
        "informal": [
            "Olá, o pagamento não passou — o que faço?",
            "Oi, tentei pagar e deu erro.",
            "Tá, o pagamento falhou — como resolvo?",
        ],
    },
    "duplicate_charge": {
        "calm": [
            "Verifiquei que fui cobrado duas vezes pelo mesmo serviço — podem verificar?",
            "Parece haver uma cobrança duplicada na minha conta — podem confirmar?",
            "Gostaria de reportar uma possível cobrança duplicada.",
        ],
        "confused": [
            "Vejo dois débitos iguais na conta mas não sei se é erro ou intencional.",
            "Não percebo porque é que aparece a mesma cobrança duas vezes.",
            "Fui cobrado duas vezes — é um erro do sistema?",
        ],
        "frustrated": [
            "Foi cobrado o mesmo valor duas vezes — exijo o reembolso imediato!",
            "Já é a segunda vez que me cobram em duplicado — isto é inaceitável.",
            "Fui duplamente debitado sem autorização — exijo explicações e devolução.",
        ],
        "urgent": [
            "É urgente anular a cobrança duplicada — o valor é significativo.",
            "Preciso de resolução urgente — a cobrança duplicada afecta o meu saldo.",
            "Necessito do reembolso da cobrança duplicada com urgência.",
        ],
        "formal": [
            "Venho comunicar a existência de uma cobrança duplicada não autorizada.",
            "Solicito a análise e rectificação da duplicação de débito verificada.",
            "Requeiro o reembolso imediato do valor cobrado indevidamente em duplicado.",
        ],
        "informal": [
            "Olá, cobrararam-me duas vezes — podem ver?",
            "Oi, há uma cobrança dupla na conta.",
            "Tá, fui cobrado duas vezes pelo mesmo.",
        ],
    },
}

# Backward-compatibility alias: flat union of all tone pools per intent.
# Existing code that uses INTENT_MESSAGES[intent] continues to work unchanged.
INTENT_MESSAGES: dict[str, list[str]] = {
    intent: [msg for pool in tones.values() for msg in pool]
    for intent, tones in TONE_MESSAGES.items()
}
```

- [ ] **Step 4: Run scenario tone tests**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_scenarios_tones.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 5: Run full suite to confirm no regressions**

```bash
python3 -m pytest tests/ -q
```

Expected: all prior tests + new tests pass (no failures).

- [ ] **Step 6: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/scenarios.py tests/test_scenarios_tones.py
git commit -m "feat(scenarios): restructure to TONE_MESSAGES nested dict — 18 intents x 6 tones (issue #45)"
```

---

## Task 3: Wire `generate.py` + add integration invariants to `test_generate.py`

**Files:**
- Modify: `scripts/generate.py`
- Modify: `tests/test_generate.py`

**Interfaces:**
- Consumes (from Task 1 `metadata.py`):
  - `derive_customer_tone(intent: str) -> str`
  - `pick_message(intent: str, tone: str) -> str`
  - `derive_subdomain(intent: str, domain: str) -> str`
  - `derive_escalation(intent: str, tone: str) -> bool`
  - `derive_difficulty(intent: str) -> str`
  - `derive_confidence(difficulty: str) -> float`
- Consumes (from Task 2 `scenarios.py`): `INTENT_DOMAINS` (already imported)
- Produces: `generate_row()` returning rows where all 5 metadata fields are derived (not random/hardcoded)

- [ ] **Step 1: Write 3 new failing tests in `tests/test_generate.py`**

Append these tests to the existing `tests/test_generate.py` file (do not remove any existing tests):

```python
# ── Phase 2: metadata correctness invariants ──────────────────────────────

def test_customer_tone_always_valid():
    """customer_tone must always be one of the 6 valid tones."""
    from config import CUSTOMER_TONES
    random.seed(77)
    rows = generate_dataset(100)
    for r in rows:
        assert r["customer_tone"] in CUSTOMER_TONES, (
            f"Invalid customer_tone: {r['customer_tone']!r}"
        )


def test_escalation_request_always_requires_escalation():
    """All escalation_request rows must have requires_escalation == True."""
    random.seed(88)
    rows = [generate_row(i) for i in range(500)]
    esc_rows = [r for r in rows if r["customer_intent"] == "escalation_request"]
    assert len(esc_rows) > 0, "No escalation_request rows generated in 500 samples"
    for r in esc_rows:
        assert r["metadata"]["requires_escalation"] is True, (
            f"escalation_request row has requires_escalation=False, tone={r['customer_tone']}"
        )


def test_intent_classification_confidence_in_range():
    """intent_classification.confidence must be a float in [0.62, 0.99] for all rows."""
    random.seed(99)
    rows = generate_dataset(100)
    for r in rows:
        ic = r.get("intent_classification")
        assert ic is not None, "Missing intent_classification field"
        c = ic.get("confidence")
        assert isinstance(c, float), f"confidence is not float: {c!r}"
        assert 0.62 <= c <= 0.99, f"confidence out of range: {c}"
        assert ic.get("intent") == r["customer_intent"], "intent_classification.intent mismatch"
```

- [ ] **Step 2: Run new tests to confirm they fail**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_generate.py::test_customer_tone_always_valid \
    tests/test_generate.py::test_escalation_request_always_requires_escalation \
    tests/test_generate.py::test_intent_classification_confidence_in_range -v
```

Expected: all 3 fail (metadata not yet wired).

- [ ] **Step 3: Update `scripts/generate.py`**

Replace the entire file with the following (all existing logic preserved, 8 lines changed/added):

```python
import json
import random

from config import *
from metadata import (
    derive_customer_tone,
    derive_confidence,
    derive_difficulty,
    derive_escalation,
    derive_subdomain,
    pick_message,
)
from responses import get_output
from scenarios import INTENT_DOMAINS
from templates import build_instruction
from validate import is_valid_row


def generate_output(task_type, intent, domain=None, agent_tone=None):
    return get_output(task_type, intent, domain=domain, agent_tone=agent_tone)


def generate_row(i):
    intent = random.choice(list(INTENT_DOMAINS.keys()))
    customer_tone = derive_customer_tone(intent)
    message = pick_message(intent, customer_tone)

    task = random.choice(TASK_TYPES)
    agent_tone = random.choice(AGENT_TONES)

    allowed_domains = INTENT_DOMAINS.get(intent, DOMAINS)
    domain = random.choice(allowed_domains)
    channel = random.choice(CHANNELS)

    difficulty = derive_difficulty(intent)

    return {
        "id": f"lusosupport_pt_{i:06d}",
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "subdomain": derive_subdomain(intent, domain),
        "task_type": task,
        "customer_intent": intent,
        "customer_tone": customer_tone,
        "agent_tone": agent_tone,
        "channel": channel,
        "difficulty": difficulty,
        "instruction": build_instruction(task, agent_tone, domain, channel),
        "input": f"Mensagem do cliente: {message}",
        "output": generate_output(task, intent, domain=domain, agent_tone=agent_tone),
        "intent_classification": {
            "intent": intent,
            "confidence": derive_confidence(difficulty),
        },
        "metadata": {
            "requires_escalation": derive_escalation(intent, customer_tone),
            "contains_pii": False,
            "synthetic": True,
            "source_type": "template_generated",
        },
    }


def generate_dataset(n=50):
    return [generate_row(i) for i in range(n)]


def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic LusoSupport-PT rows.")
    parser.add_argument("--n", type=int, default=50, help="Number of rows to generate")
    parser.add_argument("--out", default="../datasets/interim/generated.jsonl", help="Output path")
    args = parser.parse_args()

    data = generate_dataset(args.n)
    valid = [r for r in data if is_valid_row(r)[0]]
    save_jsonl(valid, args.out)
    print(f"Generated {len(data)} rows, {len(valid)} passed validation → {args.out}")
```

- [ ] **Step 4: Run the 3 new tests to confirm they pass**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/test_generate.py::test_customer_tone_always_valid \
    tests/test_generate.py::test_escalation_request_always_requires_escalation \
    tests/test_generate.py::test_intent_classification_confidence_in_range -v
```

Expected: all 3 pass.

- [ ] **Step 5: Run full test suite**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/ -q
```

Expected: all tests pass (target: ~95+ total). Confirm zero failures before committing.

- [ ] **Step 6: Smoke-test the generator end-to-end**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from generate import generate_dataset
import json, collections

rows = generate_dataset(200)
print('subdomain placeholder count:', sum(1 for r in rows if r['subdomain']=='placeholder'))
print('requires_escalation True count:', sum(1 for r in rows if r['metadata']['requires_escalation']))
tone_ok = all(r['customer_tone'] in ('calm','confused','frustrated','urgent','formal','informal') for r in rows)
print('All tones valid:', tone_ok)
conf_ok = all(0.62 <= r['intent_classification']['confidence'] <= 0.99 for r in rows)
print('All confidences in range:', conf_ok)
diffs = collections.Counter(r['difficulty'] for r in rows)
print('difficulty distribution:', dict(diffs))
"
```

Expected output (approximate):
```
subdomain placeholder count: 0
requires_escalation True count: (some positive number)
All tones valid: True
All confidences in range: True
difficulty distribution: {'easy': ~X, 'medium': ~Y, 'hard': ~Z}
```

- [ ] **Step 7: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/generate.py tests/test_generate.py
git commit -m "feat(generate): wire metadata derivation functions — tone, subdomain, escalation, difficulty, confidence (issue #45)"
```

---

## Task 4: Project board sync + close issue #45

**Files:** none (operational task)

**Interfaces:** none

- [ ] **Step 1: Verify final test count**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
python3 -m pytest tests/ -q
```

Expected: ≥ 90 tests, all passing.

- [ ] **Step 2: Close issue #45**

```bash
gh issue close 45 --repo ariazevedopt/pt-ai-instruction-dataset \
  --comment "Phase 2 metadata correctness complete. All 5 fields now derived (not random/hardcoded). Tests: ≥90 passing."
```

- [ ] **Step 3: Update project board — set #45 to Done**

```bash
# Get item ID for issue #45 in project PVT_kwHOAS3Kg84BUljL
ITEM_ID=$(gh api graphql -f query='{ node(id:"PVT_kwHOAS3Kg84BUljL") { ... on ProjectV2 { items(first:50) { nodes { id content { ... on Issue { number } } } } } } }' --jq '.data.node.items.nodes[] | select(.content.number==45) | .id')

# Set status to Done (option id: 98236657)
gh api graphql \
  -f query='mutation($p:ID!,$i:ID!,$f:ID!,$v:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$v}}){projectV2Item{id}}}' \
  -f p="PVT_kwHOAS3Kg84BUljL" \
  -f i="$ITEM_ID" \
  -f f="PVTSSF_lAHOAS3Kg84BUljLzhBstHw" \
  -f v="98236657"
```

- [ ] **Step 4: Report**

Print a summary:
- Total tests passing
- `subdomain placeholder count: 0` confirmed
- `requires_escalation` working for escalation_request
- `customer_tone` correlated with message pool
- Project board #45 → Done
