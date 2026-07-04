#!/usr/bin/env python3
"""Browser-based dataset review server for LusoSupport-PT.

Serves a self-contained HTML UI at GET / and provides JSON API endpoints
for sampling rows, generating new rows, rating rows, and exporting ratings.

Run from the project root:
    python3 scripts/review_server.py [--port 8765] [--open]
"""
import json
import os
import random
import sys
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

# Resolve project root and add scripts to sys.path when imported as module
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from config import DOMAINS, TASK_TYPES, CUSTOMER_INTENTS
from responses import get_output
from templates import build_instruction

# ---------------------------------------------------------------------------
# Paths (relative to project root — server chdirs to root on startup)
# ---------------------------------------------------------------------------

PROCESSED_PATH = Path("datasets/processed/lusosupport_pt_v1.jsonl")
FEEDBACK_DIR   = Path("datasets/feedback")
SEEDS_PATH     = Path("datasets/raw/seed_examples.jsonl")


# ---------------------------------------------------------------------------
# Helper functions (importable for tests)
# ---------------------------------------------------------------------------

def load_rows(path: Path = PROCESSED_PATH) -> list:
    """Return all rows from a JSONL file. Returns [] if file is missing."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_reviewed_ids(feedback_dir: Path = FEEDBACK_DIR) -> set:
    """Return set of row IDs already present in approved, rejected, or browser_ratings."""
    ids = set()
    for fname in ("approved.jsonl", "rejected.jsonl", "browser_ratings.jsonl"):
        p = feedback_dir / fname
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    if "id" in entry:
                        ids.add(entry["id"])
    return ids


def sample_row(rows: list, reviewed_ids: set, mode: str = "random",
               feedback_dir: Path = FEEDBACK_DIR) -> Optional[dict]:
    """Return one unreviewed row. mode='flagged' restricts to flagged.jsonl IDs."""
    if mode == "flagged":
        flagged_path = feedback_dir / "flagged.jsonl"
        flagged_ids: set = set()
        if flagged_path.exists():
            for line in flagged_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    flagged_ids.add(json.loads(line)["id"])
        candidates = [r for r in rows if r["id"] in flagged_ids and r["id"] not in reviewed_ids]
    else:
        candidates = [r for r in rows if r["id"] not in reviewed_ids]
    return random.choice(candidates) if candidates else None


def build_generated_row(domain: str, task_type: str, intent: str, message: str) -> dict:
    """Build a synthetic row from user-supplied parameters."""
    ts_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "id": f"browser_generated_{ts_ms}",
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "subdomain": "placeholder",
        "task_type": task_type,
        "customer_intent": intent,
        "customer_tone": "formal",
        "agent_tone": "professional",
        "channel": "web_form",
        "difficulty": "medium",
        "instruction": build_instruction(task_type, "professional"),
        "input": f"Mensagem do cliente: {message}",
        "output": get_output(task_type, intent, domain=domain),
        "metadata": {
            "requires_escalation": False,
            "contains_pii": False,
            "synthetic": True,
            "source_type": "browser_generated",
        },
    }


def rate_row(row_id: str, rating: str, comment: str, row: dict,
             feedback_dir: Path = FEEDBACK_DIR) -> None:
    """Append rating to the appropriate feedback JSONL file."""
    feedback_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    if rating == "good":
        entry = {"id": row_id, "timestamp": ts}
        path = feedback_dir / "approved.jsonl"
    elif rating == "bad":
        entry = {"id": row_id, "reason": comment if comment else "browser:bad", "timestamp": ts}
        path = feedback_dir / "rejected.jsonl"
    else:  # unclear
        entry = {"id": row_id, "rating": "unclear", "comment": comment, "timestamp": ts, "row": row}
        path = feedback_dir / "browser_ratings.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Embedded HTML/CSS/JS UI
# ---------------------------------------------------------------------------

_HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LusoSupport-PT · Browser Review</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333;min-height:100vh}
.header{background:#1a1a2e;color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}
.header h1{font-size:1.1rem;font-weight:600}
.header .right{display:flex;gap:12px;align-items:center;font-size:.875rem}
.btn-export{background:#22c55e;color:#fff;border:none;padding:7px 16px;border-radius:6px;cursor:pointer;font-size:.875rem;font-weight:500}
.btn-export:hover{background:#16a34a}
.tabs{background:#fff;border-bottom:2px solid #e5e7eb;padding:0 24px;display:flex}
.tab{padding:12px 20px;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-2px;font-weight:500;color:#6b7280;font-size:.9rem;transition:color .15s}
.tab.active{border-bottom-color:#1a1a2e;color:#1a1a2e}
.main{max-width:820px;margin:24px auto;padding:0 16px}
.mode-bar{display:flex;gap:8px;margin-bottom:16px}
.btn-mode{padding:5px 14px;border:1px solid #d1d5db;border-radius:20px;background:#fff;cursor:pointer;font-size:.8rem;color:#6b7280}
.btn-mode.active{background:#1a1a2e;color:#fff;border-color:#1a1a2e}
.card{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1);overflow:hidden;margin-bottom:16px}
.card-meta{background:#f8fafc;padding:10px 20px;font-size:.8rem;color:#6b7280;display:flex;gap:12px;flex-wrap:wrap;border-bottom:1px solid #f1f5f9}
.meta-label{font-weight:600;color:#374151}
.card-body{padding:20px;display:flex;flex-direction:column;gap:14px}
.field-label{font-size:.7rem;font-weight:700;text-transform:uppercase;color:#9ca3af;margin-bottom:5px;letter-spacing:.06em}
.field-value{background:#f8fafc;border-radius:8px;padding:11px 14px;font-size:.9rem;line-height:1.65;white-space:pre-wrap;word-break:break-word;border:1px solid #f1f5f9}
.field-value.output{border-left:4px solid #1a1a2e}
.rating-area{padding:14px 20px;border-top:1px solid #f1f5f9;display:flex;flex-direction:column;gap:10px}
.rating-btns{display:flex;gap:8px;flex-wrap:wrap}
.btn-rate{flex:1;min-width:110px;padding:11px 8px;border:2px solid transparent;border-radius:8px;font-size:.9rem;font-weight:600;cursor:pointer;transition:all .15s}
.btn-good{background:#f0fdf4;color:#15803d;border-color:#bbf7d0}
.btn-good:hover,.btn-good.sel{background:#22c55e;color:#fff;border-color:#22c55e}
.btn-unclear{background:#fefce8;color:#a16207;border-color:#fef08a}
.btn-unclear:hover,.btn-unclear.sel{background:#eab308;color:#fff;border-color:#eab308}
.btn-bad{background:#fff1f2;color:#be123c;border-color:#fecdd3}
.btn-bad:hover,.btn-bad.sel{background:#f43f5e;color:#fff;border-color:#f43f5e}
.btn-skip{background:#f9fafb;color:#6b7280;border-color:#e5e7eb;padding:11px 20px;flex:0}
.btn-skip:hover{background:#f3f4f6}
.comment-row{display:none;gap:8px;align-items:flex-start}
.comment-row.show{display:flex}
.comment-row textarea{flex:1;padding:8px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:.875rem;resize:none;height:60px;font-family:inherit}
.btn-confirm{padding:8px 20px;background:#1a1a2e;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.875rem;font-weight:500;white-space:nowrap}
.gen-form{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1);padding:20px;margin-bottom:16px}
.form-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px}
.form-full{grid-column:1/-1}
.form-group label{display:block;font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:#6b7280;margin-bottom:5px}
.form-group select,.form-group textarea{width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:.875rem;font-family:inherit}
.btn-generate{background:#1a1a2e;color:#fff;border:none;padding:9px 28px;border-radius:6px;font-size:.9rem;font-weight:600;cursor:pointer}
.btn-generate:hover{background:#2d2d4a}
.btn-reset{background:#f3f4f6;color:#374151;border:1px solid #d1d5db;padding:9px 20px;border-radius:6px;font-size:.9rem;cursor:pointer;margin-left:8px}
.empty,.loading{text-align:center;padding:56px 24px;color:#9ca3af;background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1)}
.empty h3{font-size:1.1rem;margin-bottom:6px;color:#6b7280}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:600;background:#e0e7ff;color:#3730a3;margin-left:4px}
</style>
</head>
<body>
<div class="header">
  <h1>🇵🇹 LusoSupport-PT &middot; Browser Review</h1>
  <div class="right">
    <span id="sess-count">0 rated this session</span>
    <button class="btn-export" onclick="doExport()">⬇ Export</button>
  </div>
</div>
<div class="tabs">
  <div class="tab active" onclick="switchTab('browse')">Browse Dataset</div>
  <div class="tab" onclick="switchTab('generate')">Generate &amp; Test</div>
</div>
<div class="main">
  <div id="tab-browse">
    <div class="mode-bar">
      <button class="btn-mode active" id="mode-random" onclick="setMode('random')">Random</button>
      <button class="btn-mode" id="mode-flagged" onclick="setMode('flagged')">Flagged Only</button>
    </div>
    <div id="browse-area"><div class="loading">Loading…</div></div>
  </div>
  <div id="tab-generate" style="display:none">
    <div class="gen-form">
      <div class="form-grid">
        <div class="form-group form-full">
          <label>Customer message (PT-PT)</label>
          <textarea id="gen-msg" rows="3" placeholder="Escreve aqui a mensagem do cliente em português de Portugal…"></textarea>
        </div>
        <div class="form-group"><label>Domain</label><select id="gen-domain"></select></div>
        <div class="form-group"><label>Task type</label><select id="gen-task"></select></div>
        <div class="form-group"><label>Intent</label><select id="gen-intent"></select></div>
      </div>
      <button class="btn-generate" onclick="doGenerate()">Generate</button>
      <button class="btn-reset" onclick="resetGenerate()">Reset</button>
    </div>
    <div id="gen-area"></div>
  </div>
</div>
<script>
var sessCount=0,curRow=null,selRating=null,browseMode='random';
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/\\n/g,'<br>')}
function switchTab(t){
  document.querySelectorAll('.tab').forEach(function(el,i){el.classList.toggle('active',['browse','generate'][i]===t)});
  document.getElementById('tab-browse').style.display=t==='browse'?'':'none';
  document.getElementById('tab-generate').style.display=t==='generate'?'':'none';
}
function setMode(m){
  browseMode=m;
  document.getElementById('mode-random').classList.toggle('active',m==='random');
  document.getElementById('mode-flagged').classList.toggle('active',m==='flagged');
  loadRow();
}
function taskColor(tt){
  var c={response_generation:'#1a1a2e',email_reply:'#1d4ed8',summarization:'#15803d',
    intent_classification:'#7e22ce',urgency_classification:'#c2410c',
    faq_answer:'#0f766e',rewrite_professional:'#5b21b6',next_action_suggestion:'#374151'};
  return c[tt]||'#6b7280';
}
function renderCard(row,controls,prefix){
  prefix=prefix||'browse';
  var col=taskColor(row.task_type);
  return '<div class="card">'+
    '<div class="card-meta">'+
      '<span><span class="meta-label">Domain:</span> '+esc(row.domain)+'</span>'+
      '<span><span class="meta-label">Task:</span> '+esc(row.task_type)+'</span>'+
      '<span><span class="meta-label">Intent:</span> '+esc(row.customer_intent)+'</span>'+
      '<span><span class="meta-label">Tone:</span> '+esc(row.agent_tone)+'</span>'+
      '<span style="margin-left:auto;color:#9ca3af">'+esc(row.id)+'</span>'+
    '</div>'+
    '<div class="card-body">'+
      '<div><div class="field-label">Instruction</div><div class="field-value">'+esc(row.instruction)+'</div></div>'+
      '<div><div class="field-label">Input (customer message)</div><div class="field-value">'+esc(row.input)+'</div></div>'+
      '<div><div class="field-label">Output (agent response)</div><div class="field-value output" style="border-left-color:'+col+'">'+esc(row.output)+'</div></div>'+
    '</div>'+
    (controls?
    '<div class="rating-area">'+
      '<div class="rating-btns">'+
        '<button class="btn-rate btn-good" onclick="selectRating(\'good\',\''+prefix+'\')">✅ Good</button>'+
        '<button class="btn-rate btn-unclear" onclick="selectRating(\'unclear\',\''+prefix+'\')">❓ Unclear</button>'+
        '<button class="btn-rate btn-bad" onclick="selectRating(\'bad\',\''+prefix+'\')">❌ Bad</button>'+
        '<button class="btn-skip btn-rate" onclick="skipRow()">Skip →</button>'+
      '</div>'+
      '<div class="comment-row" id="'+prefix+'-comment">'+
        '<textarea id="'+prefix+'-txt" placeholder="Comment (required for Bad)…"></textarea>'+
        '<button class="btn-confirm" id="'+prefix+'-confirm" onclick="confirmRating(\''+prefix+'\')">Confirm</button>'+
      '</div>'+
    '</div>':'')+
    '</div>';
}
function selectRating(r,pfx){
  selRating=r;
  var area=document.getElementById(pfx+'-browse'!==pfx+'_x'?pfx:pfx);
  document.querySelectorAll('.btn-rate').forEach(function(b){b.classList.remove('sel')});
  document.querySelector('.btn-'+r).classList.add('sel');
  var cr=document.getElementById(pfx+'-comment');
  cr.classList.add('show');
  document.getElementById(pfx+'-confirm').textContent='Confirm '+r.toUpperCase();
}
async function confirmRating(pfx){
  if(!selRating||!curRow)return;
  var comment=document.getElementById(pfx+'-txt').value.trim();
  if(selRating==='bad'&&!comment){alert('Please add a comment for Bad ratings.');return;}
  await fetch('/api/rate',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id:curRow.id,rating:selRating,comment:comment,row:curRow})});
  sessCount++;
  document.getElementById('sess-count').textContent=sessCount+' rated this session';
  selRating=null;
  if(pfx==='browse')loadRow(); else{document.getElementById('gen-area').innerHTML='<div class="empty"><h3>Rated! Generate another?</h3></div>';}
}
function skipRow(){loadRow();}
async function loadRow(){
  document.getElementById('browse-area').innerHTML='<div class="loading">Loading…</div>';
  var res=await fetch('/api/sample?mode='+browseMode);
  var data=await res.json();
  if(!data.row){
    document.getElementById('browse-area').innerHTML='<div class="empty"><h3>All done! 🎉</h3><p>No more rows in this mode. Try switching to Random.</p></div>';
    return;
  }
  curRow=data.row;selRating=null;
  document.getElementById('browse-area').innerHTML=renderCard(data.row,true,'browse');
}
async function doGenerate(){
  var msg=document.getElementById('gen-msg').value.trim();
  if(!msg){alert('Please enter a customer message.');return;}
  var p=new URLSearchParams({
    domain:document.getElementById('gen-domain').value,
    task_type:document.getElementById('gen-task').value,
    intent:document.getElementById('gen-intent').value,
    message:msg
  });
  var data=await fetch('/api/generate?'+p).then(function(r){return r.json()});
  curRow=data.row;selRating=null;
  document.getElementById('gen-area').innerHTML=renderCard(data.row,true,'gen');
}
function resetGenerate(){
  document.getElementById('gen-msg').value='';
  document.getElementById('gen-area').innerHTML='';
  curRow=null;selRating=null;
}
function doExport(){window.location.href='/api/export';}
async function init(){
  var opts=await fetch('/api/options').then(function(r){return r.json()});
  [{id:'gen-domain',key:'domains'},{id:'gen-task',key:'task_types'},{id:'gen-intent',key:'intents'}].forEach(function(x){
    var sel=document.getElementById(x.id);
    opts[x.key].forEach(function(v){sel.add(new Option(v,v))});
  });
  loadRow();
}
init();
</script>
</body>
</html>"""


