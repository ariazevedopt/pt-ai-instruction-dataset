"""Tests for export_formats.py — to_amalia_chat_jsonl()"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from export_formats import to_amalia_chat_jsonl


def _row(id_="001"):
    return {
        "id": id_,
        "instruction": "Responde ao pedido do cliente sobre o estado da encomenda.",
        "input": "Onde está a minha encomenda?",
        "output": "A sua encomenda está a caminho e deve chegar amanhã.",
        "metadata": {"synthetic": True, "source_type": "template_generated"},
    }


def test_writes_one_line_per_row(tmp_path):
    path = tmp_path / "out.jsonl"
    to_amalia_chat_jsonl([_row("001"), _row("002")], str(path))
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2


def test_messages_have_system_user_assistant_roles(tmp_path):
    path = tmp_path / "out.jsonl"
    to_amalia_chat_jsonl([_row()], str(path))
    row = json.loads(path.read_text(encoding="utf-8").strip())
    roles = [m["role"] for m in row["messages"]]
    assert roles == ["system", "user", "assistant"]


def test_message_content_maps_instruction_input_output(tmp_path):
    path = tmp_path / "out.jsonl"
    r = _row()
    to_amalia_chat_jsonl([r], str(path))
    row = json.loads(path.read_text(encoding="utf-8").strip())
    system_msg, user_msg, assistant_msg = row["messages"]
    assert system_msg["content"] == r["instruction"]
    assert user_msg["content"] == r["input"]
    assert assistant_msg["content"] == r["output"]


def test_output_has_no_hardcoded_chatml_tokens(tmp_path):
    """The exporter must not hand-roll <|im_start|>/<|im_end|> text — the
    target model's own tokenizer.apply_chat_template() should apply those,
    so the export stays valid even if AMALIA's template changes."""
    path = tmp_path / "out.jsonl"
    to_amalia_chat_jsonl([_row()], str(path))
    content = path.read_text(encoding="utf-8")
    assert "<|im_start|>" not in content
    assert "<|im_end|>" not in content


def test_empty_rows_writes_empty_file(tmp_path):
    path = tmp_path / "out.jsonl"
    to_amalia_chat_jsonl([], str(path))
    assert path.read_text(encoding="utf-8") == ""
