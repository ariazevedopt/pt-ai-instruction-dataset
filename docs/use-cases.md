# LusoSupport-PT — Use Cases, Value & Integration Guide

This document explains the value of the LusoSupport-PT dataset, the problems it solves, and how to integrate it into real products and workflows.

---

## Why This Dataset Exists

Most available Portuguese NLP datasets share the same three problems:

| Problem | Impact |
|---|---|
| **Brazilian Portuguese dominance** | Models trained on `pt-BR` data produce unnatural outputs for European Portuguese speakers — wrong vocabulary, wrong register, wrong idioms |
| **Generic or academic framing** | Broad corpora and benchmark sets don't map to real support workflows; few examples reflect actual business dialogue |
| **Lack of structured metadata** | Raw text collections without task type, intent, domain, or tone labels are hard to filter, fine-tune on selectively, or repurpose |

LusoSupport-PT addresses all three: it is **pt-PT first**, **support-domain focused**, and **richly annotated**.

---

## What the Dataset Covers

**1,275 rows** across 8 domains, 8 task types, and 18 customer intents.

### Domains

| Domain | Typical scenarios |
|---|---|
| `ecommerce` | Refunds, damaged goods, delivery delays, order status |
| `subscriptions` | Plan changes, cancellations, billing cycles |
| `saas` | Account access, password issues, technical faults |
| `telecom` | Service interruptions, billing disputes, upgrades |
| `utilities` | Meter readings, outages, contract queries |
| `travel` | Booking changes, cancellations, delays |
| `marketplace` | Seller disputes, payment issues, logistics |
| `billing_accounts` | Invoices, duplicate charges, payment failures |

### Task types

| Task type | What the model learns | Example output |
|---|---|---|
| `response_generation` | Draft a complete, professional PT-PT reply to a customer | Full agent response |
| `email_reply` | Write a formal email reply with subject + body structure | Email text |
| `summarization` | Summarise the customer's issue for internal handover | 1–3 sentence summary |
| `intent_classification` | Classify what the customer wants + urgency level | JSON with intent + confidence |
| `urgency_classification` | Rate urgency and explain why | JSON with urgency level + reason |
| `rewrite_professional` | Rewrite an informal draft into formal PT-PT | Rewritten text |
| `next_action_suggestion` | Suggest the most appropriate next step for an agent | Action description |
| `faq_answer` | Answer a common question from a knowledge-base perspective | Direct answer |

### Customer intents (18 total)

`refund_request` · `return_request` · `order_status` · `delivery_delay` · `damaged_item` · `billing_question` · `invoice_request` · `cancel_subscription` · `change_plan` · `technical_issue` · `password_reset` · `account_access` · `complaint` · `escalation_request` · `booking_change` · `booking_cancellation` · `payment_failure` · `duplicate_charge`

---

## Use Cases

### 1. Fine-tuning an LLM for PT-PT customer support

Train or fine-tune a language model to handle support queries in European Portuguese. The dataset provides instruction-input-output triples in Alpaca format, ready for frameworks like LLaMA-Factory, Unsloth, Axolotl, or OpenAI fine-tuning.

**What you get:** A model that understands PT-PT vocabulary, replies with the right register, and handles the most common support intents without translation artefacts.

**Who benefits:** Companies serving Portuguese markets that can't afford to deploy a generic model that mixes Brazilian Portuguese into customer replies.

---

### 2. Prompting and few-shot examples

Use rows directly as few-shot examples in a system prompt to steer a general-purpose model (GPT-4, Claude, Gemini, etc.) toward PT-PT support behaviour — without fine-tuning.

**Example:** Filter for `task_type = response_generation` and `domain = ecommerce`, pick 3–5 approved rows, and inject them as examples into your system prompt.

**What you get:** Immediate improvement in PT-PT output quality with no training cost.

---

### 3. Intent + urgency classification pipeline

Use the `intent_classification` and `urgency_classification` rows to train or evaluate a routing/triage model that reads incoming customer messages and labels them automatically before routing to the right queue.

**What you get:** A structured classifier that outputs `{ intent, urgency, domain, confidence }` in PT-PT — ready to plug into a helpdesk system.

---

### 4. RAG grounding and retrieval

Use approved rows as a retrieval corpus. When a new customer message arrives, retrieve the most semantically similar instruction-input pairs and use their outputs as grounding context for a generation model.

**What you get:** Reduced hallucination; outputs anchored to known-good PT-PT responses for similar situations.

---

### 5. Agent response evaluation

Use the dataset as a **reference set for evaluation**: compare your model's outputs against the ground-truth `output` field to measure:

- ROUGE / BLEU scores for text overlap
- BERTScore for semantic similarity
- PT-PT vocabulary compliance (no pt-BR terms)
- Intent alignment (does the response address the right intent?)

**What you get:** A concrete benchmark for PT-PT support quality that doesn't require manual annotation.

---

### 6. Chatbot and helpdesk copilot prototyping

