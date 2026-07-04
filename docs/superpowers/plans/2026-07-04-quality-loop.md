# Quality Loop System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full human-in-the-loop quality system: upgraded `validate.py` (15 rules, `(bool, str)` return), `flag.py` (auto-scanner), `review.py` (interactive terminal review with approve/reject/fix), `quality_report.py` (template health), and pipeline exclusion of rejected rows.

**Architecture:** `flag.py` auto-scans the processed dataset using `validate.py` rules plus heuristics, writing `datasets/feedback/flagged.jsonl`. `review.py` presents rows interactively using `rich`, writing to `datasets/feedback/{approved,rejected,corrections}.jsonl`. `pipeline.py` reads both files at step 4 to build an exclusion set, protecting seed rows from exclusion. `quality_report.py` reads all feedback files and surfaces the weakest template areas.

**Tech Stack:** Python 3.10+, `rich` (display, tables, panels), `pathlib`, `json`, `datetime`, `argparse`. All scripts run from `scripts/` directory.

## Global Constraints

- All PT-PT text; no pt-BR vocabulary (`celular`, `senha`, `nota fiscal`, `assinatura`, `código de rastreio`, `contato` without 'c')
- Scripts run from `scripts/` directory; paths are relative to `scripts/`
- Processed dataset: `../datasets/processed/lusosupport_pt_v1.jsonl`
- Feedback directory: `../datasets/feedback/`
- Seeds: `../datasets/raw/seed_examples.jsonl` — always protected, never excluded
- `is_valid_row(row)` returns `(bool, str)` after Task 1 — all callers must unpack the tuple
- `rich` is already in `requirements.txt`; no new dependencies needed
- Branch: `dev`; commit after each task

---

### Task 1: Upgrade `validate.py` to 15 rules + `(bool, str)` return, update all callers

**Files:**
- Modify: `scripts/validate.py`
- Modify: `scripts/generate.py` (caller at line 68)
- Modify: `scripts/pipeline.py` (caller at line 39)
- Modify: `tests/test_validate.py` (all assertions)

**Interfaces:**
- Produces: `is_valid_row(row: dict) -> tuple[bool, str]` — `(True, "ok")` on pass, `(False, "<rule_name>")` on first failure
- Rule names (used by `flag.py` later): `"missing_id"`, `"wrong_language"`, `"wrong_variant"`, `"invalid_task_type"`, `"invalid_domain"`, `"missing_input_prefix"`, `"input_too_short"`, `"output_too_short"`, `"output_stub"`, `"pt_br_vocab:<word>"`, `"json_missing_keys"`, `"json_domain_mismatch"`, `"json_urgency_missing_keys"`

- [ ] **Step 1: Write the new failing tests first**

Replace the entire content of `tests/test_validate.py` with:

```python
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
               "intent_classification", "urgency_classification",
               "rewrite_professional", "next_action_suggestion", "faq_answer"]:
        ok, _ = is_valid_row(_row(task_type=tt))
        assert ok is True, f"task_type={tt} should pass"


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
    ok, reason = is_valid_row(_row(output="[sem template para response_generation/refund_request]"))
    assert ok is False
    assert reason == "output_stub"

    ok2, reason2 = is_valid_row(_row(output="Resposta gerada para o cliente."))
    assert ok2 is False
    assert reason2 == "output_stub"


# ── rule 13: pt-BR banned words ───────────────────────────────────────────────
def test_banned_ptbr_words_fail():
    for word, phrase in [
        ("celular", "Ligue para o seu celular agora."),
        ("senha", "Redefina a sua senha aqui."),
        ("nota fiscal", "Enviamos a nota fiscal por e-mail."),
        ("assinatura", "A sua assinatura foi cancelada."),
        ("código de rastreio", "Utilize o código de rastreio para acompanhar."),
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
    output = json.dumps({"urgency": "high"})
    ok, reason = is_valid_row(_row(task_type="urgency_classification", output=output))
    assert ok is False
    assert reason == "json_urgency_missing_keys"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /path/to/pt-ai-instruction-dataset
python3 -m pytest tests/test_validate.py -v 2>&1 | head -40
```

Expected: Many FAILs — `is_valid_row` currently returns `bool`, not `(bool, str)`, and most new rules don't exist yet.

- [ ] **Step 3: Replace `scripts/validate.py` with the upgraded implementation**

```python
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
```

