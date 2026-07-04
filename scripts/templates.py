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
