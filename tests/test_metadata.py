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
