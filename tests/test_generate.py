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


def test_domain_label_appears_in_outputs():
    """Domain label should appear in at least 1% of non-classification prose outputs."""
    from templates import DOMAIN_LABELS
    rows = _sample(300)
    classification_types = {"intent_classification", "urgency_classification"}
    prose_rows = [r for r in rows if r["task_type"] not in classification_types]
    if not prose_rows:
        return
    hits = 0
    for row in prose_rows:
        label = DOMAIN_LABELS.get(row["domain"], "")
        if label and label in row["output"]:
            hits += 1
    ratio = hits / len(prose_rows)
    # Domain label should appear in ≥2% of prose outputs (only parametric templates contribute)
    assert ratio >= 0.02, (
        f"Domain label appeared in only {100*ratio:.1f}% of prose outputs — need ≥2%"
    )


def test_all_generated_rows_pass_validation():
    """All generated rows must pass is_valid_row()."""
    from validate import is_valid_row
    rows = _sample(100)
    for i, row in enumerate(rows):
        ok, reason = is_valid_row(row)
        assert ok, f"Row {i} failed validation: {reason} — {row}"