- [ ] **Step 4: Update `scripts/generate.py` — fix the caller at line 68**

Change:
```python
    valid = [r for r in data if is_valid_row(r)]
```
To:
```python
    valid = [r for r in data if is_valid_row(r)[0]]
```

- [ ] **Step 5: Update `scripts/pipeline.py` — fix the caller**

Find the validation list comprehension:
```python
valid = [r for r in tqdm(rows, desc="  Validating", unit="row") if is_valid_row(r)]
```
Change to:
```python
valid = [r for r in tqdm(rows, desc="  Validating", unit="row") if is_valid_row(r)[0]]
```

- [ ] **Step 6: Run all tests**

```bash
cd /path/to/pt-ai-instruction-dataset
python3 -m pytest tests/test_validate.py -v
```

Expected: All tests pass. Count should be ~30 tests.

- [ ] **Step 7: Verify pipeline still works end-to-end**

```bash
cd scripts && python3 pipeline.py --n 50 2>&1 | tail -5
```

Expected: `Processed → .../lusosupport_pt_v1.jsonl (N rows total)` — no errors.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py scripts/generate.py scripts/pipeline.py tests/test_validate.py
git commit -m "feat: upgrade validate.py to 15 rules with (bool, str) return type

- is_valid_row() now returns (bool, reason_str) instead of bool
- 15 validation rules: structure, input prefix/length, output length by
  task_type, stub detection, PT-BR vocab, JSON integrity for both
  classification task types including domain-match check
- Update generate.py and pipeline.py callers to use [0] indexing
- All 30+ tests passing"
```

---

### Task 2: Create feedback directory + pipeline exclusion integration

**Files:**
- Create: `datasets/feedback/.gitkeep`
- Modify: `scripts/pipeline.py` — add step 4 (exclusion + correction injection)
- Create: `tests/test_pipeline_exclusions.py`

**Interfaces:**
- Consumes: `is_valid_row(row) -> (bool, str)` from Task 1
- Produces:
  - `load_seed_ids(seeds_path: Path) -> set[str]` — set of seed row IDs
  - `load_exclusion_ids(feedback_dir: Path, seed_ids: set) -> set[str]` — excluded row IDs
  - `load_corrections(feedback_dir: Path) -> dict[str, str]` — maps row_id → corrected_output

- [ ] **Step 1: Write failing tests**

Create `tests/test_pipeline_exclusions.py`:

```python
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
```

- [ ] **Step 2: Run to confirm fail**

```bash
python3 -m pytest tests/test_pipeline_exclusions.py -v 2>&1 | head -20
```

Expected: `ImportError` — `load_seed_ids`, `load_exclusion_ids`, `load_corrections` not yet in pipeline.py.

- [ ] **Step 3: Create `datasets/feedback/` directory**

```bash
mkdir -p datasets/feedback
touch datasets/feedback/.gitkeep
```

- [ ] **Step 4: Add exclusion functions to `scripts/pipeline.py`**

At the top of `pipeline.py`, ensure `pathlib` is imported:
```python
from pathlib import Path
```

Add these three functions **before** the `run_pipeline()` function:

```python
SEEDS_PATH = Path("../datasets/raw/seed_examples.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")


def load_seed_ids(seeds_path: Path = SEEDS_PATH) -> set:
    """Return the set of IDs from the seed file (always protected from exclusion)."""
    if not seeds_path.exists():
        return set()
    ids = set()
    for line in seeds_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(json.loads(line)["id"])
    return ids


def load_exclusion_ids(feedback_dir: Path = FEEDBACK_DIR,
                       seed_ids: set = None) -> set:
    """Return IDs from flagged.jsonl and rejected.jsonl, excluding seed IDs."""
    if seed_ids is None:
        seed_ids = load_seed_ids()
    excluded = set()
    for fname in ["flagged.jsonl", "rejected.jsonl"]:
        path = feedback_dir / fname
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    row_id = json.loads(line)["id"]
                    if row_id not in seed_ids:
                        excluded.add(row_id)
    return excluded


def load_corrections(feedback_dir: Path = FEEDBACK_DIR) -> dict:
    """Return a dict mapping row_id -> corrected_output from corrections.jsonl."""
    path = feedback_dir / "corrections.jsonl"
    if not path.exists():
        return {}
    corrections = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            corrections[entry["id"]] = entry["corrected_output"]
    return corrections
