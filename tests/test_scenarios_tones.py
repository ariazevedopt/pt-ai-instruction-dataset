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
BANNED = ["celular", "senha", "nota fiscal", "assinatura", "código de rastreio", "contato", "cadê", "oi,", "tá,"]


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
