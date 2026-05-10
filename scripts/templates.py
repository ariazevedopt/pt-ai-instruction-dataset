def build_instruction(task_type, agent_tone):
    if task_type == "response_generation":
        return f"Responde ao cliente em português de Portugal, com tom {agent_tone}."
    if task_type == "email_reply":
        return "Escreve uma resposta por e-mail em português de Portugal."
    if task_type == "summarization":
        return "Resume o problema do cliente de forma concisa."
    if task_type == "intent_classification":
        return "Classifica a intenção do cliente."
    if task_type == "urgency_classification":
        return "Classifica a urgência do pedido."
    if task_type == "rewrite_professional":
        return "Reescreve a mensagem de forma profissional."
    if task_type == "next_action_suggestion":
        return "Indica os próximos passos."
    if task_type == "faq_answer":
        return "Responde à pergunta do cliente."