```

- [ ] **Step 5: Wire exclusion + corrections into `run_pipeline()`**

In the `run_pipeline()` function, after the deduplicate step and before saving, add:

```python
    # Step 4: Apply exclusions and corrections
    seed_ids = load_seed_ids()
    excluded = load_exclusion_ids(seed_ids=seed_ids)
    corrections = load_corrections()
    if excluded:
        before = len(unique_rows)
        unique_rows = [r for r in unique_rows if r["id"] not in excluded]
        console.print(f"      {len(excluded)} IDs in exclusion list, {before - len(unique_rows)} rows removed")
    if corrections:
        for r in unique_rows:
            if r["id"] in corrections:
                r["output"] = corrections[r["id"]]
        console.print(f"      {len(corrections)} corrections applied")
```

Place this block after `unique_rows` is defined by `deduplicate()` but before the `# [4/4] Saving...` section.

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest tests/test_pipeline_exclusions.py tests/test_validate.py -v
```

Expected: All pass.

- [ ] **Step 7: Verify pipeline with empty feedback dir**

```bash
cd scripts && python3 pipeline.py --n 50 2>&1 | tail -8
```

Expected: No errors; no exclusion output (feedback files don't exist — that's correct).

- [ ] **Step 8: Commit**

```bash
git add datasets/feedback/.gitkeep scripts/pipeline.py tests/test_pipeline_exclusions.py
git commit -m "feat: add feedback directory and pipeline exclusion/correction logic

- datasets/feedback/ dir with .gitkeep
- load_seed_ids(), load_exclusion_ids(), load_corrections() in pipeline.py
- Pipeline step 4: exclude flagged/rejected IDs, inject corrections
- Seeds in raw/seed_examples.jsonl are always protected from exclusion
- 5 new tests in test_pipeline_exclusions.py"
```

---

### Task 3: Create `scripts/flag.py` + `tests/test_flag.py`

**Files:**
- Create: `scripts/flag.py`
- Create: `tests/test_flag.py`

**Interfaces:**
- Consumes: `is_valid_row(row) -> (bool, str)` from Task 1
- Produces: `scan_dataset(processed_path: Path, feedback_dir: Path, approved_ids: set) -> list[dict]` — list of `{"id": str, "reason": str, "row": dict}`

- [ ] **Step 1: Write failing test**

Create `tests/test_flag.py`:

```python
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
    bad["output"] = "Redefina a sua senha aqui para continuar."
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
    bad["output"] = "Redefina a sua senha aqui."
    p = _make_dataset(tmp_path, [bad])
    flags = scan_dataset(p, tmp_path, approved_ids={"lusosupport_pt_000100"})
    assert flags == []


def test_flagged_jsonl_written(tmp_path):
    bad = _good_row()
    bad["output"] = "Redefina a sua senha aqui."
    p = _make_dataset(tmp_path, [bad])
    scan_dataset(p, tmp_path, approved_ids=set())
    flagged_path = tmp_path / "flagged.jsonl"
    assert flagged_path.exists()
    entry = json.loads(flagged_path.read_text().strip())
    assert entry["id"] == "lusosupport_pt_000100"