Bootstrap a PT-PT support chatbot with zero labelling effort. Use the dataset as the starting training set, add your company-specific scenarios on top, and iterate with the browser review UI.

**What you get:** A running prototype within hours, not weeks.

---

### 7. Agent tone and professionalism rewriting

The `rewrite_professional` task type provides pairs of informal → formal PT-PT text. Use these to train a lightweight rewrite model that transforms what agents type into polished customer-facing language.

**What you get:** Consistent, professional tone across all agent-customer interactions regardless of who is writing.

---

### 8. Internal knowledge-base summarisation

Use `summarization` rows to train or evaluate a model that condenses customer messages into structured internal notes for handover between agents or teams.

**What you get:** Faster agent handovers, less context lost between shifts.

---

## Integration Patterns

→ **[Full integration guide](integration.md)** — complete working code for every pattern listed below.

| Pattern | What it covers |
|---|---|
| [Loading with HuggingFace `datasets`](integration.md#1-loading-the-dataset) | Load, filter, train/val split |
| [Unsloth fine-tuning (LLaMA / Mistral)](integration.md#2-fine-tuning-with-unsloth-llama--mistral) | QLoRA on consumer GPU, full training script + inference |
| [LLaMA-Factory](integration.md#3-fine-tuning-with-llama-factory) | Config-driven multi-model training |
| [OpenAI fine-tuning](integration.md#4-openai-fine-tuning-gpt-4o-mini) | Convert format, upload, train, monitor, use |
| [Few-shot prompting](integration.md#5-few-shot-prompting-no-training) | Dynamic + semantic shot selection, no training cost |
| [Intent classification pipeline](integration.md#6-intent-classification-pipeline) | Prompt-based or fine-tuned BERT classifier |
| [RAG with LangChain + FAISS](integration.md#7-rag-with-langchain--faiss) | Full chain with domain filtering |
| [RAG with ChromaDB (persistent)](integration.md#8-rag-with-chromadb-persistent) | On-disk index for production |
| [Evaluation and benchmarking](integration.md#9-evaluation-and-benchmarking) | ROUGE, BERTScore, PT-PT compliance |
| [Push to Hugging Face Hub](integration.md#10-pushing-to-hugging-face-hub) | Share dataset or fine-tuned model |

---

## What Makes This Dataset Distinctive

### pt-PT vocabulary enforcement

The validation pipeline enforces European Portuguese at the word level. Banned pt-BR terms (`senha`, `celular`, `nota fiscal`) are automatically rejected. Every row uses:
- `palavra-passe` (not `senha`)
- `telemóvel` (not `celular`)
- `fatura` (not `nota fiscal`)
- `encomenda` for orders

This matters for models: training on mixed-variant data produces outputs that flip between variants unpredictably.

### Rich metadata for selective training

Each row has `domain`, `task_type`, `customer_intent`, `customer_tone`, `agent_tone`, `channel`, `difficulty`, and safety metadata. This lets you build **targeted subsets** — e.g., a fine-tune only on hard ecommerce refund cases in an empathetic agent tone — without writing custom labelling pipelines.

### Human review loop

The dataset includes a built-in human review workflow (`make review-browser`) with feedback recorded in structured JSONL files. Approved rows are marked as quality anchors. Rejected rows are excluded from the pipeline. This means the dataset improves continuously with use.

### Seed examples as quality floor

`datasets/raw/seed_examples.jsonl` contains 64 hand-crafted rows that act as a permanent quality floor. These are always included in the processed dataset and serve as reference examples for both manual reviewers and automated validators.

---

## Scope Boundaries

### What is in scope

- Customer-to-agent dialogue in PT-PT
- Business support workflows across the 8 domains listed above
- Single-turn instruction-following (instruction → input → output)
- Classification outputs (JSON-structured intent and urgency labels)
- Text transformation tasks (rewrite, summarisation, next-action)
- FAQ answering from a support knowledge-base perspective

### What is out of scope (v1)

- Multi-turn conversation / dialogue history
- Medical, legal, tax, or investment advice
- Real personal data or PII
- Company-specific proprietary policies stated as facts
- Brazilian Portuguese (`pt-BR`) — this is a separate future variant
- Languages other than Portuguese

### Possible future expansions

- `pt-BR` split for Brazilian market coverage
- Multi-turn conversation format
- Bilingual PT-PT ↔ EN pairs
- Industry-specific vertical slices (healthcare admin, insurance, banking)
- Larger scale (10k+ rows) with broader intent coverage
- Model evaluation benchmarks built on top of this dataset

---

## Getting Started

```bash
# Clone and install
git clone https://github.com/ariazevedopt/pt-ai-instruction-dataset
pip install -r requirements.txt

# The ready-to-use dataset
cat datasets/processed/lusosupport_pt_v1.jsonl | head -1 | python3 -m json.tool

# Export to Alpaca format for training
make export

# Run the browser review UI to explore the data visually
make review-browser
```

For the full schema reference, see [`docs/schema.md`](schema.md).  
For annotated examples, see [`docs/examples.md`](examples.md).
