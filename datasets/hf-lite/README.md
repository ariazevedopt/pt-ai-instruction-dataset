---
language:
- pt
license: cc-by-4.0
task_categories:
- text-generation
- text-classification
- question-answering
task_ids:
- dialogue-modeling
- intent-classification
pretty_name: LusoSupport-PT Lite
size_categories:
- n<1K
tags:
- customer-support
- portuguese
- pt-PT
- european-portuguese
- instruction-tuning
- fine-tuning
- synthetic
---

# LusoSupport-PT Lite

**LusoSupport-PT** is a structured **European Portuguese (pt-PT)** customer support instruction dataset for LLM fine-tuning, prompting experiments, and support automation.

This **Lite** version contains **200 curated rows** — a representative free sample covering all 8 domains, 8 task types, and all 18 customer intents.

The full dataset (5 163 rows) is available for purchase at [Gumroad](https://gumroad.com) — see pricing below.

---

## Why pt-PT?

Most publicly available Portuguese NLP datasets are either broad generic corpora, academic benchmarks, or heavily oriented toward **Brazilian Portuguese (pt-BR)**. LusoSupport-PT fills the gap: a clean, structured instruction dataset that uses **European Portuguese vocabulary and register** throughout.

- ✅ `palavra-passe` (not `senha`)
- ✅ `telemóvel` (not `celular`)
- ✅ `fatura` (not `nota fiscal`)
- ✅ `encomenda` for orders

---

## Dataset Structure

Each row contains:

| Field | Type | Description |
|---|---|---|
| `id` | string | `lusosupport_pt_NNNNNN` |
| `language` | string | Always `"pt"` |
| `variant` | string | Always `"pt-PT"` |
| `domain` | string | One of 8 business domains |
| `subdomain` | string | Specific sub-area within domain |
| `task_type` | string | One of 8 task types |
| `customer_intent` | string | One of 18 customer intents |
| `customer_tone` | string | Tone of the customer message |
| `agent_tone` | string | Target tone for the agent response |
| `channel` | string | `email`, `chat`, `web_form`, `phone_transcript` |
| `difficulty` | string | `easy`, `medium`, `hard` |
| `instruction` | string | System-level task instruction (pt-PT) |
| `input` | string | Customer message prefixed with `"Mensagem do cliente:"` |
| `output` | string | Model target: agent response or classification |
| `metadata` | object | `requires_escalation`, `contains_pii`, `synthetic`, `source_type` |

### Domains

`ecommerce` · `subscriptions` · `saas` · `telecom` · `utilities` · `travel` · `marketplace` · `billing_accounts`

### Task Types

| Task Type | Description |
|---|---|
| `response_generation` | Write a support reply to a customer |
| `email_reply` | Draft a formal email response |
| `summarization` | Summarise a customer interaction |
| `intent_classification` | Classify intent, urgency, domain (JSON output) |
| `urgency_classification` | Rate urgency and recommend escalation (JSON output) |
| `rewrite_professional` | Rewrite a message in a professional register |
| `next_action_suggestion` | Recommend the next best action for the agent |
| `faq_answer` | Answer a frequently asked question |

---

## Usage

### Load with 🤗 Datasets

```python
from datasets import load_dataset

ds = load_dataset("ariazevedopt/LusoSupport-PT", split="train")
print(ds[0])
```

### Fine-tuning (Alpaca format)

The full dataset ships with an Alpaca JSONL export. Convert directly:

```python
import json

with open("lusosupport_pt_lite.jsonl") as f:
    rows = [json.loads(l) for l in f]

alpaca = [
    {"instruction": r["instruction"], "input": r["input"], "output": r["output"]}
    for r in rows
]
```

### Intent classification example

```python
import json

row = ds.filter(lambda r: r["task_type"] == "intent_classification")[0]
print(row["input"])
# → "Mensagem do cliente: A minha encomenda não chegou."

result = json.loads(row["output"])
print(result)
# → {"intent": "order_status", "urgency": "medium", "domain": "ecommerce", "confidence": 0.95}
```

---

## Pricing

| Tier | Price | Rows | Licence |
|---|---|---|---|
| **Lite (this dataset)** | Free | 200 | CC BY 4.0 |
| **Premium Individual** | €39 | 5 163 | Personal / research / non-commercial |
| **Commercial Licence** | €149 | 5 163 | Commercial use in products & APIs |

👉 [Buy on Gumroad](https://gumroad.com) · [GitHub Sponsors](https://github.com/sponsors/ariazevedopt)

---

## Licence

This Lite version is released under **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.  
You are free to use, share, and adapt the data — provided you give appropriate credit.

**Attribution:** `LusoSupport-PT by @ariazevedopt — https://huggingface.co/datasets/ariazevedopt/LusoSupport-PT`

The full dataset is sold under separate commercial and personal-use licence agreements available at Gumroad.

---

## Citation

```bibtex
@dataset{lusosupport_pt_2026,
  author    = {ariazevedopt},
  title     = {LusoSupport-PT: European Portuguese Customer Support Instruction Dataset},
  year      = {2026},
  url       = {https://huggingface.co/datasets/ariazevedopt/LusoSupport-PT},
  note      = {CC BY 4.0}
}
```

---

## Related Links

- 📦 [GitHub Repository](https://github.com/ariazevedopt/pt-ai-instruction-dataset)
- 📖 [Schema Documentation](https://github.com/ariazevedopt/pt-ai-instruction-dataset/blob/main/docs/schema.md)
- 🔗 [Integration Guide](https://github.com/ariazevedopt/pt-ai-instruction-dataset/blob/main/docs/integration.md) — Unsloth, LLaMA-Factory, OpenAI, LangChain
