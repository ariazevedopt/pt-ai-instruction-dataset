"""validate.py — Row validation for LusoSupport-PT dataset.

is_valid_row(row) -> (bool, str)
  Returns (True, "ok") if the row passes all checks.
  Returns (False, "<rule_name>") on the first failing rule.
"""
import json

from config import TASK_TYPES, DOMAINS

# Minimum output lengths by task type
_MIN_OUTPUT_LEN = {
    "response_generation": 80,
    "email_reply": 80,
    "summarization": 40,
    "intent_classification": 20,
    "urgency_classification": 20,
}
_DEFAULT_MIN_OUTPUT_LEN = 30

# PT-BR banned vocabulary
_BANNED_WORDS = [
    "celular",
    "senha",
    "nota fiscal",
    "assinatura",
    "código de rastreio",
    "contato",       # PT-PT uses "contacto"
]


def is_valid_row(row: dict) -> tuple:
    """Validate a single dataset row.

    Returns:
        (True, "ok") if all checks pass.
        (False, rule_name) on the first failing check.
    """
    # Rule 1 — id present
    if not row.get("id"):
        return False, "missing_id"

    # Rule 2 — language
    if row.get("language") != "pt":
        return False, "wrong_language"

    # Rule 3 — variant
    if row.get("variant") != "pt-PT":
        return False, "wrong_variant"

    # Rule 4 — task_type enum
    if row.get("task_type") not in TASK_TYPES:
        return False, "invalid_task_type"

    # Rule 5 — domain enum
    if row.get("domain") not in DOMAINS:
        return False, "invalid_domain"

    # Rule 6 — input prefix
    input_text = row.get("input", "")
    if "Mensagem do cliente:" not in input_text:
        return False, "missing_input_prefix"

    # Rule 7 — input length
    if len(input_text) < 30:
        return False, "input_too_short"

    output = row.get("output", "")

    # Rule 8-11 — output minimum length by task_type
    task_type = row.get("task_type", "")
    min_len = _MIN_OUTPUT_LEN.get(task_type, _DEFAULT_MIN_OUTPUT_LEN)
    if len(output) < min_len:
        return False, "output_too_short"

    # Rule 12 — stub detection
    if "[sem template" in output or "Resposta gerada" in output:
        return False, "output_stub"

    # Rule 13 — PT-BR vocabulary
    output_lower = output.lower()
    for word in _BANNED_WORDS:
        if word in output_lower:
            return False, f"pt_br_vocab:{word}"

    # Rule 14 — intent_classification JSON integrity
    if task_type == "intent_classification":
        try:
            parsed = json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return False, "json_missing_keys"
        required = {"intent", "urgency", "domain", "confidence"}
        if not required.issubset(parsed.keys()):
            return False, "json_missing_keys"
        if parsed.get("domain") != row.get("domain"):
            return False, "json_domain_mismatch"

    # Rule 15 — urgency_classification JSON integrity
    if task_type == "urgency_classification":
        try:
            parsed = json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return False, "json_urgency_missing_keys"
        # Accept either "reason" or "rationale" (both appear in seeds)
        has_reason = "reason" in parsed or "rationale" in parsed
        if "urgency" not in parsed or not has_reason:
            return False, "json_urgency_missing_keys"

    return True, "ok"
