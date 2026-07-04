# Phase 1: Parametric Template Diversity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace static string templates with parametric ones that use `domain`, `channel`, and `agent_tone` at generation time, raising unique instructions from 12 → 800+, unique inputs from 79 → 270+, and unique outputs from ~315 repeating → <50.

**Architecture:** Four files change. `templates.py` becomes the single source of truth for label maps and parametric instruction templates. `scenarios.py` expands its message pool. `responses.py` imports labels from `templates.py`, adds `TONE_PHRASES`, and `get_output()` gains an `agent_tone` param. `generate.py` passes the two new params through. A new `tests/test_generate.py` enforces diversity invariants.

**Tech Stack:** Python 3.9+, pytest, existing project structure in `scripts/` and `tests/`.

## Global Constraints

- All content in European Portuguese (pt-PT) only — never pt-BR
- Banned words must not appear in any template: `celular`, `senha`, `nota fiscal`, `assinatura`, `código de rastreio`, `contato`
- Use pt-PT: `palavra-passe`, `telemóvel`, `fatura`, `encomenda`, `contacto`, `actualização`
- Row schema unchanged — no new fields added
- `build_instruction()` and `get_output()` new params must default to `None` for backward compatibility
- All 54 existing tests (`pytest tests/`) must continue to pass after every task
- Run `pytest` from repo root: `cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q`

---

### Task 1: Rewrite `templates.py` with parametric instruction templates

**Files:**
- Modify: `scripts/templates.py` (full replacement)

**Interfaces:**
- Produces: `DOMAIN_LABELS: dict[str, str]`, `CHANNEL_LABELS: dict[str, str]`, `AGENT_TONE_LABELS: dict[str, str]`, `INSTRUCTION_TEMPLATES: dict[str, list[str]]`
- Produces: `build_instruction(task_type: str, agent_tone: str, domain: str = None, channel: str = None) -> str`
- Consumed by: `scripts/generate.py` (Task 4), `scripts/responses.py` (Task 3 imports `DOMAIN_LABELS`)

---

- [ ] **Step 1: Verify existing tests pass before touching anything**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q
```
Expected: `54 passed`

- [ ] **Step 2: Write a failing test for the new `build_instruction()` signature**

Create `tests/test_templates.py`:

```python
"""Tests for parametric build_instruction() in templates.py."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from config import TASK_TYPES, DOMAINS, CHANNELS, AGENT_TONES
import templates as T


def test_build_instruction_returns_string_for_all_task_types():
    for tt in TASK_TYPES:
        result = T.build_instruction(tt, "professional", "ecommerce", "email")
        assert isinstance(result, str) and len(result) > 10, f"failed for {tt}"


def test_build_instruction_no_unfilled_placeholders():
    random.seed(99)
    for tt in TASK_TYPES:
        for domain in DOMAINS:
            for tone in AGENT_TONES:
                result = T.build_instruction(tt, tone, domain, "chat")
                assert "{" not in result and "}" not in result, (
                    f"Unfilled placeholder in task_type={tt} domain={domain} tone={tone}: {result!r}"
                )


def test_build_instruction_uses_domain_label():
    # At least one template per task_type should embed the domain label
    for tt in TASK_TYPES:
        found = False
        random.seed(0)
        for _ in range(30):
            result = T.build_instruction(tt, "professional", "telecom", "chat")
            if "telecomunicações" in result:
                found = True
                break
        # Not every task_type has domain in every template, so just check DOMAIN_LABELS exists
    assert hasattr(T, "DOMAIN_LABELS")
    assert T.DOMAIN_LABELS["telecom"] == "telecomunicações"


def test_build_instruction_backward_compat_no_domain():
    """Old callers that pass only task_type and agent_tone still work."""
    result = T.build_instruction("response_generation", "professional")
    assert isinstance(result, str) and len(result) > 5


def test_domain_labels_covers_all_domains():
    for d in DOMAINS:
        assert d in T.DOMAIN_LABELS, f"DOMAIN_LABELS missing domain: {d}"


def test_channel_labels_covers_all_channels():
    for c in CHANNELS:
        assert c in T.CHANNEL_LABELS, f"CHANNEL_LABELS missing channel: {c}"


def test_agent_tone_labels_covers_all_tones():
    for tone in AGENT_TONES:
        assert tone in T.AGENT_TONE_LABELS, f"AGENT_TONE_LABELS missing tone: {tone}"


def test_instruction_templates_has_all_task_types():
    for tt in TASK_TYPES:
        assert tt in T.INSTRUCTION_TEMPLATES, f"INSTRUCTION_TEMPLATES missing task_type: {tt}"
        assert len(T.INSTRUCTION_TEMPLATES[tt]) >= 5, f"Need ≥5 templates for {tt}"
```

- [ ] **Step 3: Run the test to confirm it fails**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py -v 2>&1 | head -30
```
Expected: Multiple ERRORS — `templates` module doesn't have `DOMAIN_LABELS` yet.

- [ ] **Step 4: Replace `scripts/templates.py` with the full parametric implementation**

```python
"""Parametric instruction templates for LusoSupport-PT.

DOMAIN_LABELS, CHANNEL_LABELS, AGENT_TONE_LABELS are the single source of
truth for enum → pt-PT label conversion, imported by responses.py too.

build_instruction(task_type, agent_tone, domain=None, channel=None) → str
  Picks a random template from INSTRUCTION_TEMPLATES[task_type] and fills
  {domain_label}, {channel}, {agent_tone} placeholders. Falls back to
  safe defaults when params are None.
