"""Tests for generate.py diversity invariants (Phase 1 — issue #44)."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate import generate_dataset


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
