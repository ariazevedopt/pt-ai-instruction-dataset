"""validate.py — Row validation for LusoSupport-PT dataset.

is_valid_row(row) -> (bool, str)
  Returns (True, "ok") if the row passes all checks.
  Returns (False, "<rule_name>") on the first failing rule.
"""
import json
import re

from config import (
    TASK_TYPES, DOMAINS,
    CUSTOMER_INTENTS, CUSTOMER_TONES, AGENT_TONES, CHANNELS, DIFFICULTY_LEVELS,
)

# Minimum output lengths by task type
_MIN_OUTPUT_LEN = {
    "response_generation": 80,
    "email_reply": 80,
    "summarization": 40,
    "intent_classification": 20,
    "urgency_classification": 20,
}
_DEFAULT_MIN_OUTPUT_LEN = 30

# PT-BR banned vocabulary — enforced on agent OUTPUT only (see Rule 19).
# These are terms with a distinct pt-PT equivalent that a European Portuguese
# support agent should always use. Customer INPUT is deliberately NOT checked
# against this list (see Rule 13 note below): real pt-PT speakers sometimes
# use pt-BR-influenced vocabulary (media/app exposure, code-switching), and
# the dataset intentionally includes some such rows so a fine-tuned model
# learns to recognise the term and still respond with the correct pt-PT
# equivalent. See docs/pt-pt-style-guide.md for the full pt-BR → pt-PT map
# and the rationale (resolves issue #55).
#
# NOTE: "assinatura" and "código de rastreio" were previously included here
# but are NOT pt-BR-exclusive — both are standard European Portuguese
# (e.g. "assinatura de um serviço", "código de rastreio da encomenda" is the
# term used by CTT). They were removed as false positives.
_BANNED_WORDS = [
    "celular",     # pt-PT: telemóvel
    "senha",       # pt-PT: palavra-passe
    "nota fiscal", # pt-PT: fatura
    "contato",     # pt-PT: contacto
]


def is_valid_row(row: dict) -> tuple:
    """Validate a single dataset row.

    Returns:
        (True, "ok") if all checks pass.
        (False, rule_name) on the first failing check.
    """
    # Rule 1 — id present and format valid
    row_id = row.get("id", "")
    if not row_id:
        return False, "missing_id"
    if not re.fullmatch(r"lusosupport_pt_\d{6}", row_id):
        return False, "invalid_id_format"

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

    # Rule 6 — customer_intent enum
    if row.get("customer_intent") not in CUSTOMER_INTENTS:
        return False, "invalid_customer_intent"

    # Rule 7 — customer_tone enum
    if row.get("customer_tone") not in CUSTOMER_TONES:
        return False, "invalid_customer_tone"

    # Rule 8 — agent_tone enum
    if row.get("agent_tone") not in AGENT_TONES:
        return False, "invalid_agent_tone"

    # Rule 9 — channel enum
    if row.get("channel") not in CHANNELS:
        return False, "invalid_channel"

    # Rule 10 — difficulty enum
    if row.get("difficulty") not in DIFFICULTY_LEVELS:
        return False, "invalid_difficulty"

    # Rule 11 — input prefix
    input_text = row.get("input", "")
    if "Mensagem do cliente:" not in input_text:
        return False, "missing_input_prefix"

    # Rule 12 — input length
    if len(input_text) < 30:
        return False, "input_too_short"

    # Rule 13 — PT-BR vocabulary is intentionally NOT banned in customer input.
    # Real customers may use pt-BR-influenced terms (e.g. "celular", "senha");
    # the dataset includes some such rows on purpose so the agent OUTPUT (Rule 19,
    # always strict) demonstrates understanding the term and replying with the
    # correct pt-PT equivalent. See docs/pt-pt-style-guide.md.

    output = row.get("output", "")

    # Rule 14-17 — output minimum length by task_type
    task_type = row.get("task_type", "")
    min_len = _MIN_OUTPUT_LEN.get(task_type, _DEFAULT_MIN_OUTPUT_LEN)
    if len(output) < min_len:
        return False, "output_too_short"

    # Rule 18 — stub detection
    if "[sem template" in output or "Resposta gerada" in output:
        return False, "output_stub"

    # Rule 19 — PT-BR vocabulary in output
    output_lower = output.lower()
    for word in _BANNED_WORDS:
        if word in output_lower:
            return False, f"pt_br_vocab:{word}"

    # Rule 20 — intent_classification JSON integrity
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

    # Rule 21 — urgency_classification JSON integrity
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
