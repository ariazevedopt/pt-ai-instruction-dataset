# LusoSupport-PT — Usage Guide

A quick-start guide for anyone who has downloaded or purchased **LusoSupport-PT** — whether the free Lite sample from Hugging Face or the full dataset from Gumroad. For deep integration recipes (fine-tuning, RAG, evaluation), see [`docs/integration.md`](integration.md).

---

## 1. What you got

| Tier | Source | Rows | Files |
|---|---|---|---|
| 🆓 Lite | [Hugging Face](https://huggingface.co/datasets/ariazevedo/LusoSupport-PT) | 200 | `lusosupport_pt_lite.jsonl`, `lusosupport_pt_lite_amalia_chat.jsonl` |
| 💼 Individual | [Gumroad](https://ariazevedo.gumroad.com/l/lusosupport-pt) | 10 828 | `lusosupport_pt_v1.jsonl`, `.csv`, `_alpaca.jsonl`, `_amalia_chat.jsonl`, `.parquet`, `LICENCE-COMMERCIAL.md` |
| 🏢 Commercial | [Gumroad](https://ariazevedo.gumroad.com/l/lusosupport-pt-commercial) | 10 828 | Same files as Individual |

All formats contain the **same rows** — pick whichever format suits your tooling:

| File | Best for |
|---|---|
| `.jsonl` | Python, Hugging Face `datasets`, most ML pipelines |
| `.csv` | Excel, Google Sheets, pandas, spreadsheet review |
| `_alpaca.jsonl` | Instruction fine-tuning frameworks expecting `{instruction, input, output}` (Unsloth, LLaMA-Factory, Axolotl) — for models using a plain Alpaca-style prompt template |
| `_amalia_chat.jsonl` | Fine-tuning [AMALIA](https://amaliallm.pt/) or any other ChatML-style chat model — `{"messages": [{"role": "system"/"user"/"assistant", "content": ...}]}`, ready for `tokenizer.apply_chat_template()`. See [`docs/integration.md` §2](integration.md#2-fine-tuning-amalia-for-customer-support). |
| `.parquet` | Large-scale/columnar processing (Spark, DuckDB, polars) |

---

## 2. Loading the dataset

### Python — plain JSONL
```python
import json

rows = [json.loads(line) for line in open("lusosupport_pt_v1.jsonl", encoding="utf-8")]
print(len(rows), rows[0]["instruction"])
```

### Python — pandas
```python
import pandas as pd

df = pd.read_json("lusosupport_pt_v1.jsonl", lines=True)
# or: df = pd.read_csv("lusosupport_pt_v1.csv")
# or: df = pd.read_parquet("lusosupport_pt_v1.parquet")

print(df.groupby("domain").size())
```

### Hugging Face `datasets`
```python
from datasets import load_dataset

# Free Lite sample directly from the Hub
ds = load_dataset("ariazevedo/LusoSupport-PT", split="train")

# Full purchased dataset, loaded locally
ds = load_dataset("json", data_files="lusosupport_pt_v1.jsonl", split="train")
```

### Excel / Google Sheets
Open `lusosupport_pt_v1.csv` directly — no conversion needed.

---

## 3. Row structure

Each row is a JSON object with these fields:

```json
{
  "id": "lusosupport_pt_000001",
  "language": "pt",
  "variant": "pt-PT",
  "domain": "ecommerce",
  "subdomain": "returns_refunds",
  "task_type": "response_generation",
  "customer_intent": "refund_request",
  "customer_tone": "frustrated",
  "agent_tone": "empathetic",
  "channel": "email",
  "difficulty": "easy",
  "instruction": "Responde ao cliente em português de Portugal, com tom empático e profissional...",
  "input": "Mensagem do cliente: \"...\"",
  "output": "Lamentamos a situação. Podemos ajudar no processo de devolução...",
  "metadata": { "requires_escalation": false, "contains_pii": false, "synthetic": true, "source_type": "manual_seed" }
}
```

Full field reference: [`docs/schema.md`](schema.md).

---

## 4. Common quick uses

**Filter by domain or task type**
```python
ecommerce_rows = df[df["domain"] == "ecommerce"]
classification_rows = df[df["task_type"].isin(["intent_classification", "urgency_classification"])]
```

**Fine-tune with the Alpaca format** (Unsloth / LLaMA-Factory / Axolotl)
```python
alpaca_ds = load_dataset("json", data_files="lusosupport_pt_v1_alpaca.jsonl", split="train")
# Each row: {"instruction": ..., "input": ..., "output": ...}
```

**Few-shot prompting** — sample a handful of rows matching your `domain`/`task_type` and inject them into your system prompt as examples.

For full code walkthroughs (Unsloth training script, LangChain RAG, OpenAI fine-tuning, evaluation with ROUGE/BERTScore), see [`docs/integration.md`](integration.md) and [`docs/use-cases.md`](use-cases.md).

---

## 5. Licence recap

- **Lite (Hugging Face):** CC BY 4.0 — free use with attribution.
- **Individual / Research (€59):** personal, research, and non-commercial internal use. Not for resale or redistribution as a data product.
- **Commercial (€229):** all Individual uses, plus commercial software, SaaS APIs, consulting deliverables, and team/organisation use.

Full terms: [`LICENCE-COMMERCIAL.md`](../LICENCE-COMMERCIAL.md) (paid tiers) or the CC BY 4.0 licence text (Lite tier).

**Not permitted at any tier:** redistributing or reselling the raw dataset files, or publishing the full dataset publicly.

---

## 6. Support

- 📖 Schema reference: [`docs/schema.md`](schema.md)
- 🔧 Integration recipes: [`docs/integration.md`](integration.md)
- 💡 Use cases: [`docs/use-cases.md`](use-cases.md)
- 🐛 Issues or questions: [GitHub Issues](https://github.com/ariazevedopt/pt-ai-instruction-dataset/issues)
