"""Tests for pipeline exclusion and correction logic."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from pipeline import load_seed_ids, load_exclusion_ids, load_corrections


def _write_jsonl(path, entries):
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def test_load_seed_ids_returns_set(tmp_path):
    seeds_file = tmp_path / "seeds.jsonl"
    _write_jsonl(seeds_file, [
        {"id": "lusosupport_pt_000001", "output": "ok ok ok ok ok ok ok ok ok ok ok"},
        {"id": "lusosupport_pt_000002", "output": "ok ok ok ok ok ok ok ok ok ok ok"},
    ])
    ids = load_seed_ids(seeds_file)
    assert ids == {"lusosupport_pt_000001", "lusosupport_pt_000002"}


def test_load_exclusion_ids_reads_flagged_and_rejected(tmp_path):
    seed_ids = {"lusosupport_pt_000001"}
    _write_jsonl(tmp_path / "flagged.jsonl", [
        {"id": "lusosupport_pt_000050", "reason": "output_too_short", "row": {}},
    ])
    _write_jsonl(tmp_path / "rejected.jsonl", [
        {"id": "lusosupport_pt_000051", "reason": "output too generic",
         "timestamp": "2026-01-01"},
    ])
    excluded = load_exclusion_ids(tmp_path, seed_ids)
    assert "lusosupport_pt_000050" in excluded
    assert "lusosupport_pt_000051" in excluded


def test_seeds_are_never_excluded(tmp_path):
    seed_ids = {"lusosupport_pt_000001"}
    _write_jsonl(tmp_path / "flagged.jsonl", [
        {"id": "lusosupport_pt_000001", "reason": "output_too_short", "row": {}},
    ])
    excluded = load_exclusion_ids(tmp_path, seed_ids)
    assert "lusosupport_pt_000001" not in excluded


def test_load_corrections_returns_dict(tmp_path):
    _write_jsonl(tmp_path / "corrections.jsonl", [
        {
            "id": "lusosupport_pt_000100",
            "original_output": "bad output",
            "corrected_output": "Boa tarde, lamentamos o sucedido.",
            "timestamp": "2026-01-01T10:00:00",
        }
    ])
    corrections = load_corrections(tmp_path)
    assert corrections["lusosupport_pt_000100"] == "Boa tarde, lamentamos o sucedido."


def test_load_corrections_empty_when_no_file(tmp_path):
    corrections = load_corrections(tmp_path)
    assert corrections == {}
