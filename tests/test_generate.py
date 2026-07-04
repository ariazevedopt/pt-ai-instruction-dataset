"""Tests for generate.py diversity invariants (Phase 1 — issue #44)."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate import generate_dataset, generate_row


def _sample(n=200, seed=42):
    random.seed(seed)
    return generate_dataset(n)


def test_no_unfilled_placeholders():
    """No generated field should contain an unfilled {placeholder}."""
    rows = _sample(200)
    text_fields = ["instruction", "input", "output"]
    classification_types = {"intent_classification", "urgency_classification"}
    for i, row in enumerate(rows):
        for field in text_fields:
            value = row.get(field, "")
            # Skip JSON outputs from classification tasks
            if field == "output" and row["task_type"] in classification_types:
                continue
            assert "{" not in value and "}" not in value, (
                f"Row {i} field '{field}' has unfilled placeholder: {value!r}"
            )


def test_instruction_diversity():
    """200 generated rows must produce at least 50 unique instructions."""
    rows = _sample(200)
    unique_instructions = {r["instruction"] for r in rows}
    assert len(unique_instructions) >= 50, (
        f"Only {len(unique_instructions)} unique instructions in 200 rows — need ≥50"
    )


def test_domain_label_fills_in_parametric_outputs():
    """Domain labels must fill correctly when a parametric template is selected.

    Only ~6 of ~80+ (task_type, intent) keys have {domain_label} templates.
    This test directly verifies the filling mechanism on those keys rather
    than relying on random sampling frequency.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from responses import get_output
    from templates import DOMAIN_LABELS
    import random

    parametric_pairs = [
        ("response_generation", "refund_request"),
        ("response_generation", "technical_issue"),
        ("response_generation", "complaint"),
        ("email_reply", "billing_question"),
        ("next_action_suggestion", "escalation_request"),
        ("summarization", "technical_issue"),
    ]

    for task_type, intent in parametric_pairs:
        filled_with_label = False
        for seed in range(30):
            random.seed(seed)
            result = get_output(task_type, intent, domain="telecom", agent_tone="empathetic")
            assert "{" not in result and "}" not in result, (
                f"Unfilled placeholder in ({task_type}, {intent}): {result!r}"
            )
            if "telecomunicações" in result:
                filled_with_label = True
                break
        assert filled_with_label, (
            f"No domain label found in 30 samples of ({task_type}, {intent}) with domain='telecom'. "
            f"At least one parametric template should reference domain_label."
        )


def test_all_generated_rows_pass_validation():
    """All generated rows must pass is_valid_row()."""
    from validate import is_valid_row
    rows = _sample(100)
    for i, row in enumerate(rows):
        ok, reason = is_valid_row(row)
        assert ok, f"Row {i} failed validation: {reason} — {row}"


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
