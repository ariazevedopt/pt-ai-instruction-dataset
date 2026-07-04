"""Tests for dedupe.py — deduplicate()"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from dedupe import deduplicate, _row_fingerprint


def _row(id_, output="Resposta de teste para validação."):
    return {
        "id": id_,
        "instruction": "Responde ao cliente.",
        "input": "Mensagem do cliente: Preciso de ajuda.",
        "output": output,
    }


def test_empty_input_returns_empty():
    assert deduplicate([]) == []


def test_no_duplicates_unchanged():
    rows = [_row("001", "Resposta A."), _row("002", "Resposta B.")]
    result = deduplicate(rows)
    assert len(result) == 2


def test_exact_duplicate_removed():
    row = _row("001")
    result = deduplicate([row, row])
    assert len(result) == 1


def test_same_content_different_id_is_duplicate():
    r1 = _row("001", "Texto de saída idêntico.")
    r2 = _row("002", "Texto de saída idêntico.")
    result = deduplicate([r1, r2])
    assert len(result) == 1
    assert result[0]["id"] == "001"  # first occurrence kept


def test_different_output_not_deduplicated():
    r1 = _row("001", "Primeira resposta.")
    r2 = _row("001", "Segunda resposta diferente.")
    result = deduplicate([r1, r2])
    assert len(result) == 2


def test_different_instruction_not_deduplicated():
    r1 = {**_row("001"), "instruction": "Instrução A."}
    r2 = {**_row("001"), "instruction": "Instrução B."}
    result = deduplicate([r1, r2])
    assert len(result) == 2


def test_fingerprint_is_stable():
    row = _row("001")
    assert _row_fingerprint(row) == _row_fingerprint(row)


def test_fingerprint_differs_on_output_change():
    r1 = _row("001", "Saída A.")
    r2 = _row("001", "Saída B.")
    assert _row_fingerprint(r1) != _row_fingerprint(r2)


def test_large_batch_dedup():
    rows = [_row(str(i), "Resposta repetida igual.") for i in range(100)]
    result = deduplicate(rows)
    assert len(result) == 1