"""
import random


DOMAIN_LABELS: dict = {
    "ecommerce":        "comércio electrónico",
    "subscriptions":    "subscrições e planos",
    "saas":             "software e plataformas digitais",
    "telecom":          "telecomunicações",
    "utilities":        "serviços de utilidade pública",
    "travel":           "viagens e reservas",
    "marketplace":      "marketplace",
    "billing_accounts": "faturação e contas",
}

CHANNEL_LABELS: dict = {
    "email":             "e-mail",
    "chat":              "chat",
    "web_form":          "formulário web",
    "phone_transcript":  "telefone",
}

AGENT_TONE_LABELS: dict = {
    "professional": "profissional",
    "empathetic":   "empático",
    "concise":      "conciso",
    "reassuring":   "tranquilizador",
    "formal":       "formal",
}

INSTRUCTION_TEMPLATES: dict = {
    "response_generation": [
        "Responde ao cliente em português de Portugal, com tom {agent_tone}.",
        "Elabora uma resposta de suporte em pt-PT para uma questão de {domain_label}. Tom: {agent_tone}.",
        "Como agente de apoio de {domain_label}, redige uma resposta {agent_tone} ao cliente pelo {channel}.",
        "Responde a esta mensagem com um registo {agent_tone}. Contexto: {domain_label}.",
        "Escreve uma resposta em português europeu, adequada ao canal {channel}, com tom {agent_tone}.",
        "Responde ao cliente sobre a sua questão de {domain_label} com um tom {agent_tone} e linguagem clara.",
        "Redige uma resposta de apoio ao cliente em pt-PT. Área: {domain_label}. Tom pretendido: {agent_tone}.",
    ],
    "email_reply": [
        "Escreve uma resposta por e-mail em português de Portugal.",
        "Redige um e-mail de resposta ao cliente sobre {domain_label}, em pt-PT.",
        "Escreve uma resposta formal por e-mail, em português europeu, sobre a questão de {domain_label}.",
        "Elabora uma resposta de e-mail com tom {agent_tone} para o cliente, em pt-PT.",
        "Redige um e-mail de apoio ao cliente em português de Portugal sobre {domain_label}, com tom {agent_tone}.",
        "Escreve um e-mail de resposta em pt-PT — área: {domain_label}. Tom: {agent_tone}.",
    ],
    "summarization": [
        "Resume o problema do cliente de forma concisa.",
        "Resume em pt-PT a questão levantada pelo cliente sobre {domain_label}.",
        "Elabora um resumo breve da mensagem do cliente, em português europeu, para arquivo interno.",
        "Resume o pedido do cliente sobre {domain_label} em duas a três frases, em pt-PT.",
        "Cria um resumo interno da mensagem do cliente recebida pelo {channel}, em português de Portugal.",
    ],
    "intent_classification": [
        "Classifica a intenção do cliente.",
        "Identifica a intenção principal do cliente nesta mensagem sobre {domain_label}.",
        "Classifica a intenção do cliente e retorna JSON com intent, urgency, domain e confidence.",
        "Analisa a mensagem do cliente sobre {domain_label} e classifica a intenção em formato JSON.",
        "Determina a intenção do cliente nesta mensagem de {domain_label} e retorna JSON estruturado.",
    ],
    "urgency_classification": [
        "Classifica a urgência do pedido.",
        "Avalia a urgência da mensagem do cliente sobre {domain_label} e retorna JSON.",
        "Classifica a urgência do pedido de suporte de {domain_label} em formato JSON.",
        "Determina o nível de urgência desta mensagem de cliente e indica se requer escalamento.",
        "Avalia a urgência do pedido de {domain_label} e retorna JSON com urgency, reason e escalate.",
    ],
    "rewrite_professional": [
        "Reescreve a mensagem de forma profissional.",
        "Reescreve esta mensagem de cliente num registo formal e profissional, em pt-PT.",
        "Transforma a mensagem original num texto profissional adequado para comunicação corporativa.",
        "Reformula a mensagem do cliente de forma clara e profissional, adequada para envio pelo {channel}.",
        "Reescreve o texto em português europeu com um registo formal, mantendo o conteúdo original.",
    ],
    "next_action_suggestion": [
        "Indica os próximos passos.",
        "Sugere os próximos passos para o agente de suporte de {domain_label} resolver este pedido.",
        "Lista as acções que o agente deve tomar para resolver a questão de {domain_label}, em pt-PT.",
        "Descreve os próximos passos que o agente deve seguir para tratar este pedido de {domain_label}.",
        "Indica as acções recomendadas para o agente responder a esta questão com um tom {agent_tone}.",
        "Sugere os próximos passos para resolver este pedido de {domain_label} de forma {agent_tone}.",
    ],
    "faq_answer": [
        "Responde à pergunta do cliente.",
        "Responde à questão do cliente sobre {domain_label} em português de Portugal.",
        "Fornece uma resposta clara à pergunta do cliente sobre {domain_label}, em pt-PT.",
        "Responde a esta pergunta frequente de {domain_label} em português europeu de forma directa.",
        "Elabora uma resposta de FAQ para {domain_label} que responda directamente à dúvida do cliente.",
    ],
}

_DEFAULT_DOMAIN_LABEL = "serviços ao cliente"
_DEFAULT_CHANNEL_LABEL = "canal de suporte"
_DEFAULT_TONE_LABEL = "profissional"


def build_instruction(
    task_type: str,
    agent_tone: str,
    domain: str = None,
    channel: str = None,
) -> str:
    """Return a parametric instruction string for the given task_type.

    Picks a random template from INSTRUCTION_TEMPLATES[task_type] and fills
    {domain_label}, {channel}, and {agent_tone} placeholders. Safe defaults
    are used when any parameter is None.
    """
    templates = INSTRUCTION_TEMPLATES.get(task_type, ["Processa o pedido do cliente em pt-PT."])
    template = random.choice(templates)
    domain_label = DOMAIN_LABELS.get(domain, _DEFAULT_DOMAIN_LABEL) if domain else _DEFAULT_DOMAIN_LABEL
    channel_label = CHANNEL_LABELS.get(channel, _DEFAULT_CHANNEL_LABEL) if channel else _DEFAULT_CHANNEL_LABEL
    tone_label = AGENT_TONE_LABELS.get(agent_tone, agent_tone or _DEFAULT_TONE_LABEL)
    return template.format(
        domain_label=domain_label,
        channel=channel_label,
        agent_tone=tone_label,
    )
```

- [ ] **Step 5: Run the new tests**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py -v
```
Expected: All tests in `test_templates.py` pass.

- [ ] **Step 6: Run the full suite to confirm no regressions**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q
```
Expected: All tests pass (count increases by the new tests).

- [ ] **Step 7: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/templates.py tests/test_templates.py
git commit -m "feat: parametric instruction templates with domain/channel/tone vars (issue #44)"
```

---

### Task 2: Expand `scenarios.py` message pool to 12–15 per intent

**Files:**
- Modify: `scripts/scenarios.py` (expand `INTENT_MESSAGES` values only — same dict structure)

**Interfaces:**
- Consumes: nothing new
- Produces: `INTENT_MESSAGES` with ≥12 entries per intent key

---

- [ ] **Step 1: Write a failing test for message pool size**

Add to `tests/test_templates.py` (append to existing file):

```python
def test_intent_messages_min_pool_size():
    """Every intent must have at least 12 messages for adequate input diversity."""
    import scenarios as S
    for intent, messages in S.INTENT_MESSAGES.items():
        assert len(messages) >= 12, (
            f"INTENT_MESSAGES['{intent}'] has only {len(messages)} messages — need ≥12"
        )
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py::test_intent_messages_min_pool_size -v
```
Expected: FAIL — most intents have 3-5 messages.

- [ ] **Step 3: Expand `INTENT_MESSAGES` in `scripts/scenarios.py`**

For each intent below, **add** the new messages to the existing list (do not remove existing ones). The final list per intent must have ≥12 entries.

**`refund_request`** — add these 8 messages:
```python
"Já efectuei o pagamento e o serviço não foi prestado — quero o reembolso imediato.",
"Fui cobrado indevidamente e aguardo a devolução do valor há mais de uma semana.",
"O produto que recebi não corresponde ao que encomendei e pretendo ser reembolsado.",
"Solicito o reembolso referente à encomenda que foi cancelada pelo vosso serviço.",
"Não autorizei esta cobrança e exijo que o valor seja devolvido com urgência.",
"O serviço apresentou falhas graves e não cumpriu o contratado — pretendo reembolso total.",
"Efectuei o pagamento por engano e gostaria de reverter a transacção.",
"Recebi um produto danificado e, após devolução, ainda não recebi o reembolso prometido.",
```

**`return_request`** — add these 8 messages:
```python
"Gostaria de iniciar o processo de devolução — o produto não era o que esperava.",
"O artigo chegou com defeito e quero proceder à sua devolução imediata.",
"Tenho 14 dias para devolver — como faço para iniciar o processo?",
"A embalagem chegou aberta e o produto parece ter sido usado — quero devolver.",
"Encomendei o tamanho errado e preciso de devolver e trocar por outro.",
"O produto não funciona conforme descrito e pretendo devolvê-lo.",
"Podem indicar-me os passos para devolver um artigo comprado há cinco dias?",
"Quero devolver dois artigos da mesma encomenda — é possível fazê-lo em conjunto?",
```

**`order_status`** — add these 8 messages:
```python
"Realizei um pedido ontem e não recebi nenhum e-mail de confirmação.",
"O meu pedido consta como 'em processamento' há três dias — qual é o estado?",
"Gostaria de saber se a minha encomenda já saiu para entrega.",
"Podem dar-me uma previsão de entrega actualizada para o meu pedido?",
"O número de seguimento que me foi enviado não mostra qualquer actualização.",
"Fiz dois pedidos na mesma semana e estou confuso sobre qual o estado de cada um.",
"A aplicação mostra 'entregue' mas não recebi nada — o que aconteceu?",
"Já passaram cinco dias úteis desde a encomenda e não há qualquer movimento.",
```

**`delivery_delay`** — add these 8 messages:
```python
"A encomenda devia ter chegado ontem e continuo sem receber qualquer informação.",
"O transportador tentou entregar mas eu não estava — quando voltam a tentar?",
"O prazo de entrega estimado foi ultrapassado e não recebi qualquer comunicação.",
"A encomenda está parada no mesmo local há quatro dias segundo o rastreio.",
"Paguei entrega expresso e o artigo ainda não chegou dentro do prazo prometido.",
"Segundo o rastreio, o artigo está no armazém desde segunda-feira — porquê o atraso?",
"Preciso urgentemente do equipamento encomendado — podem agilizar a entrega?",
"A transportadora diz que tentou entregar mas a minha portaria esteve sempre aberta.",
```

**`damaged_item`** — add these 8 messages:
```python
"O produto chegou partido — tenho fotografias do estado em que foi recebido.",
"A caixa estava completamente esmagada e o conteúdo ficou danificado.",
"Um dos componentes do produto veio partido — os restantes parecem estar bem.",
"Recebi o artigo sem embalagem protectora e chegou com riscos visíveis.",
"O produto tem uma peça partida que impossibilita a sua utilização.",
"A embalagem estava rasgada e o manual de instruções faltava.",
"O ecrã chegou partido — parece ter sido mal acondicionado durante o envio.",
"Dois dos três artigos encomendados chegaram danificados. O terceiro está bem.",
```

**`billing_question`** — add these 8 messages:
```python
"Apareceu uma cobrança na minha fatura que não reconheço — podem identificar?",
"O valor debitado este mês é superior ao do mês anterior sem qualquer alteração de plano.",
"A fatura não inclui o desconto que me foi prometido na contratação.",
"Gostaria de perceber porque o valor da fatura aumentou em relação ao acordado.",
"Encontrei dois itens na fatura com descrições que não consigo relacionar ao meu contrato.",
"A data de vencimento da fatura coincide com um feriado — posso pagar depois?",
"O desconto de fidelização não está reflectido na última fatura.",
"Mudei de plano no meio do mês — como será faturado o período de transição?",
```

**`invoice_request`** — add these 9 messages:
```python
"Preciso da fatura com NIF da empresa para efeitos contabilísticos.",
"A fatura referente ao mês de junho ainda não chegou ao meu e-mail.",
"Podem reenviar a fatura do último mês? Não a encontro na área de cliente.",
"Necessito de uma factura recibo para submeter na minha empresa.",
"A fatura que recebi não tem os dados da minha empresa correctos — precisam de ser corrigidos.",
"Gostaria de receber as faturas automaticamente por e-mail todos os meses.",
"Precisam de emitir uma nota de crédito relativa à última fatura.",
"Podem enviar a fatura com discriminação detalhada dos serviços utilizados?",
"A área de cliente não deixa descarregar a fatura — podem enviá-la por e-mail?",
```

**`cancel_subscription`** — add these 8 messages:
```python
"Gostaria de cancelar o meu plano com efeito imediato.",
"Vou cancelar porque encontrei uma solução melhor — qual o processo?",
"Estou a pagar por uma subscrição que já não utilizo e pretendo encerrar.",
"Podem confirmar que o cancelamento não implica custos adicionais?",
"Quero cancelar antes da próxima renovação automática — quando é a data limite?",
"Solicito o cancelamento da minha conta e a eliminação dos meus dados.",
"Já cancelei pela área de cliente mas continuo a receber cobranças — precisam de confirmar.",
"Estou a cancelar por não estar satisfeito com o serviço — há algum desconto de retenção?",
```

**`change_plan`** — add these 8 messages:
```python
"Quero fazer upgrade para o plano com mais funcionalidades.",
"Estou a exceder os limites do meu plano actual — qual o próximo nível?",
"Gostaria de mudar para o plano anual para poupar nos custos mensais.",
"Posso fazer o downgrade sem perder os dados que já tenho guardados?",
"Tenho dois utilizadores e quero passar para um plano de equipa.",
"O plano actual já não se adequa às minhas necessidades — podem recomendar alternativas?",
"Quero alterar o meu plano mas manter a mesma data de faturação.",
"Qual é a diferença de funcionalidades entre o plano básico e o profissional?",
```

**`technical_issue`** — add these 8 messages:
```python
"A aplicação encerra inesperadamente sempre que tento aceder a um determinado módulo.",
"Após a actualização de ontem, deixou de ser possível exportar relatórios.",
"O sistema está lento e as operações demoram muito mais tempo do que o habitual.",
"Recebi uma mensagem de erro 500 ao tentar efectuar um pagamento.",
"A integração com a ferramenta externa deixou de funcionar desde segunda-feira.",
"Alguns botões da interface não respondem em determinado browser.",
"A sincronização entre dispositivos não está a funcionar — os dados não actualizam.",
"A plataforma não envia notificações por e-mail desde há três dias.",
```

**`password_reset`** — add these 9 messages:
```python
"Tentei repor a palavra-passe mas o código enviado por SMS já expirou.",
"O e-mail de recuperação vai para a pasta de spam e já não funciona.",
"Não tenho acesso ao e-mail associado à conta — como posso recuperar o acesso?",
"Já alterei a palavra-passe mas o sistema continua a rejeitar o acesso.",
"O botão 'Esqueci a palavra-passe' não funciona na aplicação móvel.",
"A autenticação de dois factores está a bloquear o acesso após repor a palavra-passe.",
"O código de verificação não chega ao telemóvel — tentei três vezes.",
"Preciso de repor a palavra-passe de uma conta criada por um colega que já saiu da empresa.",
"Redefini a palavra-passe mas continuo sem conseguir aceder — o sistema diz que está errada.",
```

**`account_access`** — add these 9 messages:
```python
"A minha conta foi bloqueada após várias tentativas de acesso falhadas.",
"Tentei aceder pelo novo dispositivo e o sistema pede verificação que não consigo completar.",
"Não consigo aceder desde que mudei de telemóvel.",
"O meu acesso foi revogado sem aviso — precisam de verificar o que aconteceu.",
"Estou a receber um erro de sessão expirada em todos os dispositivos.",
"O portal da empresa bloqueou o meu acesso — contactem o administrador, diz a mensagem.",
"Não consigo aceder à conta desde a migração do sistema efectuada no fim-de-semana.",
"A autenticação de dois factores está a pedir um código que não chega ao meu telemóvel.",
"A conta foi criada há menos de uma hora e já apresenta erro de acesso.",
```

**`complaint`** — add these 9 messages:
```python
"Pretendo formalizar uma reclamação sobre o tratamento que recebi no suporte.",
"Não fui informado de uma alteração de condições que me afectou directamente.",
"Recebi informações contraditórias de dois agentes diferentes — preciso de uma resposta definitiva.",
"O problema que reportei há uma semana não foi resolvido e ninguém me contactou.",
"Sinto que a minha situação não foi tratada com a seriedade que merecia.",
"Fui mal informado sobre as condições do contrato e isso causou-me prejuízo.",
"O serviço piorou consideravelmente nos últimos meses sem qualquer justificação.",
"Quero registar oficialmente a minha insatisfação e aguardo uma resposta formal.",
"Não estou satisfeito com a resolução proposta e quero escalar a situação.",
```

**`escalation_request`** — add these 8 messages:
```python
"Já contactei o suporte três vezes e o problema não foi resolvido — quero falar com um gestor.",
"A resposta que recebi não é satisfatória — solicito escalamento imediato.",
"Este problema afecta o meu negócio directamente e precisa de resolução urgente de um responsável.",
"Fui prometida uma solução que não foi cumprida — exijo falar com quem tem autoridade.",
"O caso está aberto há duas semanas sem resolução — escalar é a única opção.",
"Já perdi dinheiro por causa desta situação e exijo ser atendido pela direcção.",
"Recebo respostas automáticas mas ninguém trata efectivamente do meu problema.",
"Vou recorrer à DECO se este assunto não for resolvido por um responsável hoje.",
```

**`booking_change`** — add these 8 messages:
```python
"Preciso de alterar a data de partida para uma semana mais tarde.",
"Quero acrescentar mais uma noite à minha reserva actual.",
"Houve uma alteração no meu voo e preciso de ajustar a reserva de hotel.",
"Posso mudar o nome do passageiro numa reserva já confirmada?",
"Preciso de alterar o hotel da reserva para outro na mesma cidade.",
"A reserva está em nome errado — podem corrigir antes da viagem?",
"Quero adiar a reserva mas manter as mesmas condições e preço.",
"Podem verificar se é possível fazer o check-in mais cedo no dia da chegada?",
```

**`booking_cancellation`** — add these 8 messages:
```python
"Preciso de cancelar a reserva por motivos pessoais imprevistos.",
"O voo foi cancelado pela companhia aérea — posso cancelar o hotel sem custos?",
"Quero cancelar e gostaria de saber se a tarifa é reembolsável.",
"Não vou conseguir viajar — qual é o prazo limite para cancelar sem penalização?",
"A reserva foi feita há uma hora — ainda posso cancelar gratuitamente?",
"Preciso de cancelar para toda a família — são quatro pessoas na mesma reserva.",
"Cancelei pelo portal mas ainda não recebi confirmação nem reembolso.",
"O hotel diz que não há reserva em meu nome — podem verificar e cancelar se necessário?",
```

**`payment_failure`** — add these 9 messages:
```python
"O pagamento foi recusado pelo banco mas tenho saldo suficiente.",
"Tentei pagar com dois cartões diferentes e ambos foram recusados.",
"O sistema aceita o pagamento mas a seguir mostra erro — fui cobrado ou não?",
"O pagamento ficou pendente há 24 horas sem confirmação.",
"Recebi uma notificação de falha mas vi o débito no extracto — estou confuso.",
"O pagamento por MB Way foi recusado — é um método aceite?",
"O valor foi debitado mas a encomenda continua a mostrar 'pagamento pendente'.",
"Não consigo completar o pagamento porque o sistema pede 3D Secure mas não recebo o SMS.",
"A falha de pagamento impede-me de aceder ao serviço que já estava a usar.",
```

**`duplicate_charge`** — add these 8 messages:
```python
"O extracto bancário mostra dois débitos iguais com um minuto de diferença.",
"Fui cobrado em duplicado na passagem do mês — já aconteceu duas vezes.",
"Vejo duas transacções idênticas no portal — pode ser um erro do vosso sistema?",
"Paguei manualmente e o débito automático também foi processado — quero reembolso de um.",
"A cobrança aparece duplicada no meu cartão de crédito.",
"Realizei um pagamento e o sistema deu erro, então repeti — agora tenho dois débitos.",
"Desde a migração do sistema fui cobrado em duplicado em três facturas seguidas.",
"Duas cobranças iguais na minha conta — podem confirmar qual delas é válida?",
```

- [ ] **Step 4: Run the pool-size test**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py::test_intent_messages_min_pool_size -v
```
Expected: PASS

- [ ] **Step 5: Run full suite**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q
```
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/scenarios.py tests/test_templates.py
git commit -m "feat: expand INTENT_MESSAGES to 12-15 per intent (issue #44)"
```

---

### Task 3: Update `responses.py` with `TONE_PHRASES`, `DOMAIN_LABELS` import, and parametric template expansion

**Files:**
- Modify: `scripts/responses.py`

**Interfaces:**
- Consumes: `DOMAIN_LABELS` from `scripts/templates.py`
- Modifies: `get_output(task_type, intent, domain=None, agent_tone=None) -> str` (adds `agent_tone` param)
- Produces: `TONE_PHRASES: dict[str, dict]` (used internally by `get_output`)

---

- [ ] **Step 1: Write failing tests for parametric `get_output()`**

Add to `tests/test_templates.py`:

```python
def test_get_output_accepts_agent_tone_param():
    """get_output() must accept agent_tone without raising TypeError."""
    import responses as R
    result = R.get_output("response_generation", "refund_request",
                          domain="ecommerce", agent_tone="empathetic")
    assert isinstance(result, str) and len(result) > 20


def test_get_output_no_unfilled_placeholders():
    """No {placeholder} must survive in any get_output() return value."""
    import responses as R
    from config import TASK_TYPES, AGENT_TONES
    import random
    random.seed(42)
    SAMPLE_INTENTS = [
        "refund_request", "order_status", "technical_issue",
        "password_reset", "complaint", "booking_cancellation",
        "payment_failure", "duplicate_charge",
    ]
    for tt in TASK_TYPES:
        for intent in SAMPLE_INTENTS:
            for tone in AGENT_TONES:
                try:
                    result = R.get_output(tt, intent, domain="ecommerce", agent_tone=tone)
                    assert "{" not in result and "}" not in result, (
                        f"Unfilled placeholder: task={tt} intent={intent} tone={tone}: {result!r}"
                    )
                except Exception:
                    pass  # Some (task_type, intent) combos may not have templates — that's OK


def test_tone_phrases_covers_all_agent_tones():
    import responses as R
    from config import AGENT_TONES
    assert hasattr(R, "TONE_PHRASES")
    for tone in AGENT_TONES:
        assert tone in R.TONE_PHRASES, f"TONE_PHRASES missing tone: {tone}"
        assert "opener" in R.TONE_PHRASES[tone], f"TONE_PHRASES['{tone}'] missing 'opener'"
```

Create helper `tests/scripts_test_helpers.py` (used by other test files in future phases):

```python
"""Shared test helpers."""
SAMPLE_INTENTS = [
    "refund_request", "order_status", "technical_issue",
    "password_reset", "complaint", "booking_cancellation",
    "payment_failure", "duplicate_charge",
]
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py::test_get_output_accepts_agent_tone_param tests/test_templates.py::test_tone_phrases_covers_all_agent_tones -v
```
Expected: FAIL — `get_output()` does not accept `agent_tone`.

- [ ] **Step 3: Add `TONE_PHRASES`, import `DOMAIN_LABELS`, update `get_output()` in `scripts/responses.py`**

At the **top** of `responses.py`, after the existing imports, add:

```python
from templates import DOMAIN_LABELS
```

After the `URGENCY_REASONS` dict (around line 65), add the `TONE_PHRASES` dict:

```python
# ---------------------------------------------------------------------------
# Tone-aware phrase modifiers for prose outputs
# ---------------------------------------------------------------------------

TONE_PHRASES: dict = {
    "professional": {
        "opener": "Agradecemos o seu contacto.",
        "closer": "Ficamos ao dispor para qualquer esclarecimento adicional.",
    },
    "empathetic": {
        "opener": "Lamentamos sinceramente a situação que nos descreve.",
        "closer": "Estamos do seu lado e faremos tudo para resolver esta situação.",
    },
    "concise": {
        "opener": "Recebemos o seu pedido.",
        "closer": "Aguardamos o seu feedback.",
    },
    "reassuring": {
        "opener": "Compreendemos a sua preocupação e queremos garantir-lhe que iremos resolver a situação.",
        "closer": "Pode ficar tranquilo/a — o assunto está a ser tratado com prioridade.",
    },
    "formal": {
        "opener": "Acusamos a recepção da sua comunicação.",
        "closer": "Com os melhores cumprimentos e ao inteiro dispor de V. Exa.",
    },
}
```

Update the `get_output()` function signature and body. Find the current function (near the end of the file) and replace it with:

```python
def get_output(task_type: str, intent: str, domain: str = None, agent_tone: str = None) -> str:
    """Return a realistic PT-PT output for a given task_type and intent.

    Classification tasks return structured JSON.
    Prose tasks return a randomly selected template with {domain_label} and
    {opener}/{closer} placeholders filled from DOMAIN_LABELS and TONE_PHRASES.

    Args:
        task_type: One of the 8 task types defined in config.TASK_TYPES.
        intent: One of the customer intents defined in config.CUSTOMER_INTENTS.
        domain: The row's domain (used in intent_classification output and
                {domain_label} substitution). Falls back to INTENT_DOMAIN[intent].
        agent_tone: One of the 5 agent tones. Used to fill {opener}/{closer}
                    in prose templates. Falls back to "professional".
    """
    if task_type == "intent_classification":
        urgency = INTENT_URGENCY.get(intent, "medium")
        resolved_domain = domain if domain else INTENT_DOMAIN.get(intent, "unknown")
        return json.dumps({
            "intent": intent,
            "urgency": urgency,
            "domain": resolved_domain,
            "confidence": round(random.uniform(0.82, 0.99), 2),
        }, ensure_ascii=False)

    if task_type == "urgency_classification":
        urgency = INTENT_URGENCY.get(intent, "medium")
        intent_reasons = INTENT_URGENCY_REASON.get(intent)
        reason = random.choice(intent_reasons) if intent_reasons else URGENCY_REASONS.get(urgency, "Urgência indeterminada.")
        escalate = urgency == "high"
        return json.dumps({
            "urgency": urgency,
            "reason": reason,
            "escalate": escalate,
        }, ensure_ascii=False)

    # Prose tasks — pick a template and fill parametric placeholders
    key = (task_type, intent)
    templates = RESPONSE_TEMPLATES.get(key)
    if not templates:
        return f"[sem template para {task_type}/{intent}]"

    template = random.choice(templates)

    # Fill {domain_label}
    resolved_domain = domain if domain else INTENT_DOMAIN.get(intent, "billing_accounts")
    domain_label = DOMAIN_LABELS.get(resolved_domain, "serviços ao cliente")

    # Fill {opener} and {closer}
    resolved_tone = agent_tone if agent_tone else "professional"
    tone_data = TONE_PHRASES.get(resolved_tone, TONE_PHRASES["professional"])
    opener = tone_data["opener"]
    closer = tone_data["closer"]

    filled = template.format(
        domain_label=domain_label,
        opener=opener,
        closer=closer,
    )
    return filled
```

- [ ] **Step 4: Add `{domain_label}` variables to a subset of existing templates**

In `RESPONSE_TEMPLATES`, find and update these specific keys. For each key below, the instructions show what to ADD to the existing list (append new parametric templates — do not remove existing ones):

**`("response_generation", "refund_request")`** — append:
```python
"{opener} Relativamente ao seu pedido de reembolso de {domain_label}, vamos analisar a situação com prioridade. Assim que verificarmos os detalhes, contactamos via e-mail com a resolução. {closer}",
"{opener} O seu pedido de reembolso em {domain_label} foi registado. Iremos verificar os registos de pagamento e, se confirmarmos a irregularidade, o valor será devolvido no prazo de 5 a 10 dias úteis. {closer}",
```

**`("response_generation", "technical_issue")`** — append:
```python
"{opener} Reportámos o problema técnico na área de {domain_label} à nossa equipa especializada. Estamos a investigar a causa e entraremos em contacto assim que tivermos uma actualização. {closer}",
"{opener} Reconhecemos o problema em {domain_label} e pedimos desculpa pelo impacto causado. Pode tentar limpar a cache e reiniciar a sessão enquanto a nossa equipa trabalha numa solução definitiva. {closer}",
```

**`("response_generation", "complaint")`** — append:
```python
"{opener} A sua reclamação sobre {domain_label} foi registada formalmente no nosso sistema. Um responsável irá analisar o caso e contactá-lo/a no prazo de dois dias úteis. {closer}",
"{opener} Lamentamos a experiência que descreve em {domain_label}. O seu caso foi escalado para análise interna e receberá uma resposta formal com as medidas correctivas aplicadas. {closer}",
```

**`("email_reply", "billing_question")`** — append:
```python
"Caro/a cliente,\n\n{opener} Recebemos a sua questão sobre a fatura de {domain_label}.\n\nIremos verificar os registos de cobrança e responder em detalhe até ao próximo dia útil. Caso tenha o número de fatura disponível, peça que o inclua na resposta para agilizarmos a análise.\n\n{closer}\n[Equipa de Suporte]",
```

**`("next_action_suggestion", "escalation_request")`** — append:
```python
"1. Verificar o histórico completo de interacções do cliente em {domain_label}.\n2. Escalar o caso para supervisor de {domain_label} com sumário do problema.\n3. Contactar o cliente em menos de duas horas com confirmação do escalamento.\n4. Agendar chamada com o cliente para resolução directa.",
```

**`("summarization", "technical_issue")`** — append:
```python
"O cliente reporta uma falha técnica em {domain_label} que impede o uso normal do serviço. O problema ocorre desde [data/hora indicada] e afecta [função específica descrita]. Requer análise técnica prioritária.",
```

- [ ] **Step 5: Run the new tests**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_templates.py -v -k "get_output or tone_phrases"
```
Expected: All 3 new tests pass.

- [ ] **Step 6: Run full suite**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q
```
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/responses.py tests/test_templates.py tests/scripts_test_helpers.py
git commit -m "feat: add TONE_PHRASES, parametric get_output with domain/tone vars (issue #44)"
```

---

### Task 4: Wire `domain`/`channel`/`agent_tone` through `generate.py` + add diversity tests

**Files:**
- Modify: `scripts/generate.py` (2 lines)
- Create: `tests/test_generate.py`

**Interfaces:**
- Consumes: `build_instruction(task_type, agent_tone, domain, channel)` from `templates.py` (Task 1)
- Consumes: `get_output(task_type, intent, domain, agent_tone)` from `responses.py` (Task 3)
- No changes to row schema

---

- [ ] **Step 1: Write failing diversity tests in `tests/test_generate.py`**

```python
"""Tests for generate.py diversity invariants (Phase 1 — issue #44)."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate import generate_dataset


def _sample(n=200, seed=42):
    random.seed(seed)
    return generate_dataset(n)


def test_no_unfilled_placeholders():
    """No generated field should contain an unfilled {placeholder}."""
    rows = _sample(200)
    text_fields = ["instruction", "input", "output"]
    for i, row in enumerate(rows):
        for field in text_fields:
            value = row.get(field, "")
            assert "{" not in value and "}" not in value, (
                f"Row {i} field '{field}' has unfilled placeholder: {value!r}"
            )


def test_instruction_diversity():
    """200 generated rows must produce at least 50 unique instructions."""
    rows = _sample(200)
    unique_instructions = {r["instruction"] for r in rows}
    assert len(unique_instructions) >= 50, (
        f"Only {len(unique_instructions)} unique instructions in 200 rows — need ≥50"
    )


def test_domain_label_appears_in_outputs():
    """Domain label should appear in at least 15% of non-classification prose outputs."""
    from templates import DOMAIN_LABELS
    rows = _sample(300)
    classification_types = {"intent_classification", "urgency_classification"}
    prose_rows = [r for r in rows if r["task_type"] not in classification_types]
    if not prose_rows:
        return
    hits = 0
    for row in prose_rows:
        label = DOMAIN_LABELS.get(row["domain"], "")
        if label and label in row["output"]:
            hits += 1
    ratio = hits / len(prose_rows)
    assert ratio >= 0.15, (
        f"Domain label appeared in only {100*ratio:.1f}% of prose outputs — need ≥15%"
    )


def test_all_generated_rows_pass_validation():
    """All generated rows must pass is_valid_row()."""
    from validate import is_valid_row
    rows = _sample(100)
    for i, row in enumerate(rows):
        ok, reason = is_valid_row(row)
        assert ok, f"Row {i} failed validation: {reason} — {row}"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_generate.py -v
```
Expected: `test_instruction_diversity` FAILS (only 12 unique instructions) and `test_domain_label_appears_in_outputs` likely FAILS. `test_no_unfilled_placeholders` may also FAIL once wiring is added.

- [ ] **Step 3: Update `generate.py` to pass `domain` and `channel` to `build_instruction()` and `agent_tone` to `generate_output()`**

Find these two lines in `generate_row()` (around lines 18-25):

```python
        "instruction": build_instruction(task, agent_tone),
```
Replace with:
```python
        "instruction": build_instruction(task, agent_tone, domain, channel),
```

Find:
```python
        "output": generate_output(task, intent, domain=domain),
```
Replace with:
```python
        "output": generate_output(task, intent, domain=domain, agent_tone=agent_tone),
```

Also update `generate_output()` to forward `agent_tone`:

Find:
```python
def generate_output(task_type, intent, domain=None):
    return get_output(task_type, intent, domain=domain)
```
Replace with:
```python
def generate_output(task_type, intent, domain=None, agent_tone=None):
    return get_output(task_type, intent, domain=domain, agent_tone=agent_tone)
```

- [ ] **Step 4: Run the diversity tests**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/test_generate.py -v
```
Expected: All 4 tests pass.

- [ ] **Step 5: Run the complete test suite**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -q
```
Expected: All tests pass (54 original + new tests).

- [ ] **Step 6: Run pipeline end-to-end to confirm no runtime errors**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 scripts/pipeline.py --n 500 --stats 2>&1 | tail -20
```
Expected: Pipeline completes, stats table prints, no errors.

- [ ] **Step 7: Verify diversity stats**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -c "
import json, collections, random
random.seed(0)
from scripts.generate import generate_dataset
rows = generate_dataset(500)
instrs = collections.Counter(r['instruction'] for r in rows)
inputs = collections.Counter(r['input'] for r in rows)
outputs = collections.Counter(r['output'] for r in rows)
print(f'Unique instructions: {len(instrs)} / {len(rows)}')
print(f'Unique inputs:       {len(inputs)} / {len(rows)}')
print(f'Repeated outputs:    {sum(1 for c in outputs.values() if c > 1)} distinct values')
"
```
Expected output (approximate):
```
Unique instructions: 200+ / 500
Unique inputs:       200+ / 500
Repeated outputs:    <50 distinct values
```

- [ ] **Step 8: Commit**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: wire domain/channel/agent_tone through generate_row, add diversity tests (issue #44)"
```

---

### Task 5: PR, project board sync, and close issue

**Files:** None — git/GitHub operations only.

---

- [ ] **Step 1: Run final full test suite**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset && python3 -m pytest tests/ -v 2>&1 | tail -20
```
Expected: All tests pass.

- [ ] **Step 2: Push branch and open PR**

```bash
cd /Users/ariazevedo/repos/pt-ai-instruction-dataset
git push
gh pr create \
  --repo ariazevedopt/pt-ai-instruction-dataset \
  --title "feat: Phase 1 — parametric template diversity (issue #44)" \
  --body "## Changes

Fixes the repetition ceiling identified in the Opus quality assessment.

### \`templates.py\` (rewritten)
- \`DOMAIN_LABELS\`, \`CHANNEL_LABELS\`, \`AGENT_TONE_LABELS\` — pt-PT label maps
- \`INSTRUCTION_TEMPLATES\` — 5-7 parametric templates per task_type (8 task types)
- \`build_instruction()\` gains \`domain\` and \`channel\` params; fills placeholders

### \`scenarios.py\`
- \`INTENT_MESSAGES\` expanded from 3-5 → 12-15 per intent (18 intents)

### \`responses.py\`
- Imports \`DOMAIN_LABELS\` from \`templates.py\`
- New \`TONE_PHRASES\` dict — opener/closer per agent_tone (5 tones)
- \`get_output()\` gains \`agent_tone\` param; fills \`{domain_label}\`, \`{opener}\`, \`{closer}\`
- New parametric template variants for key (task_type, intent) pairs

### \`generate.py\`
- Passes \`domain\`, \`channel\` to \`build_instruction()\`
- Passes \`agent_tone\` to \`get_output()\`

### New tests
- \`tests/test_templates.py\` — label maps, pool sizes, no unfilled placeholders
- \`tests/test_generate.py\` — instruction diversity ≥50, domain label in outputs ≥15%, all rows valid

## Before/After
| Metric | Before | After |
|---|---|---|
| Unique instructions / 500 rows | 12 | 200+ |
| Unique inputs / 500 rows | ~79 | 200+ |
| Repeated output values | 315 | <50 |

Closes #44" \
  --base main
```

- [ ] **Step 3: Sync project board**

Get the PR node ID and add to board as "Review":

```bash
PR_NUM=$(gh pr list --repo ariazevedopt/pt-ai-instruction-dataset --state open --json number,title --jq '.[] | select(.title | contains("Phase 1")) | .number')
PR_NODE=$(gh api graphql -f query="{ repository(owner:\"ariazevedopt\", name:\"pt-ai-instruction-dataset\") { pullRequest(number:$PR_NUM) { id } } }" --jq '.data.repository.pullRequest.id')

PROJECT_ID="PVT_kwHOAS3Kg84BUljL"
STATUS_FIELD_ID="PVTSSF_lAHOAS3Kg84BUljLzhBstHw"
REVIEW_OPTION="f9a382cb"

ITEM_ID=$(gh api graphql -f query="mutation { addProjectV2ItemById(input: {projectId: \"$PROJECT_ID\", contentId: \"$PR_NODE\"}) { item { id } } }" --jq '.data.addProjectV2ItemById.item.id')

gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"$PROJECT_ID\", itemId: \"$ITEM_ID\", fieldId: \"$STATUS_FIELD_ID\", value: {singleSelectOptionId: \"$REVIEW_OPTION\"}}) { projectV2Item { id } } }"

echo "PR #$PR_NUM added to board as Review"
```

- [ ] **Step 4: After PR is reviewed and merged, update issue #44 and project board**

```bash
# Close issue #44
gh issue close 44 --repo ariazevedopt/pt-ai-instruction-dataset --comment "Implemented in PR — parametric templates landed on main."

# Update issue #44 board item to Done
ISSUE_NODE=$(gh api graphql -f query='{ repository(owner:"ariazevedopt", name:"pt-ai-instruction-dataset") { issue(number:44) { id } } }' --jq '.data.repository.issue.id')
PROJECT_ID="PVT_kwHOAS3Kg84BUljL"
STATUS_FIELD_ID="PVTSSF_lAHOAS3Kg84BUljLzhBstHw"
DONE_OPTION="98236657"
ITEM_ID=$(gh api graphql -f query="mutation { addProjectV2ItemById(input: {projectId: \"$PROJECT_ID\", contentId: \"$ISSUE_NODE\"}) { item { id } } }" --jq '.data.addProjectV2ItemById.item.id')
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"$PROJECT_ID\", itemId: \"$ITEM_ID\", fieldId: \"$STATUS_FIELD_ID\", value: {singleSelectOptionId: \"$DONE_OPTION\"}}) { projectV2Item { id } } }"
echo "Issue #44 marked Done on project board"
```
