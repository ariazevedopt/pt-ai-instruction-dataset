# Feedback Application Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply human review feedback to (1) dismiss false-positive "unclear" labels, (2) improve `response_generation` templates to ask clarifying questions instead of assuming, and (3) remove 2 rejected rows and replace them with fresh rows generated from the improved templates.

**Architecture:** Three sequential tasks — feedback file cleanup first, then template improvements, then dataset re-generation. Tasks 1 and 2 are independent and could swap order; Task 3 depends on Task 2 being done first so replacement rows use the improved templates.

**Tech Stack:** Python 3.9 stdlib, `scripts/responses.py` (template library), `scripts/generate.py` / `validate.py` / `dedupe.py`, `datasets/feedback/browser_ratings.jsonl`, `datasets/processed/lusosupport_pt_v1.jsonl`.

## Global Constraints

- All text in pt-PT only — no pt-BR vocabulary (`senha`, `celular`, `nota fiscal` are banned)
- Never delete entries from feedback files — mark as dismissed with `"dismissed": true`
- Row IDs follow pattern `lusosupport_pt_NNNNNN` (zero-padded to 6 digits); next available is `001999`
- Run tests from project root: `python3 -m pytest tests/ -v`; all 54 tests must pass
- Commit after each task

---

### Task 1: Dismiss False-Positive Feedback Entries

**Files:**
- Modify: `datasets/feedback/browser_ratings.jsonl`

**Interfaces:**
- Produces: `browser_ratings.jsonl` where 9 entries with classification-task IDs have `"dismissed": true, "dismiss_reason": "classification_task_correct"` added

- [ ] **Step 1: Run the dismissal script**

From the project root, run this one-off Python command to patch the file in-place:

```bash
python3 - <<'EOF'
import json
from pathlib import Path

DISMISS_IDS = {
    "lusosupport_pt_000107",
    "lusosupport_pt_000242",
    "lusosupport_pt_001165",
    "lusosupport_pt_000164",
    "lusosupport_pt_000115",
    "lusosupport_pt_001402",
    "lusosupport_pt_000970",
    "lusosupport_pt_000513",
    "lusosupport_pt_000412",
}

path = Path("datasets/feedback/browser_ratings.jsonl")
lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]
updated = []
for line in lines:
    entry = json.loads(line)
    if entry.get("id") in DISMISS_IDS:
        entry["dismissed"] = True
        entry["dismiss_reason"] = "classification_task_correct"
    updated.append(json.dumps(entry, ensure_ascii=False))

path.write_text("\n".join(updated) + "\n", encoding="utf-8")
print(f"Updated {path}: {len(lines)} entries processed")
EOF
```

Expected output:
```
Updated datasets/feedback/browser_ratings.jsonl: 13 entries processed
```

- [ ] **Step 2: Verify the changes**

```bash
python3 - <<'EOF'
import json
from pathlib import Path

entries = [json.loads(l) for l in Path("datasets/feedback/browser_ratings.jsonl").read_text().splitlines() if l.strip()]
dismissed = [e for e in entries if e.get("dismissed")]
active    = [e for e in entries if not e.get("dismissed")]
print(f"Dismissed: {len(dismissed)} (expected 9)")
print(f"Active:    {len(active)}    (expected 4)")
for e in dismissed:
    print(f"  - {e['id']}  task_type={e.get('row',{}).get('task_type','?')}")
EOF
```

Expected output:
```
Dismissed: 9 (expected 9)
Active:    4  (expected 4)
  - lusosupport_pt_000107  task_type=intent_classification
  - lusosupport_pt_000242  task_type=urgency_classification
  - lusosupport_pt_001165  task_type=intent_classification
  - lusosupport_pt_000164  task_type=intent_classification
  - lusosupport_pt_000115  task_type=urgency_classification
  - lusosupport_pt_001402  task_type=urgency_classification
  - lusosupport_pt_000970  task_type=intent_classification
  - lusosupport_pt_000513  task_type=urgency_classification
  - lusosupport_pt_000412  task_type=intent_classification
```

- [ ] **Step 3: Commit**

```bash
git add datasets/feedback/browser_ratings.jsonl
git commit -m "data: dismiss 9 false-positive unclear ratings for classification tasks"
```

---

### Task 2: Add Clarifying Template Variants to `responses.py`

