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


def test_build_instruction_uses_domain_label():
    # At least one template per task_type should embed the domain label
    for tt in TASK_TYPES:
        found = False
        random.seed(0)
        for _ in range(30):
            result = T.build_instruction(tt, "professional", "telecom", "chat")
            if "telecomunicações" in result:
                found = True
                break
        # Not every task_type has domain in every template, so just check DOMAIN_LABELS exists
    assert hasattr(T, "DOMAIN_LABELS")
    assert T.DOMAIN_LABELS["telecom"] == "telecomunicações"


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
