
# Maps each intent to the domains where it makes semantic sense.
# generate_row() uses this to avoid nonsensical intent+domain combinations.
INTENT_DOMAINS = {
    "refund_request":      ["ecommerce", "marketplace", "billing_accounts", "subscriptions", "telecom", "utilities", "saas", "travel"],
    "return_request":      ["ecommerce", "marketplace"],
    "order_status":        ["ecommerce", "marketplace", "subscriptions"],
    "delivery_delay":      ["ecommerce", "marketplace", "subscriptions"],
    "damaged_item":        ["ecommerce", "marketplace"],
    "billing_question":    ["billing_accounts", "telecom", "utilities", "subscriptions", "saas", "ecommerce", "travel"],
    "invoice_request":     ["billing_accounts", "telecom", "utilities", "subscriptions", "saas", "ecommerce", "travel"],
    "cancel_subscription": ["subscriptions", "saas", "telecom", "utilities"],
    "change_plan":         ["subscriptions", "saas", "telecom", "utilities"],
    "technical_issue":     ["saas", "telecom", "utilities", "subscriptions", "ecommerce"],
    "password_reset":      ["saas", "telecom", "subscriptions", "ecommerce", "marketplace", "billing_accounts"],
    "account_access":      ["saas", "telecom", "subscriptions", "ecommerce", "marketplace", "billing_accounts"],
    "complaint":           ["ecommerce", "marketplace", "saas", "telecom", "utilities", "subscriptions", "travel", "billing_accounts"],
    "escalation_request":  ["ecommerce", "marketplace", "saas", "telecom", "utilities", "subscriptions", "travel", "billing_accounts"],
    "booking_change":      ["travel"],
    "booking_cancellation":["travel"],
    "payment_failure":     ["ecommerce", "marketplace", "billing_accounts", "subscriptions", "telecom", "utilities", "saas", "travel"],
    "duplicate_charge":    ["billing_accounts", "ecommerce", "telecom", "utilities", "subscriptions", "travel"],
}

INTENT_MESSAGES = {
    "refund_request": [
        "Quero devolver o produto e receber o reembolso.",
        "O artigo chegou com defeito e quero ser reembolsado.",
        "Efectuei um pagamento em duplicado e pretendo o reembolso do valor cobrado a mais.",
        "O serviço que contratei não foi prestado e exijo o reembolso.",
        "Fui cobrado por um serviço que já cancelei — quero o valor de volta.",
    ],
    "return_request": [
        "Gostaria de devolver o artigo que encomendei.",
        "O produto não corresponde à descrição e quero devolvê-lo.",
        "Pretendo iniciar o processo de devolução da minha encomenda.",
        "O artigo veio errado e preciso de o devolver.",
    ],
    "order_status": [
        "Queria saber qual é o estado da minha encomenda.",
        "Quando é que a minha encomenda vai ser entregue?",
        "Não recebi nenhuma actualização sobre o meu pedido desde que o realizei.",
        "Podem confirmar se o meu pedido foi processado?",
    ],
    "delivery_delay": [
        "A encomenda ainda não chegou.",
        "O prazo de entrega já passou e continuo sem receber o artigo.",
        "A minha encomenda está em atraso — qual é a causa?",
        "O equipamento que encomendei devia ter chegado esta semana e não apareceu.",
        "Ainda não recebi o material que foi enviado há mais de duas semanas.",
    ],
    "damaged_item": [
        "O artigo que recebi chegou danificado.",
        "A embalagem estava completamente destruída e o produto está inutilizável.",
        "Recebi um produto partido. O que devo fazer?",
        "O produto chegou com defeito visível — quero uma solução.",
    ],
    "billing_question": [
        "Tenho uma dúvida relativamente ao valor cobrado na minha fatura.",
        "O montante debitado não corresponde ao que foi acordado.",
        "Gostaria de perceber a que se referem alguns itens da minha fatura.",
    ],
    "invoice_request": [
        "Preciso de uma fatura com os dados da minha empresa.",
        "Ainda não recebi a fatura referente ao meu pagamento do mês passado.",
        "Podem enviar-me a fatura para o meu e-mail, por favor?",
    ],
    "cancel_subscription": [
        "Pretendo cancelar a minha subscrição.",
        "Quero encerrar a minha conta e deixar de ser cobrado.",
        "Desejo cancelar o plano com efeitos no final do período de faturação.",
    ],
    "change_plan": [
        "Gostaria de mudar para um plano superior.",
        "Pretendo fazer o downgrade do meu plano actual.",
        "Quero alterar a minha subscrição para o plano anual.",
    ],
    "technical_issue": [
        "A aplicação não está a funcionar correctamente.",
        "Estou a ter problemas ao aceder à plataforma desde ontem.",
        "O serviço apresenta erros e não consigo completar as minhas tarefas.",
    ],
    "password_reset": [
        "Não consigo repor a palavra-passe.",
        "O e-mail de recuperação não chega à minha caixa de entrada.",
        "Esqueci-me da palavra-passe e preciso de aceder à conta com urgência.",
    ],
    "account_access": [
        "Não consigo iniciar sessão na minha conta.",
        "A minha conta foi bloqueada e não sei porquê.",
        "Estou a tentar aceder ao portal mas continuo a receber erro de autenticação.",
    ],
    "complaint": [
        "Estou muito insatisfeito com o serviço prestado.",
        "A qualidade do apoio que recebi foi inaceitável.",
        "Quero registar uma reclamação formal relativamente à minha experiência.",
    ],
    "escalation_request": [
        "Preciso de falar com um responsável ou supervisor.",
        "Este problema já dura há demasiado tempo sem resolução — quero escalar.",
        "Não estou satisfeito com as respostas que tenho recebido e exijo uma solução.",
    ],
    "booking_change": [
        "Preciso de alterar a data da minha reserva.",
        "Gostaria de mudar o destino ou o horário da minha viagem.",
        "Quero adicionar um passageiro à minha reserva.",
    ],
    "booking_cancellation": [
        "Pretendo cancelar a minha reserva.",
        "Devido a um imprevisto, necessito de cancelar a viagem marcada.",
        "Quero cancelar a minha reserva e saber se tenho direito a reembolso.",
    ],
    "payment_failure": [
        "O meu pagamento foi recusado mas não percebo porquê.",
        "Tentei efectuar o pagamento várias vezes e continua a falhar.",
        "Recebi uma notificação de falha no pagamento — como posso resolver?",
    ],
    "duplicate_charge": [
        "Foi cobrado o mesmo valor duas vezes.",
        "Tenho uma cobrança repetida na fatura deste mês.",
        "Verifiquei que fui debitado em duplicado e quero que o valor seja devolvido.",
    ],
}