class ReviewHandler(BaseHTTPRequestHandler):
    """Handles all HTTP requests for the browser review UI."""

    def log_message(self, fmt, *args):  # suppress per-request logs
        pass

    # ------------------------------------------------------------------ GET

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        params = parse_qs(parsed.query)

        def _param(key, default=""):
            return params.get(key, [default])[0]

        if path == "/":
            self._send_html(_HTML)

        elif path == "/api/options":
            self._send_json({
                "domains":    DOMAINS,
                "task_types": TASK_TYPES,
                "intents":    CUSTOMER_INTENTS,
            })

        elif path == "/api/sample":
            mode = _param("mode", "random")
            rows = load_rows()
            reviewed = load_reviewed_ids()
            row = sample_row(rows, reviewed, mode=mode, feedback_dir=FEEDBACK_DIR)
            self._send_json({"row": row})

        elif path == "/api/generate":
            domain    = _param("domain",    DOMAINS[0])
            task_type = _param("task_type", TASK_TYPES[0])
            intent    = _param("intent",    CUSTOMER_INTENTS[0])
            message   = _param("message",   "")
            row = build_generated_row(domain, task_type, intent, message)
            self._send_json({"row": row})

        elif path == "/api/stats":
            rows      = load_rows()
            reviewed  = load_reviewed_ids()
            approved  = load_rows(FEEDBACK_DIR / "approved.jsonl")
            rejected  = load_rows(FEEDBACK_DIR / "rejected.jsonl")
            unclear   = load_rows(FEEDBACK_DIR / "browser_ratings.jsonl")
            self._send_json({
                "total_rows":     len(rows),
                "reviewed_total": len(reviewed),
                "approved_total": len(approved),
                "rejected_total": len(rejected),
                "unclear_total":  len(unclear),
            })

        elif path == "/api/export":
            export_path = FEEDBACK_DIR / "browser_ratings.jsonl"
            if not export_path.exists():
                self._send_json({"error": "No ratings yet"}, status=404)
            else:
                content = export_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/jsonl")
                self.send_header("Content-Disposition",
                                 'attachment; filename="browser_ratings.jsonl"')
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        else:
            self.send_response(404)
            self.end_headers()

    # ----------------------------------------------------------------- POST

    def do_POST(self):
        if self.path == "/api/rate":
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            rate_row(
                row_id      = body.get("id", ""),
                rating      = body.get("rating", "unclear"),
                comment     = body.get("comment", ""),
                row         = body.get("row", {}),
            )
            self._send_json({"ok": True})
        else:
            self.send_response(404)
            self.end_headers()

    # ----------------------------------------------------------------- util

    def _send_json(self, data: dict, status: int = 200):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html: str):
        payload = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LusoSupport-PT browser review server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open browser tab on start")
    args = parser.parse_args()

    # Always run relative to project root
    os.chdir(_ROOT)

    server = HTTPServer(("", args.port), ReviewHandler)
    url = f"http://localhost:{args.port}"
    print(f"Browser review → {url}  (Ctrl-C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
