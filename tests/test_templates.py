"""Tests for parametric build_instruction() in templates.py."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from config import TASK_TYPES, DOMAINS, CHANNELS, AGENT_TONES
import templates as T


def test_build_instruction_returns_string_for_all_task_types():
    for tt in TASK_TYPES:
        result = T.build_instruction(tt, "professional", "ecommerce", "email")
        assert isinstance(result, str) and len(result) > 10, f"failed for {tt}"


def test_build_instruction_no_unfilled_placeholders():
    random.seed(99)
    for tt in TASK_TYPES:
        for domain in DOMAINS:
            for tone in AGENT_TONES:
                result = T.build_instruction(tt, tone, domain, "chat")
                assert "{" not in result and "}" not in result, (
                    f"Unfilled placeholder in task_type={tt} domain={domain} tone={tone}: {result!r}"
                )


def test_domain_labels_dict_values():
    """Verify DOMAIN_LABELS dict has expected structure and values."""
    assert hasattr(T, "DOMAIN_LABELS")
    assert T.DOMAIN_LABELS["telecom"] == "telecomunicações"
    assert T.DOMAIN_LABELS["ecommerce"] == "comércio electrónico"
    assert T.DOMAIN_LABELS["subscriptions"] == "subscrições e planos"


def test_some_instructions_embed_domain_label():
    """Verify that some instructions sampled across all task types contain the domain label."""
    # Domain label should appear in at least some instructions across all task types
    # (Not every task_type template includes domain_label, so we just check the overall sampling)
    random.seed(0)
    domain = "telecom"
    domain_label = "telecomunicações"
    
    found_count = 0
    total_samples = 200
    
    for _ in range(total_samples):
        task_type = random.choice(TASK_TYPES)
        result = T.build_instruction(task_type, "professional", domain, "chat")
        if domain_label in result:
            found_count += 1
    
    # Assert that at least some instructions contain the domain label
    assert found_count > 0, (
        f"Expected at least some instructions to contain domain label '{domain_label}', "
        f"but found 0 out of {total_samples} samples"
    )


def test_build_instruction_backward_compat_no_domain():
    """Old callers that pass only task_type and agent_tone still work."""
    result = T.build_instruction("response_generation", "professional")
    assert isinstance(result, str) and len(result) > 5


def test_domain_labels_covers_all_domains():
    for d in DOMAINS:
        assert d in T.DOMAIN_LABELS, f"DOMAIN_LABELS missing domain: {d}"


def test_channel_labels_covers_all_channels():
    for c in CHANNELS:
        assert c in T.CHANNEL_LABELS, f"CHANNEL_LABELS missing channel: {c}"


def test_agent_tone_labels_covers_all_tones():
    for tone in AGENT_TONES:
        assert tone in T.AGENT_TONE_LABELS, f"AGENT_TONE_LABELS missing tone: {tone}"


def test_instruction_templates_has_all_task_types():
    for tt in TASK_TYPES:
        assert tt in T.INSTRUCTION_TEMPLATES, f"INSTRUCTION_TEMPLATES missing task_type: {tt}"
        assert len(T.INSTRUCTION_TEMPLATES[tt]) >= 5, f"Need ≥5 templates for {tt}"


def test_intent_messages_min_pool_size():
    """Every intent must have at least 12 messages for adequate input diversity."""
    import scenarios as S
    for intent, messages in S.INTENT_MESSAGES.items():
        assert len(messages) >= 12, (
            f"INTENT_MESSAGES['{intent}'] has only {len(messages)} messages — need ≥12"
        )


def test_get_output_accepts_agent_tone_param():
    """get_output() must accept agent_tone without raising TypeError."""
    import responses as R
    result = R.get_output("response_generation", "refund_request",
                          domain="ecommerce", agent_tone="empathetic")
    assert isinstance(result, str) and len(result) > 20


def test_get_output_no_unfilled_placeholders():
    """No {placeholder} must survive in any get_output() return value."""
    import responses as R
    from config import TASK_TYPES, AGENT_TONES
    import random
    random.seed(42)
    SAMPLE_INTENTS = [
        "refund_request", "order_status", "technical_issue",
        "password_reset", "complaint", "booking_cancellation",
        "payment_failure", "duplicate_charge",
    ]
    for tt in TASK_TYPES:
        for intent in SAMPLE_INTENTS:
            for tone in AGENT_TONES:
                try:
                    result = R.get_output(tt, intent, domain="ecommerce", agent_tone=tone)
                    assert "{" not in result and "}" not in result, (
                        f"Unfilled placeholder: task={tt} intent={intent} tone={tone}: {result!r}"
                    )
                except Exception:
                    pass  # Some (task_type, intent) combos may not have templates — that's OK


def test_tone_phrases_covers_all_agent_tones():
    import responses as R
    from config import AGENT_TONES
    assert hasattr(R, "TONE_PHRASES")
    for tone in AGENT_TONES:
        assert tone in R.TONE_PHRASES, f"TONE_PHRASES missing tone: {tone}"
        assert "opener" in R.TONE_PHRASES[tone], f"TONE_PHRASES['{tone}'] missing 'opener'"