**Files:**
- Modify: `scripts/responses.py` — lines ~215–255 (the `response_generation` section for `change_plan`, `password_reset`, `account_access`)

**Interfaces:**
- Produces: `RESPONSE_TEMPLATES[("response_generation", "account_access")]` grows from 5 → 7 variants; `password_reset` from 5 → 7; `change_plan` from 3 → 5

- [ ] **Step 1: Add 2 variants to `("response_generation", "change_plan")`**

Find the block (around line 215):
```python
    ("response_generation", "change_plan"): [
        "Claro, podemos ajudá-lo/a a alterar o plano. ...",
        "Agradecemos o contacto. A alteração de plano ...",
        "Ficamos disponíveis para ajudar na mudança de plano. ...",
    ],
```

Add 2 new strings at the end of the list (before the closing `],`):

```python
    ("response_generation", "change_plan"): [
        "Claro, podemos ajudá-lo/a a alterar o plano. Temos disponíveis as opções [Plano A], [Plano B] e [Plano C]. Qual prefere? A alteração é efectuada de imediato e o novo valor será cobrado no próximo ciclo de faturação.",
        "Agradecemos o contacto. A alteração de plano pode ser feita sem qualquer interrupção do serviço. Para avançar, pode indicar-nos qual o plano para o qual pretende mudar?",
        "Ficamos disponíveis para ajudar na mudança de plano. A alteração entra em vigor imediatamente. Quer que lhe expliquemos as diferenças entre os planos disponíveis antes de decidir?",
        "Posso ajudá-lo/a a explorar as opções de plano disponíveis. Qual é a sua principal prioridade — reduzir o custo mensal, aumentar o armazenamento, ou adicionar utilizadores?",
        "Antes de efectuarmos qualquer alteração, gostaria de apresentar as opções actuais para que possa escolher o plano mais adequado. Qual é a sua necessidade principal?",
    ],
```

- [ ] **Step 2: Add 2 variants to `("response_generation", "password_reset")`**

Find the block (around line 229):
```python
    ("response_generation", "password_reset"): [
        "Para repor a sua palavra-passe, ...",
        ...
        "Para sua segurança, o link de reposição ...",
    ],
```

Add 2 new strings at the end of the list (before the closing `],`):

```python
    ("response_generation", "password_reset"): [
        "Para repor a sua palavra-passe, aceda à página de início de sessão e clique em 'Esqueceu a palavra-passe?'. Será enviado um e-mail de recuperação para o endereço associado à conta. Verifique também a pasta de spam.",
        "Agradecemos o contacto. Para redefinir a palavra-passe, enviámos um e-mail de recuperação para o endereço registado. Caso não o receba nos próximos 5 minutos, verifique a pasta de spam ou contacte-nos novamente.",
        "A reposição da palavra-passe é feita através do link que enviámos para o seu e-mail. Se não recebeu o e-mail, pode indicar-nos o endereço registado na conta para verificarmos a situação?",
        "Pode redefinir a palavra-passe directamente através do portal em 'Acesso à Conta' → 'Esqueci a palavra-passe'. Se o endereço de e-mail registado já não está activo, contacte-nos para verificação de identidade alternativa.",
        "Para sua segurança, o link de reposição de palavra-passe expira ao fim de 30 minutos. Se já expirou, pode solicitar um novo na página de login. Caso continue sem acesso, podemos verificar a conta e fazer o reset manualmente.",
        "Para auxiliar com a recuperação da palavra-passe, pode confirmar o endereço de e-mail associado à conta? Por vezes, o e-mail de recuperação pode chegar à pasta de spam ou lixo.",
        "Verificou a pasta de spam ou de lixo do seu e-mail? O e-mail de recuperação pode ter sido filtrado. Se confirmar o endereço registado, podemos reenviar de imediato.",
    ],
```

- [ ] **Step 3: Add 2 variants to `("response_generation", "account_access")`**

Find the block (around line 237):
```python
    ("response_generation", "account_access"): [
        "Pedimos desculpa pelo problema no acesso. ...",
        ...
        "O acesso bloqueado pode dever-se a múltiplas tentativas ...",
    ],
```

Add 2 new strings at the end of the list (before the closing `],`):

