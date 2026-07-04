# Browser Review UI — Design Spec

**Date:** 2026-07-04  
**Status:** Approved  
**Purpose:** Provide a browser-based tool to review dataset rows and classify them as Good / Unclear / Bad, complementing the existing terminal `review.py` tool.

---

## Goals

1. Let the user browse existing dataset rows and rate them without touching the terminal.
2. Let the user type a free-form customer message, select domain/task_type/intent, and see a generated output to rate.
3. Persist ratings back to the feedback pipeline (`approved.jsonl`, `rejected.jsonl`, `browser_ratings.jsonl`).
4. Allow one-click export of browser ratings as JSON.
5. Zero new dependencies — stdlib only.

---

## Architecture

### Server: `scripts/review_server.py`

Single-file Python HTTP server using `http.server.BaseHTTPRequestHandler`. The HTML/CSS/JS UI is embedded as a string constant and served inline (no separate template files).

**Runs from the project root** (`python3 scripts/review_server.py`), so relative paths (`../datasets/…`) resolve correctly.

**CLI flags:**
- `--port N` (default: 8765)
- `--open` (opens browser tab on start)
- `--mode random|flagged|all` (default: random — controls Browse tab default mode)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serves the full UI (HTML+CSS+JS string) |
| GET | `/api/options` | Returns `{domains, task_types, intents}` arrays for dropdowns |
| GET | `/api/sample?mode=random\|flagged` | Returns one unreviewed row as JSON; skips rows already in approved/rejected/browser_ratings |
| GET | `/api/generate?domain=…&task_type=…&intent=…&message=…` | Builds a row using provided message as input, calls `get_output(task_type, intent, domain)` for output; returns row JSON |
| POST | `/api/rate` | Body: `{id, rating, comment, row}`. Writes to feedback files. Returns `{ok: true}` |
| GET | `/api/export` | Streams `datasets/feedback/browser_ratings.jsonl` as a file download (`Content-Disposition: attachment`) |
| GET | `/api/stats` | Returns `{total_rows, rated_session, approved_total, rejected_total, unclear_total}` |

### Feedback file mapping

| Rating | File |
|--------|------|
| Good | `datasets/feedback/approved.jsonl` — `{id, timestamp}` |
| Bad | `datasets/feedback/rejected.jsonl` — `{id, reason: comment_or_"browser:bad", timestamp}` |
| Unclear | `datasets/feedback/browser_ratings.jsonl` — `{id, rating: "unclear", comment, timestamp, row}` |

`browser_ratings.jsonl` is a new file. It does **not** affect `make pipeline` (which reads only `rejected.jsonl` and `flagged.jsonl`). Its purpose is human review logging and export.

### Already-reviewed detection

`/api/sample` loads IDs from all three files (approved + rejected + browser_ratings) and excludes them from sampling. Seeds (IDs from `seed_examples.jsonl`) are eligible for review — they can receive ratings too.

---

## UI

### Layout

Single-page app, two tabs: **Browse** and **Generate**.

**Header** (always visible):
- Title: "LusoSupport-PT · Browser Review"
- Session counter: "N rated this session"
- Export button → triggers `/api/export`

### Browse Tab

Shows one dataset row at a time.

**Row card** displays:
- Metadata bar: `domain · task_type · intent · tone`
- **INSTRUCTION** block
- **INPUT** block (customer message)
- **OUTPUT** block (agent response — most important to rate)

**Controls below card:**
- ✅ **Good** (green) — correct PT-PT, on-topic, well-formed
- ❓ **Unclear** (yellow) — ambiguous, borderline, needs human review
- ❌ **Bad** (red) — wrong domain/intent, bad PT-PT, stub output
- Optional comment textarea (shown after clicking any rating, before confirming)
- **Skip** (grey) — advances to next row without rating
- Mode toggle: Random / Flagged

After rating or skipping → auto-loads next row.

### Generate Tab

**Form fields:**
- Customer message — free-form `<textarea>` (placeholder: "Escreve aqui a mensagem do cliente…")
- Domain — `<select>` (all 8 domains)
- Task type — `<select>` (all 8 task types)
- Intent — `<select>` (all 18 intents)
- **Generate** button

**Result card** (same layout as Browse tab row card) appears below the form after generation. The same Good / Unclear / Bad controls appear, plus a **Reset** button to clear the form.

Generated rows get a synthetic ID: `browser_generated_<timestamp>` so they can be tracked in browser_ratings.jsonl.

---

## Makefile Target

```makefile
review-browser:
    @echo "Starting browser review at http://localhost:8765 ..."
    cd scripts && python3 review_server.py --port 8765 --open
```

Placed after the existing `quality` target.

---

## Guide: `docs/browser-review-guide.md`

Short guide covering:
1. How to start: `make review-browser`
2. Browse tab workflow (rate rows, skip, export)
3. Generate tab workflow (type message, pick options, rate result)
4. Where ratings go (approved/rejected/browser_ratings files)
5. How to feed results into the pipeline: after rating, run `make flag && make pipeline`
6. How to export: click Export in the header → downloads `browser_ratings.jsonl`

---

## Out of Scope

- Authentication / multi-user support
- Persistent session state across server restarts (beyond what's written to feedback files)
- Editing row fields in the browser (use terminal `review.py --mode flagged` for fixes)
- Any dependencies beyond Python stdlib + existing project scripts
