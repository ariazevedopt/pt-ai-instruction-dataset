"""Tests for validate.py — is_valid_row()"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from validate import is_valid_row


def _row(**overrides):
    base = {
        "id": "lusosupport_pt_000001",
        "language": "pt",
        "variant": "pt-PT",
        "output": "Lamentamos a situação. Vamos ajudá-lo com a sua encomenda.",
    }
    base.update(overrides)
    return base


def test_valid_row_passes():
    assert is_valid_row(_row()) is True


def test_missing_id_fails():
    assert is_valid_row(_row(id="")) is False
    assert is_valid_row({k: v for k, v in _row().items() if k != "id"}) is False


def test_wrong_language_fails():
    assert is_valid_row(_row(language="en")) is False
    assert is_valid_row(_row(language="pt-BR")) is False


def test_wrong_variant_fails():
    assert is_valid_row(_row(variant="pt-BR")) is False
    assert is_valid_row(_row(variant="")) is False


def test_short_output_fails():
    assert is_valid_row(_row(output="ok")) is False
    assert is_valid_row(_row(output="")) is False


def test_banned_ptbr_words_fail():
    assert is_valid_row(_row(output="Por favor redefina sua senha aqui.")) is False
    assert is_valid_row(_row(output="Ligue para o seu celular.")) is False
    assert is_valid_row(_row(output="Enviamos a nota fiscal por e-mail.")) is False


def test_output_exactly_10_chars_passes():
    assert is_valid_row(_row(output="1234567890")) is True


def test_output_9_chars_fails():
    assert is_valid_row(_row(output="123456789")) is False


def test_ptpt_vocabulary_passes():
    row = _row(output="A sua palavra-passe foi redefinida com sucesso. O telemóvel associado foi verificado.")
    assert is_valid_row(row) is True
