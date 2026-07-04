"""Tests for flag.py — automated dataset scanner."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from flag import scan_dataset


def _make_dataset(tmp_path, rows):
    p = tmp_path / "processed.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return p


def _good_row(id_="lusosupport_pt_000100", domain="ecommerce",
              task_type="response_generation"):
    return {
        "id": id_,
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "task_type": task_type,
        "customer_intent": "order_status",
        "customer_tone": "calm",
        "agent_tone": "professional",
        "channel": "email",
        "difficulty": "easy",
        "input": "Mensagem do cliente: A minha encomenda não chegou ainda.",
        "output": (
            "Lamentamos o sucedido. Para darmos seguimento à situação, "
            "pedimos que nos indique o número da encomenda e entraremos "
            "em contacto brevemente com uma atualização."
        ),
    }


def test_good_row_not_flagged(tmp_path):
    p = _make_dataset(tmp_path, [_good_row()])
    flags = scan_dataset(p, tmp_path, approved_ids=set())
    assert flags == []


def test_validate_rule_violation_flagged(tmp_path):
    bad = _good_row()
    bad["output"] = "Redefina a sua senha aqui para continuar e aceder novamente à sua conta. Pedimos desculpa pelo transtorno."
    p = _make_dataset(tmp_path, [bad])
    flags = scan_dataset(p, tmp_path, approved_ids=set())
    assert len(flags) == 1
    assert flags[0]["reason"].startswith("pt_br_vocab")


def test_duplicate_output_in_bucket_flagged(tmp_path):
    same_output = (
        "Lamentamos o sucedido. Verifique o estado da sua encomenda e "
        "entre em contacto connosco para mais informações detalhadas."
    )
    rows = [
        {**_good_row(id_=f"lusosupport_pt_{i:06d}"), "output": same_output}
        for i in range(100, 103)
    ]
    p = _make_dataset(tmp_path, rows)
    flags = scan_dataset(p, tmp_path, approved_ids=set())
    reasons = [f["reason"] for f in flags]
    assert any("duplicate_in_bucket" in r for r in reasons)


def test_approved_rows_skipped(tmp_path):
    bad = _good_row()
    bad["output"] = "Redefina a sua senha aqui para continuar e aceder novamente à sua conta. Pedimos desculpa pelo transtorno."
    p = _make_dataset(tmp_path, [bad])
    flags = scan_dataset(p, tmp_path, approved_ids={"lusosupport_pt_000100"})
    assert flags == []


def test_flagged_jsonl_written(tmp_path):
    bad = _good_row()
    bad["output"] = "Redefina a sua senha aqui para continuar e aceder novamente à sua conta. Pedimos desculpa pelo transtorno."
    p = _make_dataset(tmp_path, [bad])
    scan_dataset(p, tmp_path, approved_ids=set())
    flagged_path = tmp_path / "flagged.jsonl"
    assert flagged_path.exists()
    entry = json.loads(flagged_path.read_text().strip())
    assert entry["id"] == "lusosupport_pt_000100"
