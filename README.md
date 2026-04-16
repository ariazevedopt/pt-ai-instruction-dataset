# LusoSupport-PT

**LusoSupport-PT** is a structured **European Portuguese (pt-PT)** customer support and business operations instruction dataset designed for LLM fine-tuning, prompting experiments, evaluation, and support automation workflows.

The project focuses on realistic support-related tasks written in **Portuguese from Portugal**, with clean metadata and a format that is easy to reuse in model training, prototyping, and downstream NLP applications.

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
``
