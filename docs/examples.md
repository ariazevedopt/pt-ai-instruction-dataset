# LusoSupport-PT — Examples

This document contains **representative examples** from the LusoSupport‑PT dataset.
All examples conform to the **LusoSupport‑PT Schema v1.0** and demonstrate:

- correct PT‑PT linguistic usage
- realistic customer support scenarios
- consistent metadata and controlled vocabularies
- proper instruction / input / output alignment

All examples are **synthetic**, **safe for public release**, and meant to act as
**reference-quality samples** for both manual review and automated validation.

---

## Example 1 — Refund request (response_generation)

Domain: ecommerce  
Subdomain: returns_refunds  

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
      "instruction": "Responde ao cliente em português de Portugal, com tom empático e profissional.",
      "input": "Mensagem do cliente: Recebi a encomenda com defeito e quero devolver o produto.",
      "output": "Boa tarde. Lamentamos a situação. Para avançarmos com a devolução e o reembolso, pedimos que nos indique o número da encomenda e, se possível, envie uma fotografia do defeito.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 2 — Delivery delay (email_reply)

Domain: ecommerce  
Subdomain: delivery_delay  

    {
      "id": "lusosupport_pt_000002",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "ecommerce",
      "subdomain": "delivery_delay",
      "task_type": "email_reply",
      "customer_intent": "delivery_delay",
      "customer_tone": "calm",
      "agent_tone": "professional",
      "channel": "email",
      "difficulty": "easy",
      "instruction": "Escreve uma resposta por e-mail em português de Portugal, profissional e prestável.",
      "input": "Mensagem do cliente: A minha encomenda deveria ter sido entregue ontem e ainda não recebi novidades.",
      "output": "Boa tarde.\n\nAgradecemos o seu contacto. Para verificarmos o estado da entrega, pedimos que nos indique a referência da encomenda.\n\nCom os melhores cumprimentos,",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 3 — Subscription cancellation (email_reply)

Domain: subscriptions  
Subdomain: cancel_subscription  

    {
      "id": "lusosupport_pt_000003",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "subscriptions",
      "subdomain": "cancel_subscription",
      "task_type": "email_reply",
      "customer_intent": "cancel_subscription",
      "customer_tone": "formal",
      "agent_tone": "professional",
      "channel": "email",
      "difficulty": "easy",
      "instruction": "Redige uma resposta profissional em português de Portugal a um pedido de cancelamento.",
      "input": "Mensagem do cliente: Pretendo cancelar a minha subscrição no final do mês.",
      "output": "Boa tarde.\n\nPara procedermos ao cancelamento, pedimos que confirme o e-mail associado à conta ou a referência da subscrição.\n\nCom os melhores cumprimentos,",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 4 — Internet outage (summarization)

Domain: telecom  
Subdomain: internet_issue  

    {
      "id": "lusosupport_pt_000004",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "telecom",
      "subdomain": "internet_issue",
      "task_type": "summarization",
      "customer_intent": "technical_issue",
      "customer_tone": "frustrated",
      "agent_tone": "concise",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Resume o problema do cliente em três pontos.",
      "input": "Mensagem do cliente: Estou sem internet desde ontem à noite e trabalho a partir de casa.",
      "output": "- Problema: falta de ligação à internet.\n- Impacto: impossibilidade de trabalhar remotamente.\n- Informação em falta: confirmação de avaria na zona.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 5 — Invoice request (intent_classification)

Domain: billing_accounts  
Subdomain: invoice_request  

    {
      "id": "lusosupport_pt_000005",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "billing_accounts",
      "subdomain": "invoice_request",
      "task_type": "intent_classification",
      "customer_intent": "invoice_request",
      "customer_tone": "calm",
      "agent_tone": "professional",
      "channel": "web_form",
      "difficulty": "easy",
      "instruction": "Classifica a intenção principal do cliente.",
      "input": "Mensagem do cliente: Preciso da fatura referente a este mês.",
      "output": "{ \"intent\": \"invoice_request\", \"urgency\": \"low\", \"domain\": \"billing_accounts\" }",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 6 — Duplicate charge (response_generation)

Domain: billing_accounts  
Subdomain: duplicate_charge  

    {
      "id": "lusosupport_pt_000006",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "billing_accounts",
      "subdomain": "duplicate_charge",
      "task_type": "response_generation",
      "customer_intent": "duplicate_charge",
      "customer_tone": "frustrated",
      "agent_tone": "empathetic",
      "channel": "email",
      "difficulty": "medium",
      "instruction": "Responde ao cliente com empatia e foco na resolução.",
      "input": "Mensagem do cliente: Reparei que o mesmo valor foi cobrado duas vezes.",
      "output": "Boa tarde. Lamentamos o incómodo. Para analisarmos a situação, pedimos que nos indique a referência da cobrança para verificarmos o ocorrido.",
      "metadata": {
        "requires_escalation": true,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 7 — Password reset issue (summarization)

Domain: saas  
Subdomain: password_reset  

    {
      "id": "lusosupport_pt_000007",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "saas",
      "subdomain": "password_reset",
      "task_type": "summarization",
      "customer_intent": "password_reset",
      "customer_tone": "urgent",
      "agent_tone": "concise",
      "channel": "phone_transcript",
      "difficulty": "easy",
      "instruction": "Resume o contacto em formato estruturado.",
      "input": "Transcrição: Não consigo repor a palavra-passe e preciso de acesso urgente.",
      "output": "{ \"problema\": \"Impossibilidade de repor palavra-passe\", \"urgencia\": \"alta\", \"proximo_passo\": \"Confirmar e-mail da conta\" }",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 8 — Informal message rewrite (rewrite_professional)

Domain: saas  
Subdomain: account_access  

    {
      "id": "lusosupport_pt_000008",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "saas",
      "subdomain": "account_access",
      "task_type": "rewrite_professional",
      "customer_intent": "account_access",
      "customer_tone": "informal",
      "agent_tone": "formal",
      "channel": "email",
      "difficulty": "medium",
      "instruction": "Reescreve a mensagem de forma profissional.",
      "input": "Mensagem original: nao consigo entrar na conta, podem ajudar?",
      "output": "Boa tarde.\n\nNão consigo aceder à minha conta. Podem, por favor, indicar como resolver esta situação?\n\nObrigado.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 9 — Damaged item (next_action_suggestion)

Domain: marketplace  
Subdomain: damaged_item  

    {
      "id": "lusosupport_pt_000009",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "marketplace",
      "subdomain": "damaged_item",
      "task_type": "next_action_suggestion",
      "customer_intent": "damaged_item",
      "customer_tone": "confused",
      "agent_tone": "professional",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Indica os passos seguintes.",
      "input": "Mensagem do cliente: O artigo chegou danificado.",
      "output": "1. Solicitar a referência da encomenda.\n2. Pedir fotografias do dano.\n3. Confirmar solução pretendida.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 10 — Utility outage (urgency_classification)

Domain: utilities  
Subdomain: outage_report  

    {
      "id": "lusosupport_pt_000010",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "utilities",
      "subdomain": "outage_report",
      "task_type": "urgency_classification",
      "customer_intent": "technical_issue",
      "customer_tone": "urgent",
      "agent_tone": "professional",
      "channel": "chat",
      "difficulty": "easy",
      "instruction": "Avalia a urgência.",
      "input": "Mensagem do cliente: Estamos sem eletricidade há duas horas.",
      "output": "{ \"urgency\": \"high\" }",
      "metadata": {
        "requires_escalation": true,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 11 — Booking change (faq_answer)

Domain: travel  
Subdomain: booking_change  

    {
      "id": "lusosupport_pt_000011",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "travel",
      "subdomain": "booking_change",
      "task_type": "faq_answer",
      "customer_intent": "booking_change",
      "customer_tone": "formal",
      "agent_tone": "professional",
      "channel": "web_form",
      "difficulty": "medium",
      "instruction": "Responde à pergunta frequente.",
      "input": "Pergunta do cliente: Posso alterar a data da minha reserva?",
      "output": "A alteração da reserva depende das condições contratadas. Para confirmarmos, precisamos da referência da reserva.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 12 — Booking cancellation (intent_classification)

Domain: travel  
Subdomain: booking_cancellation  

    {
      "id": "lusosupport_pt_000012",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "travel",
      "subdomain": "booking_cancellation",
      "task_type": "intent_classification",
      "customer_intent": "booking_cancellation",
      "customer_tone": "formal",
      "agent_tone": "professional",
      "channel": "web_form",
      "difficulty": "easy",
      "instruction": "Classifica a intenção.",
      "input": "Mensagem do cliente: Quero cancelar a minha reserva.",
      "output": "{ \"intent\": \"booking_cancellation\", \"urgency\": \"medium\", \"domain\": \"travel\" }",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 13 — Plan change (faq_answer)

Domain: telecom  
Subdomain: plan_change  

    {
      "id": "lusosupport_pt_000013",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "telecom",
      "subdomain": "plan_change",
      "task_type": "faq_answer",
      "customer_intent": "change_plan",
      "customer_tone": "calm",
      "agent_tone": "professional",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Esclarece a dúvida do cliente.",
      "input": "Mensagem do cliente: Posso mudar de tarifário antes do fim do mês?",
      "output": "A alteração de tarifário pode depender das condições do seu contrato. Para confirmar, precisamos da referência do serviço.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 14 — Service activation delay (response_generation)

Domain: telecom  
Subdomain: service_activation  

    {
      "id": "lusosupport_pt_000014",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "telecom",
      "subdomain": "service_activation",
      "task_type": "response_generation",
      "customer_intent": "technical_issue",
      "customer_tone": "confused",
      "agent_tone": "professional",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Responde de forma clara e orientada para resolução.",
      "input": "Mensagem do cliente: Aderi ao serviço ontem e ainda aparece como inativo.",
      "output": "Vamos verificar o estado da ativação. Para isso, pedimos que nos indique a referência do pedido de adesão.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 15 — Account billing question (response_generation)

Domain: saas  
Subdomain: billing_question  

    {
      "id": "lusosupport_pt_000015",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "saas",
      "subdomain": "billing_question",
      "task_type": "response_generation",
      "customer_intent": "billing_question",
      "customer_tone": "confused",
      "agent_tone": "professional",
      "channel": "email",
      "difficulty": "easy",
      "instruction": "Responde com clareza ao pedido de esclarecimento.",
      "input": "Mensagem do cliente: Não consigo perceber um valor cobrado na fatura.",
      "output": "Para esclarecermos a cobrança, pedimos que nos indique a referência da fatura ou o valor em causa.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 16 — Meter reading question (faq_answer)

Domain: utilities  
Subdomain: meter_question  

    {
      "id": "lusosupport_pt_000016",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "utilities",
      "subdomain": "meter_question",
      "task_type": "faq_answer",
      "customer_intent": "technical_issue",
      "customer_tone": "calm",
      "agent_tone": "professional",
      "channel": "web_form",
      "difficulty": "easy",
      "instruction": "Responde à pergunta frequente.",
      "input": "Pergunta do cliente: Como posso submeter a leitura do contador?",
      "output": "Pode submeter a leitura através da sua área de cliente ou pelos canais de apoio indicados no site.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 17 — Order not received (response_generation)

Domain: marketplace  
Subdomain: order_not_received  

    {
      "id": "lusosupport_pt_000017",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "marketplace",
      "subdomain": "order_not_received",
      "task_type": "response_generation",
      "customer_intent": "order_status",
      "customer_tone": "concerned",
      "agent_tone": "professional",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Responde de forma clara e tranquilizadora.",
      "input": "Mensagem do cliente: O prazo de entrega já passou e ainda não recebi a encomenda.",
      "output": "Vamos verificar o estado da entrega. Para isso, pedimos que nos indique a referência da encomenda.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 18 — Payment failure (response_generation)

Domain: telecom  
Subdomain: invoice_question  

    {
      "id": "lusosupport_pt_000018",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "telecom",
      "subdomain": "invoice_question",
      "task_type": "response_generation",
      "customer_intent": "payment_failure",
      "customer_tone": "frustrated",
      "agent_tone": "empathetic",
      "channel": "chat",
      "difficulty": "medium",
      "instruction": "Responde com empatia e orientação.",
      "input": "Mensagem do cliente: O pagamento da fatura foi recusado e a data limite é hoje.",
      "output": "Compreendemos a sua preocupação. Para ajudar, pedimos que confirme a referência da fatura e a mensagem de erro apresentada.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 19 — Change account details (next_action_suggestion)

Domain: billing_accounts  
Subdomain: account_update  

    {
      "id": "lusosupport_pt_000019",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "billing_accounts",
      "subdomain": "account_update",
      "task_type": "next_action_suggestion",
      "customer_intent": "account_update",
      "customer_tone": "calm",
      "agent_tone": "professional",
      "channel": "web_form",
      "difficulty": "easy",
      "instruction": "Indica os passos a seguir para atualização de dados.",
      "input": "Mensagem do cliente: Quero atualizar os meus dados de faturação.",
      "output": "1. Confirmar a identidade do cliente.\n2. Indicar o local onde os dados podem ser atualizados.\n3. Confirmar a submissão das alterações.",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Example 20 — Complaint escalation (response_generation)

Domain: billing_accounts  
Subdomain: complaint  

    {
      "id": "lusosupport_pt_000020",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "billing_accounts",
      "subdomain": "complaint",
      "task_type": "response_generation",
      "customer_intent": "complaint",
      "customer_tone": "frustrated",
      "agent_tone": "empathetic",
      "channel": "email",
      "difficulty": "hard",
      "instruction": "Responde a uma reclamação com empatia e foco em encaminhamento adequado.",
      "input": "Mensagem do cliente: Esta situação já se repete e continuo sem resposta.",
      "output": "Lamentamos a situação e compreendemos a sua insatisfação. Vamos encaminhar o caso para análise prioritária e entraremos em contacto assim que possível.",
      "metadata": {
        "requires_escalation": true,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## Final notes

- Total examples: 20
- All examples are PT‑PT, synthetic, and schema‑compliant.
- These examples define the **reference quality bar** for the dataset.

End of examples.