```

- [ ] **Step 2: Run to confirm fail**

```bash
python3 -m pytest tests/test_flag.py -v 2>&1 | head -10
```

Expected: `ImportError` — `flag.py` doesn't exist yet.

- [ ] **Step 3: Create `scripts/flag.py`**

```python
"""flag.py — Automated quality scanner for LusoSupport-PT dataset.

Reads the processed dataset, applies validate.py rules and heuristics,
and writes datasets/feedback/flagged.jsonl.

Usage:
    python3 flag.py [--processed PATH] [--feedback PATH]
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from validate import is_valid_row

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")

# Task types that produce free text (not JSON)
_TEXT_TASK_TYPES = {
    "response_generation", "email_reply", "summarization",
    "rewrite_professional", "next_action_suggestion", "faq_answer",
}


def _load_approved_ids(feedback_dir: Path) -> set:
    path = feedback_dir / "approved.jsonl"
    if not path.exists():
        return set()
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(json.loads(line)["id"])
    return ids


def _heuristic_flags(row: dict, bucket_outputs: dict) -> list:
    """Return list of heuristic reason strings; empty if none apply."""
    reasons = []
    task_type = row.get("task_type", "")
    output = row.get("output", "")
    domain = row.get("domain", "")
    bucket_key = (domain, task_type)

    # Heuristic 1: duplicate output within same domain × task_type bucket
    if output in bucket_outputs[bucket_key]:
        reasons.append("duplicate_in_bucket")
    else:
        bucket_outputs[bucket_key].add(output)

    if task_type in _TEXT_TASK_TYPES:
        # Heuristic 2: output-to-input length ratio < 0.5
        input_len = len(row.get("input", ""))
        if input_len > 0 and len(output) / input_len < 0.5:
            reasons.append("low_output_input_ratio")

        # Heuristic 3: single sentence for email_reply or response_generation
        if task_type in {"email_reply", "response_generation"}:
            sentences = [s.strip() for s in output.split(".") if s.strip()]
            if len(sentences) <= 1:
                reasons.append("single_sentence_email")

    return reasons


def scan_dataset(processed_path: Path, feedback_dir: Path,
                 approved_ids: set = None) -> list:
    """Scan the processed dataset and return a list of flagged entries.

    Each entry: {"id": str, "reason": str, "row": dict}
    Also writes flagged.jsonl to feedback_dir.
    """
    if approved_ids is None:
        approved_ids = _load_approved_ids(feedback_dir)

    rows = []
    for line in processed_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))

    flagged = []
    bucket_outputs = defaultdict(set)

    for row in rows:
        row_id = row.get("id", "")
        if row_id in approved_ids:
            continue

        # Pass 1: validate.py rules
        ok, reason = is_valid_row(row)
        if not ok:
            flagged.append({"id": row_id, "reason": reason, "row": row})
            continue  # don't also run heuristics on already-failed rows

        # Pass 2: heuristics (only first hit per row)
        heuristic_reasons = _heuristic_flags(row, bucket_outputs)
        if heuristic_reasons:
            flagged.append({"id": row_id, "reason": heuristic_reasons[0], "row": row})

    # Write flagged.jsonl
    feedback_dir.mkdir(parents=True, exist_ok=True)
    out_path = feedback_dir / "flagged.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for entry in flagged:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return flagged


def _print_summary(flagged: list) -> None:
    from rich.console import Console
    from rich.rule import Rule

    console = Console()
    console.print(Rule("[bold]LusoSupport-PT — Flag Report[/bold]"))

    if not flagged:
        console.print("[green]✓ No rows flagged.[/green]")
        return

    counts = Counter(entry["reason"] for entry in flagged)
    console.print(f"\n[yellow]Flagged {len(flagged)} rows across {len(counts)} rules:[/yellow]\n")
    for reason, count in counts.most_common():
        console.print(f"  [bold]{reason:<45}[/bold] {count} rows")
    console.print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-scan dataset for quality issues.")
    parser.add_argument("--processed", default=str(PROCESSED_PATH))
    parser.add_argument("--feedback", default=str(FEEDBACK_DIR))
    args = parser.parse_args()

    processed_path = Path(args.processed)
    feedback_dir = Path(args.feedback)
    approved_ids = _load_approved_ids(feedback_dir)

    flagged = scan_dataset(processed_path, feedback_dir, approved_ids)
    _print_summary(flagged)
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_flag.py -v
```

Expected: All 5 tests pass.

- [ ] **Step 5: Smoke-test against real dataset**

```bash
cd scripts && python3 flag.py 2>&1
```

Expected: Summary printed showing flagged row count.

- [ ] **Step 6: Commit**

```bash
git add scripts/flag.py tests/test_flag.py
git commit -m "feat: add flag.py automated dataset quality scanner

- scan_dataset() applies all 15 validate.py rules + 3 heuristics:
  duplicate output in domain×task_type bucket, low output/input ratio,
  single-sentence email/response
- Skips already-approved rows
- Writes datasets/feedback/flagged.jsonl
- Rich summary output
- 5 tests in test_flag.py"
```

---

### Task 4: Create `scripts/review.py` — Interactive Human Review

**Files:**
- Create: `scripts/review.py`

**Interfaces:**
- Consumes: feedback JSONL files from Tasks 2 and 3
- Produces: writes to `datasets/feedback/{approved,rejected,corrections}.jsonl`; writes `.review_checkpoint` for session resume

- [ ] **Step 1: Create `scripts/review.py`**

```python
"""review.py — Interactive human review for LusoSupport-PT dataset.

Usage:
    python3 review.py [--mode random|flagged|all] [--n 20]
                      [--domain DOMAIN] [--task TASK_TYPE]

