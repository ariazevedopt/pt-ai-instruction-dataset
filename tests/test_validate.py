"""Tests for validate.py — is_valid_row() returns (bool, str)."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from validate import is_valid_row


def _row(**overrides):
    base = {
        "id": "lusosupport_pt_000001",
        "language": "pt",
        "variant": "pt-PT",
        "domain": "ecommerce",
        "task_type": "response_generation",
        "input": "Mensagem do cliente: A encomenda não chegou.",
        "output": "Lamentamos o sucedido. Para darmos seguimento à sua situação, pedimos que nos indique o número da encomenda e entraremos em contacto brevemente.",
    }
    base.update(overrides)
    return base


# ── basic pass ────────────────────────────────────────────────────────────────
def test_valid_row_passes():
    ok, reason = is_valid_row(_row())
    assert ok is True
    assert reason == "ok"


# ── rule 1: id ────────────────────────────────────────────────────────────────
def test_missing_id_fails():
    ok, reason = is_valid_row(_row(id=""))
    assert ok is False
    assert reason == "missing_id"

    ok2, _ = is_valid_row({k: v for k, v in _row().items() if k != "id"})
    assert ok2 is False


# ── rule 2: language ──────────────────────────────────────────────────────────
def test_wrong_language_fails():
    ok, reason = is_valid_row(_row(language="en"))
    assert ok is False
    assert reason == "wrong_language"


# ── rule 3: variant ───────────────────────────────────────────────────────────
def test_wrong_variant_fails():
    ok, reason = is_valid_row(_row(variant="pt-BR"))
    assert ok is False
    assert reason == "wrong_variant"


# ── rule 4: task_type enum ────────────────────────────────────────────────────
def test_invalid_task_type_fails():
    ok, reason = is_valid_row(_row(task_type="magic"))
    assert ok is False
    assert reason == "invalid_task_type"


def test_valid_task_type_passes():
    for tt in ["response_generation", "email_reply", "summarization",
               "rewrite_professional", "next_action_suggestion", "faq_answer"]:
        ok, _ = is_valid_row(_row(task_type=tt))
        assert ok is True, f"task_type={tt} should pass"
    
    # Test classification tasks with valid JSON
    ok_intent, _ = is_valid_row(_row(
        task_type="intent_classification",
        output=json.dumps({"intent": "refund_request", "urgency": "low",
                           "domain": "ecommerce", "confidence": 0.91})
    ))
    assert ok_intent is True, "task_type=intent_classification should pass with valid JSON"
    
    ok_urgency, _ = is_valid_row(_row(
        task_type="urgency_classification",
        output=json.dumps({"urgency": "high", "reason": "Serviço em falha.", "escalate": True})
    ))
    assert ok_urgency is True, "task_type=urgency_classification should pass with valid JSON"


# ── rule 5: domain enum ───────────────────────────────────────────────────────
def test_invalid_domain_fails():
    ok, reason = is_valid_row(_row(domain="interplanetary"))
    assert ok is False
    assert reason == "invalid_domain"


# ── rule 6: input prefix ──────────────────────────────────────────────────────
def test_missing_input_prefix_fails():
    ok, reason = is_valid_row(_row(input="O cliente perguntou sobre a encomenda."))
    assert ok is False
    assert reason == "missing_input_prefix"


# ── rule 7: input length ──────────────────────────────────────────────────────
def test_input_too_short_fails():
    ok, reason = is_valid_row(_row(input="Mensagem do cliente: Ok"))
    assert ok is False
    assert reason == "input_too_short"


# ── rules 8-11: output length by task_type ───────────────────────────────────
def test_response_generation_short_output_fails():
    ok, reason = is_valid_row(_row(task_type="response_generation", output="Olá."))
    assert ok is False
    assert reason == "output_too_short"


def test_email_reply_short_output_fails():
    ok, reason = is_valid_row(_row(task_type="email_reply", output="Olá, obrigado."))
    assert ok is False
    assert reason == "output_too_short"


def test_summarization_short_output_fails():
    ok, reason = is_valid_row(_row(task_type="summarization", output="Resumo."))
    assert ok is False
    assert reason == "output_too_short"


def test_classification_minimum_length():
    # 20-char JSON passes
    ok, _ = is_valid_row(_row(
        task_type="intent_classification",
        domain="ecommerce",
        output=json.dumps({"intent": "refund_request", "urgency": "low",
                           "domain": "ecommerce", "confidence": 0.91}),
    ))
    assert ok is True


# ── rule 12: stubs ────────────────────────────────────────────────────────────
def test_stub_output_fails():
    ok, reason = is_valid_row(_row(output="[sem template para response_generation/refund_request] e mais texto aqui para passar o comprimento mínimo de 80 caracteres necessários."))
    assert ok is False
    assert reason == "output_stub"

    ok2, reason2 = is_valid_row(_row(output="Resposta gerada para o cliente e mais conteúdo suficiente para passar os 80 caracteres mínimos."))
    assert ok2 is False
    assert reason2 == "output_stub"


# ── rule 13: pt-BR banned words ───────────────────────────────────────────────
def test_banned_ptbr_words_fail():
    for word, phrase in [
        ("celular", "Ligue para o seu celular agora. Vamos resolver a sua questão com urgência absoluta."),
        ("senha", "Redefina a sua senha aqui através deste link seguro. Procederemos à recuperação."),
        ("nota fiscal", "Enviamos a nota fiscal por e-mail em anexo. Encontrará todos os detalhes no documento."),
        ("assinatura", "A sua assinatura foi cancelada conforme solicitado. Confirmaremos via e-mail hoje."),
        ("código de rastreio", "Utilize o código de rastreio para acompanhar a encomenda em tempo real no nosso site."),
    ]:
        ok, reason = is_valid_row(_row(output=phrase))
        assert ok is False, f"banned word '{word}' should fail"
        assert reason.startswith("pt_br_vocab"), f"reason should be pt_br_vocab, got {reason}"


def test_ptpt_vocabulary_passes():
    ok, _ = is_valid_row(_row(
        output="A sua palavra-passe foi redefinida. O telemóvel associado foi verificado. "
               "A encomenda com número de seguimento foi processada. A fatura foi emitida."
    ))
    assert ok is True


# ── rule 14: intent_classification JSON ──────────────────────────────────────
def test_intent_classification_valid_json_passes():
    output = json.dumps({
        "intent": "refund_request", "urgency": "high",
        "domain": "ecommerce", "confidence": 0.95
    })
    ok, reason = is_valid_row(_row(task_type="intent_classification",
                                   domain="ecommerce", output=output))
    assert ok is True, reason


def test_intent_classification_domain_mismatch_fails():
    output = json.dumps({
        "intent": "account_access", "urgency": "medium",
        "domain": "saas", "confidence": 0.88
    })
    ok, reason = is_valid_row(_row(task_type="intent_classification",
                                   domain="subscriptions", output=output))
    assert ok is False
    assert reason == "json_domain_mismatch"


def test_intent_classification_missing_key_fails():
    output = json.dumps({"intent": "refund_request", "urgency": "high"})
    ok, reason = is_valid_row(_row(task_type="intent_classification",
                                   domain="ecommerce", output=output))
    assert ok is False
    assert reason == "json_missing_keys"


# ── rule 15: urgency_classification JSON ─────────────────────────────────────
def test_urgency_classification_valid_json_passes():
    output = json.dumps({
        "urgency": "high", "reason": "Serviço em falha.", "escalate": True
    })
    ok, reason = is_valid_row(_row(task_type="urgency_classification", output=output))
    assert ok is True, reason


def test_urgency_classification_missing_key_fails():
    # Make it long enough to pass length check but fail JSON validation
    output = json.dumps({"urgency": "high", "extra": "padding text to reach minimum"})
    ok, reason = is_valid_row(_row(task_type="urgency_classification", output=output))
    assert ok is False
    assert reason == "json_urgency_missing_keys"