```python
    ("response_generation", "account_access"): [
        "Pedimos desculpa pelo problema no acesso. Para verificarmos a situação da sua conta, pode confirmar o endereço de e-mail associado? Verificaremos se a conta está activa e, se necessário, procederemos ao desbloqueio.",
        "Lamentamos o inconveniente. O problema de acesso pode estar relacionado com uma autenticação falhada ou com a conta temporariamente bloqueada por motivos de segurança. Pode indicar-nos o e-mail de registo?",
        "Para resolvermos o problema de acesso com a maior brevidade, precisamos de verificar a sua identidade. Pode confirmar o endereço de e-mail e o número de telemóvel associados à conta?",
        "Compreendemos o transtorno causado pelo bloqueio de acesso. Após confirmação da sua identidade, procederemos ao desbloqueio imediato da conta. Pode fornecer o e-mail de registo e os últimos 4 dígitos do número de telemóvel?",
        "O acesso bloqueado pode dever-se a múltiplas tentativas falhadas ou a uma actualização de segurança. Vamos verificar a situação. Por favor confirme o endereço de e-mail e aguarde — o desbloqueio é efectuado em minutos.",
        "Para melhor compreender a situação, pode descrever o que acontece quando tenta aceder à sua conta? Recebe alguma mensagem de erro específica?",
        "Antes de prosseguirmos, precisamos de perceber em que passo está a encontrar dificuldade. Está a tentar aceder pelo site, aplicação, ou outro canal?",
    ],
```

- [ ] **Step 4: Verify the new variant counts**

```bash
python3 - <<'EOF'
import sys
sys.path.insert(0, "scripts")
from responses import RESPONSE_TEMPLATES

for intent in ("change_plan", "password_reset", "account_access"):
    variants = RESPONSE_TEMPLATES[("response_generation", intent)]
    print(f"response_generation / {intent}: {len(variants)} variants")
    # Print the last 2 (the newly added ones)
    for v in variants[-2:]:
        print(f"  + {repr(v[:80])}")
EOF
```

Expected output:
```
response_generation / change_plan: 5 variants
  + 'Posso ajudá-lo/a a explorar as opções de plano disponíveis. Qual é a sua p...'
  + 'Antes de efectuarmos qualquer alteração, gostaria de apresentar as opções a...'
response_generation / password_reset: 7 variants
  + 'Para auxiliar com a recuperação da palavra-passe, pode confirmar o endereço...'
  + 'Verificou a pasta de spam ou de lixo do seu e-mail? O e-mail de recuperação...'
response_generation / account_access: 7 variants
  + 'Para melhor compreender a situação, pode descrever o que acontece quando ten...'
  + 'Antes de prosseguirmos, precisamos de perceber em que passo está a encontrar...'
```

- [ ] **Step 5: Run the test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: `54 passed` — no failures. (The new templates are prose content; existing tests don't enumerate template strings so no test changes are needed.)

- [ ] **Step 6: Commit**

```bash
git add scripts/responses.py
git commit -m "feat: add clarifying variants to account_access, password_reset, change_plan templates"
```

---

### Task 3: Remove Rejected Rows and Regenerate Replacements

**Files:**
- Modify: `datasets/processed/lusosupport_pt_v1.jsonl` — remove 2 rows, append 2 new ones

**Interfaces:**
- Consumes: improved templates from Task 2 (via `scripts/generate.py` → `scripts/responses.py`)
- Produces: `lusosupport_pt_v1.jsonl` with 1275 rows, IDs `lusosupport_pt_000266` and `lusosupport_pt_001685` absent, two new rows with IDs `lusosupport_pt_001999` and `lusosupport_pt_002000` present

- [ ] **Step 1: Remove the 2 rejected rows**

```bash
python3 - <<'EOF'
import json
from pathlib import Path

REJECTED_IDS = {"lusosupport_pt_000266", "lusosupport_pt_001685"}

path = Path("datasets/processed/lusosupport_pt_v1.jsonl")
rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
kept = [r for r in rows if r["id"] not in REJECTED_IDS]

path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kept) + "\n", encoding="utf-8")
print(f"Before: {len(rows)} rows  After: {len(kept)} rows  Removed: {len(rows)-len(kept)}")
EOF
```

Expected output:
```
Before: 1275 rows  After: 1273 rows  Removed: 2
```

- [ ] **Step 2: Generate 5 candidate replacement rows**

Generate more than needed so deduplication has buffer:

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, "scripts")
from generate import generate_row