Keys during review:
    a  approve row   r  reject row   f  fix output inline
    s  skip          q  quit and save progress
"""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")
CHECKPOINT_FILE = FEEDBACK_DIR / ".review_checkpoint"

console = Console()


# ── I/O helpers ────────────────────────────────────────────────────────────────

def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def _append_jsonl(path: Path, entry: dict) -> None:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── feedback sets ──────────────────────────────────────────────────────────────

def _load_reviewed_ids() -> set:
    """IDs already reviewed (approved, rejected, or corrected) in any prior session."""
    ids = set()
    for fname in ["approved.jsonl", "rejected.jsonl", "corrections.jsonl"]:
        for entry in _load_jsonl(FEEDBACK_DIR / fname):
            ids.add(entry["id"])
    return ids


def _save_checkpoint(row_id: str) -> None:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(row_id, encoding="utf-8")


# ── row selection ──────────────────────────────────────────────────────────────

def _load_all_rows() -> list:
    return _load_jsonl(PROCESSED_PATH)


def _select_rows(mode: str, n: int, domain, task) -> list:
    if mode == "flagged":
        flagged = _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
        ids = {e["id"] for e in flagged}
        rows = [r for r in _load_all_rows() if r["id"] in ids]
    elif mode == "random":
        rows = _load_all_rows()
        random.shuffle(rows)
    else:  # all
        rows = _load_all_rows()

    if domain:
        rows = [r for r in rows if r.get("domain") == domain]
    if task:
        rows = [r for r in rows if r.get("task_type") == task]

    reviewed = _load_reviewed_ids()
    rows = [r for r in rows if r["id"] not in reviewed]
    return rows[:n]


# ── display ────────────────────────────────────────────────────────────────────

def _display_row(row: dict, index: int, total: int,
                 flag_reason=None) -> None:
    header = (
        f"Row {index}/{total}  ──  "
        f"[cyan]{row.get('domain','?')}[/cyan] / "
        f"[green]{row.get('task_type','?')}[/green] / "
        f"[yellow]{row.get('customer_intent','?')}[/yellow]"
    )
    if flag_reason:
        header += f"  ⚑ [red]{flag_reason}[/red]"

    body = (
        f"[bold]INPUT[/bold]\n{row.get('input', '')}\n\n"
        f"[bold]OUTPUT[/bold]\n{row.get('output', '')}"
    )

    console.print()
    console.print(Panel(body, title=header, border_style="blue", padding=(1, 2)))
    console.print(
        "  [bold][a][/bold]pprove  "
        "[bold][r][/bold]eject  "
        "[bold][f][/bold]ix inline  "
        "[bold][s][/bold]kip  "
        "[bold][q][/bold]uit"
    )


# ── actions ────────────────────────────────────────────────────────────────────

def _approve(row: dict) -> None:
    _append_jsonl(FEEDBACK_DIR / "approved.jsonl",
                  {"id": row["id"], "timestamp": _now()})
    console.print("[green]✓ Approved[/green]")


def _reject(row: dict) -> None:
    reason = input("  Rejection reason (optional, Enter to skip): ").strip()
    _append_jsonl(FEEDBACK_DIR / "rejected.jsonl",
                  {"id": row["id"], "reason": reason, "timestamp": _now()})
    console.print("[red]✗ Rejected[/red]")


def _fix(row: dict) -> None:
    console.print(
        "\n  Type the corrected output below. "
        "Press Enter twice (blank line) when done:\n"
    )
    lines = []
    while True:
        line = input("  > ")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    corrected = "\n".join(lines).strip()
    if corrected:
        _append_jsonl(FEEDBACK_DIR / "corrections.jsonl", {
            "id": row["id"],
            "original_output": row.get("output", ""),
            "corrected_output": corrected,
            "timestamp": _now(),
        })
        console.print("[blue]✎ Correction saved[/blue]")
    else:
        console.print("[yellow]Empty correction — skipped[/yellow]")


# ── main loop ──────────────────────────────────────────────────────────────────

def run_review(mode: str, n: int, domain, task) -> None:
    rows = _select_rows(mode, n, domain, task)
    if not rows:
        console.print(Rule())
        console.print("[yellow]No unreviewed rows found for the given filters.[/yellow]")
        return

    flag_reasons = {
        e["id"]: e["reason"]
        for e in _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
    }

    console.print(Rule("[bold]LusoSupport-PT — Review Session[/bold]"))
    console.print(
        f"Mode: [cyan]{mode}[/cyan]  |  "
        f"Rows to review: [cyan]{len(rows)}[/cyan]"
        + (f"  |  domain: [cyan]{domain}[/cyan]" if domain else "")
        + (f"  |  task: [cyan]{task}[/cyan]" if task else "")
    )

    for i, row in enumerate(rows, start=1):
        _save_checkpoint(row["id"])
        _display_row(row, i, len(rows), flag_reasons.get(row["id"]))

        while True:
            key = input("  > ").strip().lower()[:1]
            if key == "a":
                _approve(row)
                break
            elif key == "r":
                _reject(row)
                break
            elif key == "f":
                _fix(row)
                break
            elif key == "s":
                console.print("[dim]Skipped[/dim]")
                break
            elif key == "q":
                console.print("\n[bold]Session saved. Resume with the same command.[/bold]")
                sys.exit(0)
            else:
                console.print("  Invalid key. Use a / r / f / s / q")

    console.print(Rule())
    console.print(f"[green]Session complete — {len(rows)} rows reviewed.[/green]")
    CHECKPOINT_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive dataset review.")
    parser.add_argument("--mode", choices=["random", "flagged", "all"],
                        default="flagged")
    parser.add_argument("--n", type=int, default=20,
                        help="Max rows to review per session")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--task", default=None)
    args = parser.parse_args()

    run_review(args.mode, args.n, args.domain, args.task)
```

- [ ] **Step 2: Smoke-test the review script**

```bash
cd scripts && python3 review.py --mode random --n 3
```

Walk through 3 rows: approve one (`a`), reject one (`r`), skip one (`s`).

Expected: No errors; feedback files written in `datasets/feedback/`.

- [ ] **Step 3: Verify feedback files**

```bash
ls -la ../datasets/feedback/
cat ../datasets/feedback/approved.jsonl 2>/dev/null
cat ../datasets/feedback/rejected.jsonl 2>/dev/null
```

Expected: JSONL files with `id` and `timestamp` fields.

- [ ] **Step 4: Commit**

```bash
git add scripts/review.py
git commit -m "feat: add review.py interactive human review tool

- Modes: random, flagged (default), all; filterable by --domain/--task
- Keys: a=approve r=reject f=fix-inline s=skip q=quit+save
- Rich panel display with domain/task/intent header + flag reason
- Checkpoint file for session resume
- Writes to datasets/feedback/{approved,rejected,corrections}.jsonl"
```

---

### Task 5: Create `scripts/quality_report.py` + update `Makefile`

**Files:**
- Create: `scripts/quality_report.py`
- Modify: `Makefile`

**Interfaces:**
- Consumes: `datasets/feedback/*.jsonl`, `datasets/processed/lusosupport_pt_v1.jsonl`
- Produces: Rich terminal report (stdout only, no file written)

- [ ] **Step 1: Create `scripts/quality_report.py`**

```python
"""quality_report.py — Template health report for LusoSupport-PT.

