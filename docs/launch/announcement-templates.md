# LusoSupport-PT — Announcement Templates

Ready-to-post copy for the launch of LusoSupport-PT on HF, Reddit, and LinkedIn.

---

## 1. Reddit — r/MachineLearning / r/LocalLLaMA / r/datasets

**Title:**
> I built the only European Portuguese (pt-PT) customer support instruction dataset for LLM fine-tuning — free sample on Hugging Face

**Body:**
```
Hey everyone,

I just published LusoSupport-PT, and as far as I can tell it's the only purpose-built European Portuguese (pt-PT) customer support instruction dataset out there — I checked the HF Hub and found only generic pt-PT/pt-BR corpora (Wikipedia, OSCAR, intent benchmarks), nothing support-domain or instruction-formatted.

**Why it exists**
Most Portuguese NLP datasets are either generic corpora, academic benchmarks, or heavily pt-BR. LusoSupport-PT targets European Portuguese (Portugal) specifically — different vocabulary, register, and tone from Brazilian Portuguese.

**What's in it**
- 200 free rows on Hugging Face (full dataset: 5,163 rows)
- 8 domains: e-commerce, SaaS, telecoms, utilities, travel, marketplace, subscriptions, billing
- 8 task types: response generation, email reply, summarisation, intent classification, urgency classification, rewrite, next-action suggestion, FAQ answer
- 18 customer intents × 6 tones × 4 channels
- Clean metadata: customer_tone, agent_tone, difficulty, requires_escalation, subdomain
- Validated: no pt-BR vocabulary, no stubs, all enums enforced

**Formats**
JSONL, CSV, Alpaca JSONL (fine-tuning ready), Parquet

🔥 Early adopter pricing on the full dataset — first 50 buyers lock in €39/€149, then it rises to €59/€199.

**Links**
🤗 Free on HF: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
💻 GitHub: https://github.com/ariazevedopt/pt-ai-instruction-dataset
💼 Full dataset (5,163 rows): https://ariazevedo.gumroad.com/l/lusosupport-pt

Happy to answer questions about the generation pipeline or the pt-PT design choices.
```

---

## 2. Hugging Face Community Forum

**Title:**
> LusoSupport-PT — European Portuguese customer support instruction dataset (pt-PT, 200 rows free)

**Body:**
```
Hi HF community 👋

I've just published **LusoSupport-PT** — as far as I can tell, the only purpose-built instruction dataset for European Portuguese (pt-PT) customer support. I checked the Hub and only found generic pt-PT/pt-BR corpora, nothing support-domain or instruction-formatted.

🔗 Dataset: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT

### What makes it different

Most Portuguese datasets are pt-BR or generic. This one is built specifically for **Portugal's Portuguese** — different vocabulary (`palavra-passe`, `telemóvel`, `fatura`, `encomenda`), formal register, and support-specific tone.

### Contents (free Lite version: 200 rows)

| Field | Details |
|---|---|
| Domains | ecommerce, saas, telecom, subscriptions, utilities, travel, marketplace, billing_accounts |
| Task types | response_generation, email_reply, summarization, intent_classification, urgency_classification, rewrite_professional, next_action_suggestion, faq_answer |
| Intents | 18 customer intents |
| Metadata | customer_tone, agent_tone, channel, difficulty, requires_escalation |

### Quick start

```python
from datasets import load_dataset
ds = load_dataset("ariazevedo/LusoSupport-PT", split="train")
print(ds[0]["instruction"])  # pt-PT instruction
print(ds[0]["output"])       # pt-PT agent response
```

The full dataset (5,163 rows) is available at https://ariazevedo.gumroad.com/l/lusosupport-pt — 🔥 early adopter pricing for the first 50 buyers (€39/€149, rising to €59/€199 after).

Feedback welcome — especially from anyone working on Portuguese NLP!
```

---

## 3. LinkedIn

**Post:**
```
🇵🇹 Excited to share LusoSupport-PT — the only purpose-built European Portuguese (pt-PT) customer support instruction dataset for LLM fine-tuning (verified against the Hugging Face Hub — no direct competitor found).

Key facts:
✅ 200 rows FREE on Hugging Face
✅ Full dataset: 5,163 rows across 8 domains and 8 task types
✅ Proper pt-PT (not pt-BR): palavra-passe, telemóvel, fatura, encomenda
✅ Fine-tuning ready: JSONL, CSV, Alpaca JSONL, Parquet
✅ Clean metadata: intent, tone, channel, difficulty, escalation flag
🔥 Early adopter pricing: first 50 buyers lock in €39/€149 (rising to €59/€199 after)

Portuguese NLP has a real gap in European Portuguese resources. LusoSupport-PT is a small step toward closing it.

🤗 Free on Hugging Face: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
💻 GitHub: https://github.com/ariazevedopt/pt-ai-instruction-dataset
💼 Full dataset: https://ariazevedo.gumroad.com/l/lusosupport-pt

#NLP #MachineLearning #Portuguese #FineTuning #OpenSource #LLM #DataScience
```

---

## Posting checklist

- [ ] HF repo is live and `[HF_URL]` is confirmed
- [ ] Gumroad product pages are live
- [ ] Post on r/MachineLearning
- [ ] Post on r/LocalLLaMA
- [ ] Post on r/datasets
- [ ] Post on HF Community Forum
- [ ] Post on LinkedIn
