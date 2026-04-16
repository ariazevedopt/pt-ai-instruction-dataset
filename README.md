# LusoSupport-PT

**LusoSupport-PT** is an European Portuguese (**pt-PT**) customer support and business operations instruction dataset designed for LLM fine-tuning, prompting experiments, evaluation, and support automation workflows.

## Goal

This dataset aims to provide high-quality, structured **pt-PT** examples for realistic support-related tasks such as:

- customer response generation
- support email drafting
- issue summarisation
- intent classification
- urgency classification
- next-action suggestion
- rewriting informal messages into professional Portuguese

The objective is to create a practical dataset that is useful for developers building:

- support assistants
- chatbots
- helpdesk copilots
- customer email automation tools
- Portuguese-language instruction-tuned models

---

## Why this dataset exists

Public Portuguese datasets are stronger in broad corpora and Brazilian Portuguese general instruction data than in practical **European Portuguese support instruction datasets**.

**LusoSupport-PT** focuses on:
- **pt-PT first**
- practical business-support scenarios
- clean metadata
- reusable instruction format
- transparent synthetic/manual creation process

---

## Scope

### Included domains
- ecommerce
- subscriptions
- SaaS
- telecom
- utilities
- travel
- marketplace
- billing and account support

### Included task types
- `response_generation`
- `email_reply`
- `summarization`
- `intent_classification`
- `urgency_classification`
- `rewrite_professional`
- `next_action_suggestion`
- `faq_answer`

### Excluded from v1
- medical advice
- legal advice
- tax advice
- investment advice
- real personal data
- company-specific policy claims not provided in context

---

## Dataset format

Each example is stored as a JSON object with structured metadata.

### Example

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
