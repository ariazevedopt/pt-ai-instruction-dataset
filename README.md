# LusoSupport-PT

**LusoSupport-PT** is a structured **European Portuguese (pt-PT)** customer support and business operations instruction dataset designed for LLM fine-tuning, prompting experiments, evaluation, and support automation workflows.

The project focuses on realistic support-related tasks written in **Portuguese from Portugal**, with clean metadata and a format that is easy to reuse in model training, prototyping, and downstream NLP applications.

→ **[Use cases, value & integration guide](docs/use-cases.md)** — fine-tuning, RAG, classification pipelines, code examples  
→ **[Full integration guide](docs/integration.md)** — Unsloth, LLaMA-Factory, OpenAI, LangChain, ChromaDB, evaluation

---

## Get the Dataset

| Tier | Price | Rows | Licence |
|---|---|---|---|
| 🆓 **[Lite (Hugging Face)](https://huggingface.co/datasets/ariazevedopt/LusoSupport-PT)** | Free | 200 | CC BY 4.0 |
| 💼 **[Premium Individual (Gumroad)](https://gumroad.com/l/lusosupport-pt)** | €39 | 5 163 | Personal / research |
| 🏢 **[Commercial Licence (Gumroad)](https://gumroad.com/l/lusosupport-pt-commercial)** | €149 | 5 163 | Commercial use |

❤️ [Sponsor this project on GitHub](https://github.com/sponsors/ariazevedopt)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline (generate → validate → deduplicate → save)
make pipeline

# Or run individual steps
make generate    # generate 100 synthetic rows → datasets/interim/
make validate    # validate datasets/processed/lusosupport_pt_v1.jsonl
make stats       # print dataset composition stats
make export      # export to CSV + Alpaca JSONL
```

The ready-to-use dataset is at `datasets/processed/lusosupport_pt_v1.jsonl`.  
High-quality hand-crafted seed examples are in `datasets/raw/seed_examples.jsonl`.

---

## Overview

Many publicly available Portuguese datasets are either:

- broad generic corpora,
- academic/benchmark resources,
- heavily oriented toward Brazilian Portuguese (`pt-BR`),
- or insufficiently structured for practical support automation.

**LusoSupport-PT** addresses that gap by providing a **pt-PT-first dataset** focused on realistic business-support scenarios such as:

- customer response generation
- support email drafting
- issue summarisation
- intent detection
- urgency detection
- next-action suggestion
- rewriting informal messages into professional PT-PT
- FAQ-style support answering

The dataset is intended to be small enough to build and maintain iteratively, but structured enough to become a reusable asset for multiple AI and automation use cases.

---

## Objectives

### Primary objective
Publish a high-quality **European Portuguese support-oriented dataset** on GitHub and Hugging Face.

### Secondary objectives
- learn practical dataset design and curation
- create a reusable dataset-generation workflow
- build public credibility in AI/data work
- create a foundation for future monetisation:
  - sponsorships
  - donations
  - commercial adaptation
  - custom vertical slices
  - follow-on dataset work

---

## Target users

This dataset is designed for:

- developers building **Portuguese-language support assistants**
- teams experimenting with **LLM fine-tuning**
- builders creating **chatbots and helpdesk copilots**
- freelancers or consultants needing structured PT-PT support data
- researchers and practitioners evaluating Portuguese support-oriented tasks

---

## Scope

### Included domains

Version 1 includes examples across the following business-support domains:

- `ecommerce`
- `subscriptions`
- `saas`
- `telecom`
- `utilities`
- `travel`
- `marketplace`
- `billing_accounts`

### Included task types

The initial release supports the following task families:

- `response_generation`
- `email_reply`
- `summarization`
- `intent_classification`
- `urgency_classification`
- `rewrite_professional`
- `next_action_suggestion`
- `faq_answer`

### Included customer situations

Examples may include scenarios such as:

- refund requests
- delivery delays
- damaged products
- account access problems
- password reset issues
- billing questions
- invoice requests
- booking changes
- cancellation requests
- duplicate charges
- service interruptions
- complaint handling

---

## Out of scope for v1

To keep the first version coherent, safe, and realistic to produce within a limited time budget, the following areas are excluded:

- medical advice
- legal advice
- tax advice
- investment advice
- highly regulated compliance content
- real personal data
- company-specific policies presented as facts without context
- abusive or extreme harmful content
- domain content requiring specialist professional certification

---

## Language policy

### Version 1
- **Primary language:** Portuguese
- **Variant:** `pt-PT` (Portuguese from Portugal)

### Important consistency rule
Version 1 **does not mix** `pt-PT` and `pt-BR` in the same dataset release.

This is intentional:
- to preserve linguistic consistency
- to simplify validation
- to create a clear differentiation angle
- to make future variant expansion cleaner

### Possible future versions
Future releases may include:
- `pt-BR` as a separate split or version
- bilingual PT-PT ↔ EN subsets
- industry-specific subsets
- multi-turn conversation variants

---

## Dataset design principles

LusoSupport-PT follows these principles:

### 1. Practicality over scale
The goal is not to create a massive generic corpus, but a structured dataset that is immediately useful for applied AI work.

### 2. PT-PT linguistic consistency
Outputs should reflect **European Portuguese** conventions wherever possible.

Examples:
- `fatura` instead of `nota fiscal`
- `palavra-passe` instead of `senha`
- `telemóvel` instead of `celular`
- `encomenda` instead of Brazilian-style order wording in many support contexts

### 3. Structure over raw text
Every row includes metadata describing:
- domain
- task type
- customer intent
- tone
- channel
- difficulty
- safety-related metadata

This makes the dataset easier to filter, extend, validate, and repurpose.

### 4. Safe and reusable examples
The dataset avoids:
- real personal data
- regulated advice
- sensitive identifiable information
- fabricated claims not supported by context

### 5. Reproducibility
The project is designed so that examples can be generated, cleaned, validated, and versioned in a repeatable way.

---

## Dataset format

Each example is stored as a JSON object.

### Canonical row structure

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
  "instruction": "Responde ao cliente em português de Portugal, com tom empático e profissional. Explica os próximos passos sem inventar políticas não fornecidas.",
  "input": "Mensagem do cliente: \"Recebi a encomenda há 3 dias e o artigo veio com defeito. Pretendo devolver o produto e receber o reembolso.\" Contexto: \"Política resumida: devoluções aceites no prazo de 30 dias mediante prova de compra.\"",
  "output": "Lamentamos a situação. Podemos ajudar no processo de devolução e reembolso. Para avançarmos, por favor envie o número da encomenda e, se possível, uma fotografia do defeito. Após validação, indicaremos os passos seguintes para a devolução e o respetivo reembolso, de acordo com a política em vigor.",
  "metadata": {
    "requires_escalation": false,
    "contains_pii": false,
    "synthetic": true,
    "source_type": "manual_seed"
  }
}
```

### Field reference

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique row ID (`lusosupport_pt_NNNNNN` or `browser_generated_<ms>`) |
| `language` | string | Always `"pt"` |
| `variant` | string | Always `"pt-PT"` |
| `domain` | string | Business domain (e.g. `ecommerce`, `travel`) |
| `subdomain` | string | More specific area within the domain |
| `task_type` | string | NLP task family (e.g. `response_generation`, `summarization`) |
| `customer_intent` | string | What the customer wants (e.g. `refund_request`, `password_reset`) |
| `customer_tone` | string | `calm`, `frustrated`, `formal`, `angry` |
| `agent_tone` | string | `professional`, `empathetic`, `neutral` |
| `channel` | string | `chat`, `email`, `web_form`, `phone_transcript` |
| `difficulty` | string | `easy`, `medium`, `hard` |
| `instruction` | string | System prompt / task instruction (PT-PT) |
| `input` | string | Customer message, prefixed with `Mensagem do cliente:` |
| `output` | string | Model-expected agent response or classification output |
| `metadata` | object | `requires_escalation`, `contains_pii`, `synthetic`, `source_type` |

---

## Development workflow

### Prerequisites

```bash
pip install -r requirements.txt   # installs faker, pandas, datasets
```

### Full pipeline

```bash
make pipeline      # generate → validate → deduplicate → save (datasets/processed/)
```

### Individual steps

```bash
make generate      # generate synthetic rows → datasets/interim/generated.jsonl
make validate      # validate datasets/processed/lusosupport_pt_v1.jsonl (15 rules)
make dedupe        # remove duplicate rows
make stats         # print dataset composition breakdown
make export        # export to CSV + Alpaca JSONL → datasets/exports/
```

### Quality loop

```bash
make flag          # scan for issues → datasets/feedback/flagged.jsonl
make review        # interactive terminal review of flagged rows
make review-random # interactive terminal review of random rows
make quality       # rich quality report (flag reasons, weakest combos)
```

#### Feedback files

| File | Purpose |
|------|---------|
| `datasets/feedback/flagged.jsonl` | Rows flagged by `make flag` for review |
| `datasets/feedback/approved.jsonl` | Rows manually approved (excluded from future flagging) |
| `datasets/feedback/rejected.jsonl` | Rows rejected (excluded from pipeline on next run) |
| `datasets/feedback/browser_ratings.jsonl` | Unclear/browser-generated ratings |
| `datasets/feedback/corrections.jsonl` | Corrected row inputs |

### Browser review UI

The easiest way to review and rate dataset rows:

```bash
make review-browser    # starts http://localhost:8765 and opens browser
```

**Browse tab** — sample random or flagged rows and rate them:

| Rating | Meaning | Saved to |
|--------|---------|----------|
| ✅ Good | Correct PT-PT, on-topic, well-formed | `approved.jsonl` |
| ❓ Unclear | Borderline — needs more thought | `browser_ratings.jsonl` |
| ❌ Bad | Wrong domain/intent, bad PT-PT, stub output (comment required) | `rejected.jsonl` |

**Generate & Test tab** — type a customer message + choose domain/task/intent → see what the system outputs → rate it.

See [`docs/browser-review-guide.md`](docs/browser-review-guide.md) for the full guide.

### After a review session

```bash
make flag       # refresh flagged list (approved rows excluded automatically)
make pipeline   # rebuild processed dataset (rejected rows excluded)
make quality    # check updated quality report
```

### Running tests

```bash
make test       # runs all tests (pytest)
```

### Clean build

```bash
make clean      # removes datasets/interim/ and datasets/exports/
```

---

## Project structure

```
pt-ai-instruction-dataset/
├── datasets/
│   ├── raw/
│   │   └── seed_examples.jsonl        # 64 hand-crafted seed rows
│   ├── interim/
│   │   └── generated.jsonl            # pipeline intermediate output
│   ├── processed/
│   │   └── lusosupport_pt_v1.jsonl    # clean final dataset
│   ├── exports/
│   │   ├── lusosupport_pt_v1.csv      # CSV export
│   │   └── lusosupport_pt_v1_alpaca.jsonl  # Alpaca-format export
│   └── feedback/
│       ├── flagged.jsonl
│       ├── approved.jsonl
│       ├── rejected.jsonl
│       ├── corrections.jsonl
│       └── browser_ratings.jsonl
├── scripts/
│   ├── config.py           # domains, task types, intents
│   ├── scenarios.py        # input message variants per intent
│   ├── templates.py        # instruction templates
│   ├── responses.py        # output templates (response_generation etc.)
│   ├── generate.py         # row generation logic
│   ├── validate.py         # 15-rule row validator
│   ├── pipeline.py         # full pipeline orchestrator
│   ├── flag.py             # automated quality scanner
│   ├── review.py           # interactive terminal review tool
│   ├── quality_report.py   # rich quality report
│   └── review_server.py    # browser review UI server
├── tests/                  # pytest test suite (54 tests)
├── docs/
│   └── browser-review-guide.md
├── Makefile
└── requirements.txt
```

---

## Makefile reference

| Target | Description |
|--------|-------------|
| `make pipeline` | Full generate → validate → dedupe → save cycle |
| `make generate` | Generate synthetic rows |
| `make validate` | Validate processed dataset |
| `make dedupe` | Remove duplicates |
| `make stats` | Dataset composition stats |
| `make export` | Export to CSV + Alpaca JSONL |
| `make flag` | Scan for quality issues |
| `make review` | Interactive terminal review of flagged rows |
| `make review-random` | Interactive terminal review of random rows |
| `make quality` | Rich quality report |
| `make review-browser` | Launch browser review UI at http://localhost:8765 |
| `make test` | Run test suite |
| `make clean` | Remove interim and export files |