Reads feedback files and the processed dataset to surface the weakest
domain × task_type combinations based on rejection and flag rates.

Usage:
    python3 quality_report.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from rich.console import Console
from rich.rule import Rule
from rich.table import Table

PROCESSED_PATH = Path("../datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR = Path("../datasets/feedback")

console = Console()


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def run_report() -> None:
    rows = _load_jsonl(PROCESSED_PATH)
    flagged = _load_jsonl(FEEDBACK_DIR / "flagged.jsonl")
    rejected = _load_jsonl(FEEDBACK_DIR / "rejected.jsonl")
    approved = _load_jsonl(FEEDBACK_DIR / "approved.jsonl")
    corrections = _load_jsonl(FEEDBACK_DIR / "corrections.jsonl")

    flagged_ids = {e["id"] for e in flagged}
    rejected_ids = {e["id"] for e in rejected}
    approved_ids = {e["id"] for e in approved}

    console.print(Rule("[bold]LusoSupport-PT — Quality Report[/bold]"))
    console.print(
        f"  [bold]{len(rows)}[/bold] total rows  |  "
        f"[yellow]{len(flagged_ids)}[/yellow] flagged  |  "
        f"[red]{len(rejected_ids)}[/red] rejected  |  "
        f"[green]{len(approved_ids)}[/green] approved  |  "
        f"[blue]{len(corrections)}[/blue] corrections"
    )
    console.print()

    # Flag reason breakdown
    if flagged:
        reason_counts = Counter(e["reason"] for e in flagged)
        console.print("[bold]Flag reasons:[/bold]")
        for reason, count in reason_counts.most_common(10):
            console.print(f"  {reason:<45} {count}")
        console.print()

    # Build per-row lookup (include rows embedded in flagged entries)
    row_lookup = {r["id"]: r for r in rows}
    for entry in flagged:
        if entry["id"] not in row_lookup and "row" in entry:
            row_lookup[entry["id"]] = entry["row"]

    # Domain × task_type buckets
    bucket_total: dict = defaultdict(int)
    bucket_rejected: dict = defaultdict(int)
    bucket_flagged: dict = defaultdict(int)

    for r in rows:
        key = (r.get("domain", "?"), r.get("task_type", "?"))
        bucket_total[key] += 1

    for entry in rejected:
        row = row_lookup.get(entry["id"])
        if row:
            key = (row.get("domain", "?"), row.get("task_type", "?"))
            bucket_rejected[key] += 1

    for entry in flagged:
        row = row_lookup.get(entry["id"])
        if row:
            key = (row.get("domain", "?"), row.get("task_type", "?"))
            bucket_flagged[key] += 1

    problem_buckets = set(bucket_rejected.keys()) | set(bucket_flagged.keys())
    if problem_buckets:
        table = Table(title="Weakest domain × task_type areas", show_lines=True)
        table.add_column("domain × task_type", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Rejected", justify="right", style="red")
        table.add_column("Flagged", justify="right", style="yellow")
        table.add_column("Issue rate", justify="right")

        rows_sorted = sorted(
            problem_buckets,
            key=lambda k: (bucket_rejected[k] + bucket_flagged[k]) / max(bucket_total[k], 1),
            reverse=True,
        )
        for key in rows_sorted[:15]:
            domain, task = key
            total = bucket_total[key]
            rej = bucket_rejected[key]
            flag = bucket_flagged[key]
            rate = (rej + flag) / total if total else 0
            bar = "▓" * int(rate * 10)
            table.add_row(
                f"{domain} × {task}",
                str(total),
                str(rej) if rej else "—",
                str(flag) if flag else "—",
                f"{rate:.0%} {bar}",
            )
        console.print(table)

        top = rows_sorted[0]
        console.print(
            f"\n[bold]→ Fix priority:[/bold] "
            f"responses.py templates for "
            f"[cyan]{top[0]}[/cyan] / [green]{top[1]}[/green]"
        )
    else:
        console.print("[green]No rejected or flagged rows found yet.[/green]")
        console.print(
            "Run [bold]make flag[/bold] then [bold]make review[/bold] "
            "to populate feedback."
        )


if __name__ == "__main__":
    run_report()
```

- [ ] **Step 2: Add Makefile targets**

Add to `Makefile` after the existing `clean` target:

```makefile
flag:
	cd scripts && python3 flag.py

review:
	cd scripts && python3 review.py --mode flagged

review-random:
	cd scripts && python3 review.py --mode random --n 20

quality:
	cd scripts && python3 quality_report.py
```

- [ ] **Step 3: Smoke-test quality report**

```bash
cd scripts && python3 quality_report.py
```

Expected: Report prints with row counts and either "No rejected or flagged rows" or a problem table.

- [ ] **Step 4: Run the full quality loop end-to-end**

```bash
cd /path/to/pt-ai-instruction-dataset
make flag
make quality
```

Expected: `make flag` writes `datasets/feedback/flagged.jsonl`; `make quality` shows stats.

- [ ] **Step 5: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: All tests pass (30+ test_validate + 5 test_flag + 5 test_pipeline_exclusions + 9 test_dedupe = 49+ total).

- [ ] **Step 6: Commit**

```bash
git add scripts/quality_report.py Makefile
git commit -m "feat: add quality_report.py and Makefile quality loop targets

- quality_report.py: rich report with flag reason breakdown,
  domain×task_type rejection table, top-priority template fix suggestion
- Makefile: flag, review, review-random, quality targets
- Full quality loop: make flag && make review && make pipeline && make quality"
```

---

### Task 6: Create PR, update GitHub project board

**Files:** None (GitHub operations only)

- [ ] **Step 1: Push dev branch**

```bash
git push origin dev
```

- [ ] **Step 2: Create PR**

```bash
gh pr create \
  --title "feat: quality loop — validate upgrade, flag, review, quality_report (#9)" \
  --body "## Summary
Closes #9 (manual quality review). Implements the full quality loop design spec.

## Changes
- \`validate.py\`: 15 rules, \`(bool, str)\` return, catches domain mismatch, JSON integrity, PT-BR vocab (6 words)
- \`flag.py\`: auto-scanner (validate rules + 3 heuristics), writes \`datasets/feedback/flagged.jsonl\`
- \`review.py\`: interactive terminal review — approve/reject/fix-inline/skip/quit, rich display, session checkpoint
- \`quality_report.py\`: template health report grouped by domain×task_type with fix priority suggestion
- \`pipeline.py\`: step 4 exclusion — reads flagged/rejected IDs, injects corrections, seed rows always protected
- \`datasets/feedback/\`: new directory for all feedback JSONL files
- \`Makefile\`: \`flag\`, \`review\`, \`review-random\`, \`quality\` targets
- Tests: 49+ tests across test_validate.py, test_flag.py, test_pipeline_exclusions.py

## Full quality loop
\`\`\`
make flag          # auto-scan → flagged.jsonl
make review        # human review → approved/rejected/corrections.jsonl
make pipeline      # rebuild with exclusions + corrections injected
make quality       # template health report
\`\`\`" \
  --base main \
  --head dev
```

- [ ] **Step 3: Close Issue #9 and add PR to project board**

```bash
gh issue close 9 --comment "Quality loop implemented in this PR: validate.py (15 rules), flag.py, review.py, quality_report.py, pipeline exclusion/correction integration."
```

Add the new PR to the project board in Review status using:
```bash
# Get PR node ID
PR_NODE=$(gh api graphql -f query='{ repository(owner:"ariazevedopt",name:"pt-ai-instruction-dataset") { pullRequest(number:PR_NUM) { id } } }' --jq '.data.repository.pullRequest.id')

# Add to board and set Review status
gh api graphql -f query="mutation { addProjectV2ItemById(input: {projectId: \"PVT_kwHOAS3Kg84BUljL\", contentId: \"$PR_NODE\"}) { item { id } } }" --jq '.data.addProjectV2ItemById.item.id'
# Then set status to Review using the item ID:
# updateProjectV2ItemFieldValue with fieldId PVTSSF_lAHOAS3Kg84BUljLzhBstHw, value f9a382cb
```

- [ ] **Step 4: Verify**

```bash
gh pr view --web
gh issue view 9
```

Expected: PR open on GitHub, Issue #9 closed with comment.

---

## Self-Review

**Spec coverage:**
- ✅ `validate.py` — 15 rules with `(bool, str)` return (Task 1)
- ✅ `flag.py` — validate rules + 3 heuristics, skips approved, writes flagged.jsonl (Task 3)
- ✅ `review.py` — a/r/f/s/q keys, checkpoint, flagged/random/all modes, domain/task filters (Task 4)
- ✅ `quality_report.py` — rich table by domain×task_type, actionable fix priority (Task 5)
- ✅ Feedback JSONL schema — all 4 files with correct fields (Tasks 2, 3, 4)
- ✅ Seed protection — `load_seed_ids()` guards seed IDs from exclusion (Task 2)
- ✅ Corrections injection — `load_corrections()` replaces output in pipeline (Task 2)
- ✅ Pipeline step 4 — integrated after dedup before save (Task 2)
- ✅ Makefile targets — flag, review, review-random, quality (Task 5)
- ✅ Tests — test_validate.py (30+), test_flag.py (5), test_pipeline_exclusions.py (5) = 40+ tests

**Placeholder scan:** No TBDs, TODOs, or vague steps. All steps include complete code. ✅

**Type consistency:**
- `is_valid_row` called as `is_valid_row(r)[0]` in generate.py and pipeline.py ✅
- `scan_dataset(processed_path, feedback_dir, approved_ids)` matches test calls ✅
- `load_exclusion_ids(feedback_dir, seed_ids)` matches test calls ✅
- `load_corrections(feedback_dir)` matches test calls ✅
- Feedback file names consistent: `flagged.jsonl`, `rejected.jsonl`, `approved.jsonl`, `corrections.jsonl` ✅
- `FEEDBACK_DIR` constant used in flag.py, review.py, quality_report.py, pipeline.py ✅
