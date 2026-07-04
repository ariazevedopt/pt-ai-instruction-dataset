"""Tests for review_server.py helper functions."""
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Patch working directory so relative paths in review_server resolve
os.chdir(Path(__file__).parent.parent)

from review_server import (
    load_rows, load_reviewed_ids, sample_row,
    build_generated_row, rate_row,
)


def _make_row(id_="lusosupport_pt_000001", domain="ecommerce", task_type="response_generation",
              intent="refund_request"):
    return {
        "id": id_, "language": "pt", "variant": "pt-PT",
        "domain": domain, "subdomain": "placeholder",
        "task_type": task_type, "customer_intent": intent,
        "customer_tone": "calm", "agent_tone": "professional",
        "channel": "chat", "difficulty": "medium",
        "instruction": "Responde ao cliente.",
        "input": "Mensagem do cliente: Quero o reembolso.",
        "output": "Compreendemos a situação.",
        "metadata": {"requires_escalation": False, "contains_pii": False,
                     "synthetic": True, "source_type": "template_generated"},
    }


def _write_jsonl(path: Path, entries: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


# --- load_rows ---

def test_load_rows_empty(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("")
    assert load_rows(p) == []


def test_load_rows_returns_dicts(tmp_path):
    row = _make_row()
    p = tmp_path / "rows.jsonl"
    _write_jsonl(p, [row])
    result = load_rows(p)
    assert len(result) == 1
    assert result[0]["id"] == "lusosupport_pt_000001"


def test_load_rows_missing_file(tmp_path):
    assert load_rows(tmp_path / "nonexistent.jsonl") == []


# --- load_reviewed_ids ---

def test_load_reviewed_ids_empty(tmp_path):
    assert load_reviewed_ids(tmp_path) == set()


def test_load_reviewed_ids_reads_all_three_files(tmp_path):
    _write_jsonl(tmp_path / "approved.jsonl",       [{"id": "a1", "timestamp": "t"}])
    _write_jsonl(tmp_path / "rejected.jsonl",       [{"id": "r1", "reason": "bad", "timestamp": "t"}])
    _write_jsonl(tmp_path / "browser_ratings.jsonl",[{"id": "b1", "rating": "unclear", "timestamp": "t"}])
    ids = load_reviewed_ids(tmp_path)
    assert ids == {"a1", "r1", "b1"}


# --- sample_row ---

def test_sample_row_returns_unreviewed(tmp_path):
    rows = [_make_row(id_=f"lusosupport_pt_{i:06d}") for i in range(5)]
    reviewed = {"lusosupport_pt_000000", "lusosupport_pt_000001"}
    result = sample_row(rows, reviewed, mode="random")
    assert result is not None
    assert result["id"] not in reviewed


def test_sample_row_returns_none_when_all_reviewed(tmp_path):
    rows = [_make_row(id_="lusosupport_pt_000001")]
    assert sample_row(rows, {"lusosupport_pt_000001"}, mode="random") is None


def test_sample_row_flagged_mode_filters_to_flagged(tmp_path, monkeypatch):
    import review_server
    flagged_path = tmp_path / "flagged.jsonl"
    _write_jsonl(flagged_path, [{"id": "lusosupport_pt_000002", "reason": "duplicate_in_bucket"}])
    monkeypatch.setattr(review_server, "FEEDBACK_DIR", tmp_path)

    rows = [_make_row(id_=f"lusosupport_pt_{i:06d}") for i in range(5)]
    result = sample_row(rows, set(), mode="flagged")
    assert result is not None
    assert result["id"] == "lusosupport_pt_000002"


# --- build_generated_row ---

def test_build_generated_row_structure():
    row = build_generated_row(
        domain="ecommerce",
        task_type="response_generation",
        intent="refund_request",
        message="Quero o meu reembolso.",
    )
    assert row["id"].startswith("browser_generated_")
    assert row["language"] == "pt"
    assert row["variant"] == "pt-PT"
    assert row["domain"] == "ecommerce"
    assert row["task_type"] == "response_generation"
    assert row["customer_intent"] == "refund_request"
    assert "Quero o meu reembolso." in row["input"]
    assert len(row["output"]) > 0
    assert row["metadata"]["source_type"] == "browser_generated"


# --- rate_row ---

def test_rate_good_writes_approved(tmp_path):
    rate_row("id1", "good", "", {}, feedback_dir=tmp_path)
    entries = [json.loads(l) for l in (tmp_path / "approved.jsonl").read_text().splitlines() if l.strip()]
    assert any(e["id"] == "id1" for e in entries)
    assert "reason" not in entries[-1]


def test_rate_bad_writes_rejected_with_reason(tmp_path):
    rate_row("id2", "bad", "output is wrong domain", {}, feedback_dir=tmp_path)
    entries = [json.loads(l) for l in (tmp_path / "rejected.jsonl").read_text().splitlines() if l.strip()]
    assert entries[-1]["id"] == "id2"
    assert entries[-1]["reason"] == "output is wrong domain"


def test_rate_bad_uses_default_reason_when_no_comment(tmp_path):
    rate_row("id3", "bad", "", {}, feedback_dir=tmp_path)
    entries = [json.loads(l) for l in (tmp_path / "rejected.jsonl").read_text().splitlines() if l.strip()]
    assert entries[-1]["reason"] == "browser:bad"


def test_rate_unclear_writes_browser_ratings(tmp_path):
    row = _make_row()
    rate_row("id4", "unclear", "borderline", row, feedback_dir=tmp_path)
    entries = [json.loads(l) for l in (tmp_path / "browser_ratings.jsonl").read_text().splitlines() if l.strip()]
    assert entries[-1]["id"] == "id4"
    assert entries[-1]["rating"] == "unclear"
    assert entries[-1]["comment"] == "borderline"
    assert "row" in entries[-1]


def test_rate_appends_not_overwrites(tmp_path):
    rate_row("id5", "good", "", {}, feedback_dir=tmp_path)
    rate_row("id6", "good", "", {}, feedback_dir=tmp_path)
    lines = (tmp_path / "approved.jsonl").read_text().splitlines()
    assert len([l for l in lines if l.strip()]) == 2