# IDs 1999 and 2000 are the next available (max existing was 1998)
candidates = [generate_row(1999), generate_row(2000), generate_row(2001), generate_row(2002), generate_row(2003)]
out_path = "datasets/interim/replacement_candidates.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for row in candidates:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"Generated {len(candidates)} candidates → {out_path}")
for r in candidates:
    print(f"  {r['id']}  task={r['task_type']}  intent={r['customer_intent']}")
EOF
```

Expected: 5 lines listing the generated row IDs and their task types.

- [ ] **Step 3: Validate and dedupe the candidates against the existing dataset**

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, "scripts")
from validate import is_valid_row
from dedupe import deduplicate
from pathlib import Path

# Load existing processed rows for dedup check
existing = [json.loads(l) for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines() if l.strip()]
candidates = [json.loads(l) for l in Path("datasets/interim/replacement_candidates.jsonl").read_text().splitlines() if l.strip()]

# Validate
valid = []
for r in candidates:
    ok, reason = is_valid_row(r)
    if ok:
        valid.append(r)
    else:
        print(f"  INVALID {r['id']}: {reason}")

# Dedupe: check candidates aren't duplicates of existing rows
all_rows = existing + valid
unique_all = deduplicate(all_rows)
new_unique = unique_all[len(existing):]  # only the candidates that survived dedup

print(f"Valid candidates: {len(valid)}")
print(f"Unique after dedup against existing: {len(new_unique)}")
for r in new_unique:
    print(f"  {r['id']}  task={r['task_type']}  intent={r['customer_intent']}")
EOF
```

Expected: at least 2 valid unique candidates printed. If fewer than 2 unique rows appear, re-run Step 2 with higher indices (2004, 2005, ...) until you have 2.

- [ ] **Step 4: Append exactly 2 replacement rows**

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, "scripts")
from validate import is_valid_row
from dedupe import deduplicate
from pathlib import Path

existing = [json.loads(l) for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines() if l.strip()]
candidates = [json.loads(l) for l in Path("datasets/interim/replacement_candidates.jsonl").read_text().splitlines() if l.strip()]

valid = [r for r in candidates if is_valid_row(r)[0]]
all_rows = existing + valid
unique_all = deduplicate(all_rows)
new_unique = unique_all[len(existing):]

if len(new_unique) < 2:
    print("ERROR: fewer than 2 unique valid candidates — re-run Step 2 with more indices")
    sys.exit(1)

to_append = new_unique[:2]
path = Path("datasets/processed/lusosupport_pt_v1.jsonl")
with open(path, "a", encoding="utf-8") as f:
    for r in to_append:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

total = len(existing) + len(to_append)
print(f"Appended {len(to_append)} rows. Total: {total} (expected 1275)")
for r in to_append:
    print(f"  + {r['id']}  task={r['task_type']}  intent={r['customer_intent']}")
EOF
```

Expected output:
```
Appended 2 rows. Total: 1275 (expected 1275)
  + lusosupport_pt_001999  task=...  intent=...
  + lusosupport_pt_002000  task=...  intent=...
```

- [ ] **Step 5: Final verification**

```bash
python3 - <<'EOF'
import json
from pathlib import Path

rows = [json.loads(l) for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines() if l.strip()]
ids = {r["id"] for r in rows}

print(f"Total rows: {len(rows)} (expected 1275)")
print(f"lusosupport_pt_000266 absent: {('lusosupport_pt_000266' not in ids)}")
print(f"lusosupport_pt_001685 absent: {('lusosupport_pt_001685' not in ids)}")
print(f"lusosupport_pt_001999 present: {('lusosupport_pt_001999' in ids)}")
EOF
```

Expected output:
```
Total rows: 1275 (expected 1275)
lusosupport_pt_000266 absent: True
lusosupport_pt_001685 absent: True
lusosupport_pt_001999 present: True
```

- [ ] **Step 6: Clean up interim file and commit**

```bash
rm datasets/interim/replacement_candidates.jsonl
git add datasets/feedback/browser_ratings.jsonl datasets/processed/lusosupport_pt_v1.jsonl
git commit -m "data: remove 2 rejected rows, append 2 regenerated replacements with improved templates"
```
