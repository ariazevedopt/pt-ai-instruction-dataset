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
