"""Response template library for LusoSupport-PT.

All text is written in European Portuguese (pt-PT).
Templates are sampled randomly at generation time to add variety.

Structure:
  INTENT_URGENCY   — urgency level per customer intent
  RESPONSE_TEMPLATES — dict mapping (task_type, intent) → list[str]
  get_output()     — returns a random output for a given (task_type, intent)
"""
import json
import random
from templates import DOMAIN_LABELS

# ---------------------------------------------------------------------------
# Metadata helpers for classification outputs
# ---------------------------------------------------------------------------

INTENT_URGENCY = {
    "refund_request":       "medium",
    "return_request":       "low",
    "order_status":         "low",
    "delivery_delay":       "medium",
    "damaged_item":         "medium",
    "billing_question":     "medium",
    "invoice_request":      "low",
    "cancel_subscription":  "low",
    "change_plan":          "low",
    "technical_issue":      "high",
    "password_reset":       "high",
    "account_access":       "high",
    "complaint":            "high",
    "escalation_request":   "high",
    "booking_change":       "medium",
    "booking_cancellation": "medium",
    "payment_failure":      "high",
    "duplicate_charge":     "high",
}

INTENT_DOMAIN = {
    "refund_request":       "ecommerce",
    "return_request":       "ecommerce",
    "order_status":         "ecommerce",
    "delivery_delay":       "ecommerce",
    "damaged_item":         "ecommerce",
    "billing_question":     "billing_accounts",
    "invoice_request":      "billing_accounts",
    "cancel_subscription":  "subscriptions",
    "change_plan":          "subscriptions",
    "technical_issue":      "saas",
    "password_reset":       "saas",
    "account_access":       "saas",
    "complaint":            "billing_accounts",
    "escalation_request":   "billing_accounts",
    "booking_change":       "travel",
    "booking_cancellation": "travel",
    "payment_failure":      "billing_accounts",
    "duplicate_charge":     "billing_accounts",
}

URGENCY_REASONS = {
    "low":    "O pedido não apresenta indicadores de urgência imediata.",
    "medium": "A situação requer atenção dentro do prazo normal de resposta.",
    "high":   "O cliente reporta um problema que afecta o acesso ou causa impacto financeiro directo.",
}

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

# Per-intent reason phrases used to build varied urgency_classification outputs.
INTENT_URGENCY_REASON = {
    "refund_request":       [
        "O cliente aguarda a devolução de um valor pago indevidamente.",
        "Existe impacto financeiro directo que requer acompanhamento dentro do prazo normal.",
        "O cliente reporta uma cobrança incorrecta e espera resolução.",
    ],
    "return_request":       [
        "O pedido de devolução não implica urgência imediata.",
        "A devolução pode ser processada dentro do prazo habitual.",
    ],
    "order_status":         [
        "O cliente aguarda informação sobre o estado da encomenda, sem urgência crítica.",
        "A consulta de estado é de baixa prioridade e pode ser respondida no prazo normal.",
    ],
    "delivery_delay":       [
        "O atraso na entrega cria transtorno mas não constitui emergência crítica.",
        "O cliente aguarda actualização sobre o envio dentro do prazo acordado.",
        "A situação requer acompanhamento para evitar escalada de insatisfação.",
    ],
    "damaged_item":         [
        "O artigo danificado requer resolução dentro do prazo normal de reclamação.",
        "O cliente reporta um produto com defeito e aguarda resposta sobre substituição.",
        "A reclamação de dano exige atenção mas não tem carácter de emergência imediata.",
    ],
    "billing_question":     [
        "A dúvida de faturação requer esclarecimento dentro do prazo de resposta habitual.",
        "O cliente questiona um item da fatura — situação de prioridade média.",
        "A questão de cobrança pode gerar insatisfação se não for respondida atempadamente.",
    ],
    "invoice_request":      [
        "O pedido de fatura é de baixa urgência e pode ser processado no prazo normal.",
        "A emissão de fatura não requer intervenção imediata.",
    ],
    "cancel_subscription":  [
        "O pedido de cancelamento não requer intervenção urgente.",
        "O cliente pretende encerrar o serviço — situação de baixa prioridade operacional.",
    ],
    "change_plan":          [
        "A alteração de plano é uma operação de rotina sem urgência.",
        "O pedido de mudança de plano pode ser tratado no prazo normal.",
    ],
    "technical_issue":      [
        "O problema técnico está a impedir o uso do serviço e exige resolução urgente.",
        "A falha reportada afecta a produtividade do cliente e requer resposta imediata.",
        "O incidente técnico tem impacto directo na operação e deve ser escalado.",
    ],
    "password_reset":       [
        "O cliente está bloqueado da conta e não consegue aceder ao serviço.",
        "A impossibilidade de acesso constitui urgência e requer resposta imediata.",
        "O bloqueio de conta impede o cliente de utilizar o serviço contratado.",
    ],
    "account_access":       [
        "O acesso bloqueado afecta directamente a utilização do serviço.",
        "O cliente não consegue aceder à conta — situação que requer resposta urgente.",
        "A falha de autenticação impede o cliente de utilizar a plataforma.",
    ],
    "complaint":            [
        "A reclamação formal indica elevada insatisfação e risco de perda do cliente.",
        "O cliente está insatisfeito e exige resposta prioritária para evitar escalada.",
        "A situação tem potencial de impacto reputacional se não for tratada com urgência.",
    ],
    "escalation_request":   [
        "O cliente exige falar com um responsável — escalada imediata necessária.",
        "A insistência do cliente em escalar indica falha no suporte de primeira linha.",
        "A situação já ultrapassou o tempo aceitável de resolução e requer atenção directa.",
    ],
    "booking_change":       [
        "A alteração de reserva tem prazo limitado e requer atenção dentro do tempo útil.",
        "O pedido de modificação pode implicar custos adicionais se não for tratado atempadamente.",
    ],
    "booking_cancellation": [
        "O cancelamento tem implicações de reembolso que requerem análise dentro do prazo.",
        "A situação tem carácter de urgência moderada devido a possíveis custos de cancelamento.",
    ],
    "payment_failure":      [
        "A falha de pagamento impede a conclusão da transacção e requer resolução urgente.",
        "O cliente não consegue efectuar o pagamento — situação de alta prioridade.",
        "O bloqueio de pagamento pode resultar em perda de serviço se não for resolvido.",
    ],
    "duplicate_charge":     [
        "A cobrança duplicada constitui impacto financeiro directo e requer resolução urgente.",
        "O cliente foi debitado indevidamente duas vezes — situação de alta prioridade.",
        "A duplicação de cobrança pode implicar reembolso urgente e verificação de registo.",
    ],
}

# ---------------------------------------------------------------------------
# Text response templates
# ---------------------------------------------------------------------------

RESPONSE_TEMPLATES = {

    # ── response_generation ────────────────────────────────────────────────

    ("response_generation", "refund_request"): [
        "Lamentamos a situação. Para avançarmos com o pedido de reembolso, pedimos que nos indique o número da encomenda e, se aplicável, uma fotografia do artigo com defeito. Assim que recebermos essa informação, processaremos o reembolso no prazo habitual.",
        "Agradecemos o seu contacto e pedimos desculpa pelo inconveniente. Para darmos início ao processo de reembolso, necessitamos do número da encomenda e da prova de compra. Após validação, o valor será devolvido ao meio de pagamento original.",
        "Compreendemos a sua situação e estamos disponíveis para ajudar. Pode indicar-nos o número da encomenda em questão? Com essa informação, verificaremos o estado do pedido e processaremos o reembolso com a maior brevidade possível.",
        "Pedimos desculpa pelo sucedido. O processo de reembolso tem início imediato após confirmação dos dados. Pode partilhar connosco o número de referência da compra e o IBAN para devolução, caso o pagamento tenha sido por transferência?",
        "Lamentamos que a situação não tenha sido resolvida anteriormente. Para tratarmos do reembolso de forma prioritária, pode confirmar o método de pagamento utilizado? Reembolsos para cartão são processados em 3 a 5 dias úteis.",
        "{opener} Relativamente ao seu pedido de reembolso de {domain_label}, vamos analisar a situação com prioridade. Assim que verificarmos os detalhes, contactamos via e-mail com a resolução. {closer}",
        "{opener} O seu pedido de reembolso em {domain_label} foi registado. Iremos verificar os registos de pagamento e, se confirmarmos a irregularidade, o valor será devolvido no prazo de 5 a 10 dias úteis. {closer}",
    ],

    ("response_generation", "return_request"): [
        "Agradecemos o seu contacto. Para iniciar o processo de devolução, por favor indique o número da encomenda e o motivo da devolução. Após confirmação, enviaremos as instruções necessárias para proceder à devolução.",
        "Ficamos ao dispor para tratar da devolução. Necessitamos do número da encomenda e de uma breve descrição do motivo. Depois de validarmos o pedido, forneceremos a etiqueta de devolução e os passos a seguir.",
        "Lamentamos que o artigo não tenha correspondido às suas expectativas. Para processar a devolução, pedimos que nos envie o número da encomenda. O prazo de devolução é de 30 dias a contar da data de entrega.",
    ],

    ("response_generation", "order_status"): [
        "Agradecemos o seu contacto. Para verificar o estado da sua encomenda, precisamos do número de encomenda ou do endereço de e-mail utilizado na compra. Assim que tivermos essa informação, fornecemos uma actualização imediata.",
        "Pode indicar-nos o número da sua encomenda? Com esse dado, conseguimos verificar o estado actual e informá-lo/a sobre a data prevista de entrega.",
        "Estamos a verificar a informação relativa à sua encomenda. Para agilizar o processo, por favor confirme o número de encomenda ou a referência da compra.",
    ],

    ("response_generation", "delivery_delay"): [
        "Pedimos desculpa pelo atraso na entrega. Estamos a investigar a situação junto do parceiro logístico. Assim que tivermos uma actualização, entraremos em contacto consigo. Agradecemos a sua compreensão.",
        "Lamentamos o atraso verificado na sua encomenda. O prazo previsto foi ultrapassado e pedimos desculpa pelo inconveniente. Pode partilhar connosco o número de encomenda para verificarmos o estado actual com urgência?",
        "Compreendemos a sua preocupação relativamente ao atraso. Estamos a acompanhar a situação com o transportador e enviaremos uma actualização logo que possível. Obrigado pela sua paciência.",
    ],

    ("response_generation", "damaged_item"): [
        "Lamentamos que o artigo tenha chegado danificado. Para darmos seguimento à situação, pedimos que nos envie fotografias do dano e o número da encomenda. Com essa informação, processaremos a substituição ou reembolso com a maior brevidade.",
        "Pedimos desculpa pela situação. Receber um artigo danificado é inaceitável e queremos resolver o problema rapidamente. Por favor envie-nos uma fotografia do dano e o número da encomenda.",
        "Compreendemos a sua frustração. Para registar a ocorrência e avançar com a resolução, necessitamos do número da encomenda e de fotografias que documentem o estado em que o artigo chegou.",
        "Lamentamos profundamente o sucedido. Ao recebermos as fotografias do artigo danificado, iremos determinar se o mais indicado é envio de substituição imediata ou reembolso integral. Qual prefere?",
        "O dano ocorrido durante o transporte é da nossa responsabilidade. Para abrirmos o processo de reclamação junto da transportadora e garantirmos a sua compensação, precisamos do número de encomenda e de fotografias do artigo e da embalagem.",
    ],

    ("response_generation", "billing_question"): [
        "Agradecemos o seu contacto relativamente à fatura. Para esclarecermos a sua dúvida, pode indicar-nos o número da fatura ou o período a que se refere? Verificaremos os detalhes e responderemos com a explicação completa.",
        "Ficamos ao dispor para esclarecer qualquer dúvida sobre a sua fatura. Para analisarmos a situação, precisamos do número de cliente ou do período de faturação em questão.",
        "Compreendemos a sua questão relativamente ao valor faturado. Para verificar os detalhes da cobrança, pode partilhar connosco o número da fatura? Assim poderemos confirmar se existe algum erro ou fornecer a explicação detalhada.",
    ],

    ("response_generation", "invoice_request"): [
        "Claro, podemos emitir a fatura com os dados que nos indicar. Por favor forneça o nome completo ou designação social, NIF e morada de facturação. Enviaremos a fatura por e-mail no prazo de 24 horas úteis.",
        "Agradecemos o pedido de fatura. Para proceder à emissão, necessitamos do NIF e da morada fiscal associada. Assim que recebermos essa informação, a fatura será emitida e enviada para o seu e-mail.",
        "Ficamos ao dispor para emitir a fatura solicitada. Pode indicar-nos os dados de facturação (nome/empresa, NIF e morada)? Após confirmação, enviaremos o documento para o endereço de e-mail registado.",
    ],

    ("response_generation", "cancel_subscription"): [
        "Lamentamos que queira cancelar a sua subscrição. Para processarmos o cancelamento, podemos fazê-lo com efeitos imediatos ou no final do período em curso, conforme a sua preferência. Por favor confirme a opção desejada.",
        "Agradecemos o seu contacto. O cancelamento da subscrição pode ser processado de imediato. Confirma que pretende avançar? Note que continuará a ter acesso até ao final do período já pago.",
        "Compreendemos a sua decisão. Para concluir o cancelamento, precisamos apenas de confirmar a sua identidade. Pode indicar-nos o endereço de e-mail associado à conta?",
        "O cancelamento foi registado. Antes de confirmarmos, gostaríamos de perceber o motivo para verificar se existe algo que possamos melhorar. Se ainda assim pretender cancelar, o serviço terminará no final do ciclo actual.",
        "Lamentamos a sua decisão de cancelar. Para garantir que o processo corre sem problemas, confirme o e-mail da conta e se pretende cancelamento imediato ou no final do período de faturação. Não serão cobradas taxas de cancelamento.",
    ],

    ("response_generation", "change_plan"): [
        "Claro, podemos ajudá-lo/a a alterar o plano. Temos disponíveis as opções [Plano A], [Plano B] e [Plano C]. Qual prefere? A alteração é efectuada de imediato e o novo valor será cobrado no próximo ciclo de faturação.",
        "Agradecemos o contacto. A alteração de plano pode ser feita sem qualquer interrupção do serviço. Para avançar, pode indicar-nos qual o plano para o qual pretende mudar?",
        "Ficamos disponíveis para ajudar na mudança de plano. A alteração entra em vigor imediatamente. Quer que lhe expliquemos as diferenças entre os planos disponíveis antes de decidir?",
        "Posso ajudá-lo/a a explorar as opções de plano disponíveis. Qual é a sua principal prioridade — reduzir o custo mensal, aumentar o armazenamento, ou adicionar utilizadores?",
        "Antes de efectuarmos qualquer alteração, gostaria de apresentar as opções actuais para que possa escolher o plano mais adequado. Qual é a sua necessidade principal?",
    ],

    ("response_generation", "technical_issue"): [
        "Lamentamos o inconveniente técnico que está a experienciar. Para ajudarmos a resolver o problema, pode descrever com mais detalhe o que está a acontecer? Qual a mensagem de erro que aparece, se existir?",
        "Agradecemos o contacto. Estamos a registar a ocorrência técnica. Para agilizar a resolução, pode indicar-nos: (1) qual o browser ou dispositivo que está a utilizar, e (2) quando começou o problema?",
        "Pedimos desculpa pelo inconveniente. Para diagnosticarmos o problema com maior precisão, pode tentar limpar a cache do browser e tentar novamente? Se o problema persistir, por favor descreva os passos que efectuou quando o erro ocorreu.",
        "Estamos a investigar a falha técnica reportada. Para confirmar se é um problema generalizado ou específico da sua conta, pode indicar-nos o número de conta ou endereço de e-mail? Actualizaremos assim que tivermos mais informação.",
        "Reconhecemos o problema técnico descrito e pedimos desculpa pelo impacto causado. A equipa técnica já foi notificada. Pode partilhar connosco capturas de ecrã do erro? Isso ajudará a agilizar o diagnóstico.",
        "{opener} Reportámos o problema técnico na área de {domain_label} à nossa equipa especializada. Estamos a investigar a causa e entraremos em contacto assim que tivermos uma actualização. {closer}",
        "{opener} Reconhecemos o problema em {domain_label} e pedimos desculpa pelo impacto causado. Pode tentar limpar a cache e reiniciar a sessão enquanto a nossa equipa trabalha numa solução definitiva. {closer}",
    ],

    ("response_generation", "password_reset"): [
        "Para repor a sua palavra-passe, aceda à página de início de sessão e clique em 'Esqueceu a palavra-passe?'. Será enviado um e-mail de recuperação para o endereço associado à conta. Verifique também a pasta de spam.",
        "Agradecemos o contacto. Para redefinir a palavra-passe, enviámos um e-mail de recuperação para o endereço registado. Caso não o receba nos próximos 5 minutos, verifique a pasta de spam ou contacte-nos novamente.",
        "A reposição da palavra-passe é feita através do link que enviámos para o seu e-mail. Se não recebeu o e-mail, pode indicar-nos o endereço registado na conta para verificarmos a situação?",
        "Pode redefinir a palavra-passe directamente através do portal em 'Acesso à Conta' → 'Esqueci a palavra-passe'. Se o endereço de e-mail registado já não está activo, contacte-nos para verificação de identidade alternativa.",
        "Para sua segurança, o link de reposição de palavra-passe expira ao fim de 30 minutos. Se já expirou, pode solicitar um novo na página de login. Caso continue sem acesso, podemos verificar a conta e fazer o reset manualmente.",
        "Para auxiliar com a recuperação da palavra-passe, pode confirmar o endereço de e-mail associado à conta? Por vezes, o e-mail de recuperação pode chegar à pasta de spam ou lixo.",
        "Verificou a pasta de spam ou de lixo do seu e-mail? O e-mail de recuperação pode ter sido filtrado. Se confirmar o endereço registado, podemos reenviar de imediato.",
    ],

    ("response_generation", "account_access"): [
        "Pedimos desculpa pelo problema no acesso. Para verificarmos a situação da sua conta, pode confirmar o endereço de e-mail associado? Verificaremos se a conta está activa e, se necessário, procederemos ao desbloqueio.",
        "Lamentamos o inconveniente. O problema de acesso pode estar relacionado com uma autenticação falhada ou com a conta temporariamente bloqueada por motivos de segurança. Pode indicar-nos o e-mail de registo?",
        "Para resolvermos o problema de acesso com a maior brevidade, precisamos de verificar a sua identidade. Pode confirmar o endereço de e-mail e o número de telemóvel associados à conta?",
        "Compreendemos o transtorno causado pelo bloqueio de acesso. Após confirmação da sua identidade, procederemos ao desbloqueio imediato da conta. Pode fornecer o e-mail de registo e os últimos 4 dígitos do número de telemóvel?",
        "O acesso bloqueado pode dever-se a múltiplas tentativas falhadas ou a uma actualização de segurança. Vamos verificar a situação. Por favor confirme o endereço de e-mail e aguarde — o desbloqueio é efectuado em minutos.",
        "Para melhor compreender a situação, pode descrever o que acontece quando tenta aceder à sua conta? Recebe alguma mensagem de erro específica?",
        "Antes de prosseguirmos, precisamos de perceber em que passo está a encontrar dificuldade. Está a tentar aceder pelo site, aplicação, ou outro canal?",
    ],

    ("response_generation", "complaint"): [
        "Lamentamos profundamente a experiência negativa que vivenciou. A sua reclamação foi registada com prioridade e será analisada pela equipa responsável. Entraremos em contacto consigo nas próximas 24 horas com uma resposta.",
        "Agradecemos o seu feedback, ainda que lamentemos que a experiência não tenha sido satisfatória. Vamos analisar a situação com detalhe e tomar as medidas necessárias. Pode contar com uma resposta formal no prazo de 2 dias úteis.",
        "Compreendemos a sua insatisfação e pedimos desculpa pelo sucedido. A sua reclamação é importante para nós e será tratada com a devida seriedade. Um responsável da equipa entrará em contacto consigo brevemente.",
        "A sua reclamação foi registada no nosso sistema com referência [número]. Partilhamos a sua insatisfação e iremos investigar o sucedido internamente. Receberá uma resposta fundamentada no prazo de 3 dias úteis.",
        "Pedimos as nossas mais sinceras desculpas pela situação descrita. Reconhecemos que a experiência não foi a que esperava e que temos a responsabilidade de melhorar. A equipa de qualidade irá analisar o caso e contactá-lo/a brevemente.",
        "{opener} A sua reclamação sobre {domain_label} foi registada formalmente no nosso sistema. Um responsável irá analisar o caso e contactá-lo/a no prazo de dois dias úteis. {closer}",
        "{opener} Lamentamos a experiência que descreve em {domain_label}. O seu caso foi escalado para análise interna e receberá uma resposta formal com as medidas correctivas aplicadas. {closer}",
    ],

    ("response_generation", "escalation_request"): [
        "Compreendemos a sua frustração e pedimos desculpa pela situação. Vamos encaminhar o seu caso para um responsável sénior que entrará em contacto consigo no prazo de 4 horas úteis. Agradecemos a sua paciência.",
        "A sua situação foi escalada para a equipa de supervisão. Um gestor de conta entrará em contacto consigo hoje, no período da tarde. Lamentamos o transtorno causado.",
        "Pedimos desculpa por não termos resolvido a situação até ao momento. O seu caso foi escalado e um supervisor irá contactá-lo/a directamente. Pode esperar uma resposta no prazo máximo de 2 horas úteis.",
    ],

    ("response_generation", "booking_change"): [
        "Claro, podemos verificar a disponibilidade para a alteração da sua reserva. Por favor indique o número de reserva e as novas datas ou preferências pretendidas. Verificaremos as opções disponíveis e informaremos sobre eventuais custos adicionais.",
        "Agradecemos o contacto. Para processar a alteração da reserva, precisamos do número de reserva e dos novos dados pretendidos. Note que alterações podem estar sujeitas a taxas dependendo da tarifa contratada.",
        "Ficamos ao dispor para ajudar na alteração da sua reserva. Pode indicar-nos o número de reserva e o que pretende alterar (data, hora, número de participantes)?",
        "Com certeza. Para verificar a disponibilidade e eventuais diferenças de preço, precisamos do número de reserva e das novas datas pretendidas. Responderemos com as opções disponíveis no prazo de 2 horas úteis.",
        "Agradecemos o pedido de alteração. Para avançar, pode confirmar o número de reserva e descrever a alteração pretendida? Se a nova data implicar custos adicionais, informaremos previamente antes de qualquer cobrança.",
    ],

    ("response_generation", "booking_cancellation"): [
        "Lamentamos que necessite de cancelar a sua reserva. Para processarmos o cancelamento e verificarmos as condições de reembolso, pode indicar-nos o número de reserva? A política de reembolso varia conforme a tarifa contratada.",
        "Agradecemos o contacto. O cancelamento da reserva pode ser processado de imediato. Dependendo da tarifa e da antecedência, poderá ter direito a reembolso total ou parcial. Pode indicar-nos o número de reserva?",
        "Compreendemos que possa haver imprevistos. Para cancelar a reserva, necessitamos do número de reserva. Informaremos sobre as condições de cancelamento e eventuais reembolsos aplicáveis.",
        "O cancelamento foi registado. De acordo com a nossa política, reservas canceladas com mais de 48 horas de antecedência têm direito a reembolso integral. Pode confirmar o número de reserva para verificarmos as condições específicas?",
        "Lamentamos não o/a poder receber como planeado. Para processar o cancelamento, pedimos que confirme o número de reserva e o motivo, caso pretenda beneficiar de isenção de taxa por motivos de força maior.",
    ],

    ("response_generation", "payment_failure"): [
        "Pedimos desculpa pelo problema no pagamento. Isto pode ocorrer por diversos motivos, como dados incorrectos ou limite do cartão atingido. Pode tentar novamente com os dados do cartão actualizados ou utilizar outro método de pagamento?",
        "Lamentamos o inconveniente com o pagamento. Para ajudarmos a resolver a situação, pode confirmar se os dados do cartão estão correctos e se existe saldo disponível? Em alternativa, podemos disponibilizar outros métodos de pagamento.",
        "O pagamento não foi processado com sucesso. Verificámos que pode ter ocorrido um erro na introdução dos dados ou uma recusa pelo banco emissor. Sugerimos contactar o banco ou tentar com um cartão diferente.",
    ],

    ("response_generation", "duplicate_charge"): [
        "Pedimos desculpa pela cobrança duplicada. Vamos verificar os registos de pagamento de imediato. Pode indicar-nos as datas e os valores das cobranças em questão? Após verificação, o valor cobrado em excesso será reembolsado.",
        "Lamentamos o erro na faturação. Para confirmarmos a cobrança duplicada, pode partilhar connosco os extractos ou referências das duas transacções? Assim que validarmos, processaremos o reembolso do valor cobrado a mais.",
        "Agradecemos o alerta sobre a cobrança duplicada. Estamos a verificar os registos de pagamento. Para agilizar, pode indicar-nos a data e o valor de cada cobrança? Resolveremos a situação com urgência.",
    ],

    # ── email_reply ────────────────────────────────────────────────────────

    ("email_reply", "refund_request"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu contacto e lamentamos a situação.\n\nPara darmos início ao processo de reembolso, solicitamos que nos envie o número da encomenda e, se aplicável, fotografias do artigo com defeito.\n\nApós validação, o reembolso será processado para o meio de pagamento original no prazo de 5 a 10 dias úteis.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nAcusamos a recepção do seu pedido de reembolso.\n\nPara procedermos ao tratamento do mesmo, necessitamos de:\n- Número da encomenda\n- Prova de compra\n- Descrição do problema\n\nAssim que recebermos esta informação, processaremos o pedido com prioridade.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "return_request"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu e-mail relativamente à devolução da encomenda.\n\nConfirmamos que o pedido de devolução foi registado. Para avançarmos com o processo, pedimos que:\n1. Embale o artigo na embalagem original\n2. Inclua a guia de devolução em anexo\n3. Entregue na transportadora mais próxima\n\nApós recepção e validação do artigo, o reembolso será processado.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nRecebemos o seu pedido de devolução e estamos a tratar do mesmo.\n\nPara completar o processo, por favor confirme o número de encomenda e o motivo da devolução. Enviaremos a etiqueta de devolução por e-mail em breve.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "order_status"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu contacto.\n\nInformamos que a sua encomenda [número] se encontra actualmente em trânsito e a entrega está prevista para [data]. Pode acompanhar o estado em tempo real através do link de tracking em anexo.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nEm resposta ao seu pedido de informação, a sua encomenda foi despachada e encontra-se com o transportador. O prazo de entrega estimado é de 2 a 3 dias úteis.\n\nCaso não receba a encomenda nesse prazo, não hesite em contactar-nos.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "delivery_delay"): [
        "Exmo(a). Sr(a).,\n\nPedimos desculpa pelo atraso verificado na entrega da sua encomenda.\n\nEstamos a acompanhar a situação com o transportador e aguardamos uma actualização. Assim que tivermos informações, contactaremos de imediato.\n\nAgradecemos a sua compreensão e lamentamos o inconveniente causado.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nAcusamos a recepção do seu e-mail e lamentamos o atraso na entrega.\n\nO atraso ficou a dever-se a [razão logística]. A nova data prevista de entrega é [data]. Caso o artigo não chegue nessa data, processaremos um reembolso integral.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "damaged_item"): [
        "Exmo(a). Sr(a).,\n\nLamentamos que o artigo tenha chegado em mau estado.\n\nPara procedermos à substituição ou reembolso, solicitamos o envio de fotografias do dano e do número de encomenda. Após análise, entraremos em contacto no prazo de 48 horas úteis.\n\nPedimos desculpa pelo inconveniente.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nRecebemos a sua reclamação relativamente ao artigo danificado e lamentamos a situação.\n\nVamos proceder à substituição imediata do artigo. Para tal, necessitamos de fotografias do estado em que chegou a encomenda. Pode enviá-las em resposta a este e-mail?\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "billing_question"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu contacto relativamente à fatura.\n\nEm resposta à sua dúvida, o valor faturado corresponde a [descrição dos itens]. Caso necessite de esclarecimentos adicionais ou identificar algum erro, não hesite em contactar-nos.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nAcusamos a recepção da sua questão sobre a fatura.\n\nConfirmamos que a fatura n.º [número] foi emitida correctamente e reflecte os serviços prestados no período [período]. Em caso de divergência, pedimos que nos indique o item em questão para verificarmos.\n\nAtenciosamente,\n[Nome da Empresa]",
        "Caro/a cliente,\n\n{opener} Recebemos a sua questão sobre a fatura de {domain_label}.\n\nIremos verificar os registos de cobrança e responder em detalhe até ao próximo dia útil. Caso tenha o número de fatura disponível, peça que o inclua na resposta para agilizarmos a análise.\n\n{closer}\n[Equipa de Suporte]",
    ],

    ("email_reply", "invoice_request"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o pedido de emissão de fatura.\n\nConfirmamos que a fatura referente à compra de [data] foi emitida e enviada em anexo. Caso necessite de dados diferentes, por favor indique-nos o NIF e morada fiscal actualizados.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nSegue em anexo a fatura solicitada, referente ao período [período].\n\nCaso necessitem de alguma rectificação ou emissão de nota de crédito, ficamos ao dispor.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "cancel_subscription"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu contacto e lamentamos a sua decisão.\n\nConfirmamos o cancelamento da subscrição com efeitos no final do período em curso ([data]). Continuará a ter acesso ao serviço até essa data.\n\nCaso mude de ideias ou necessite de mais informações, estamos ao dispor.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nO cancelamento da sua subscrição foi registado conforme solicitado.\n\nO acesso ao serviço mantém-se activo até [data de fim do período]. Não serão efectuadas cobranças adicionais.\n\nAgradecemos a sua preferência e esperamos poder servi-lo/a novamente no futuro.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "change_plan"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu pedido de alteração de plano.\n\nConfirmamos que o seu plano foi actualizado para [novo plano] com efeitos imediatos. O novo valor de [€X/mês] será cobrado a partir do próximo ciclo de faturação.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nA alteração do plano foi processada com sucesso. Passa a beneficiar das funcionalidades do [novo plano] de imediato.\n\nEm caso de dúvidas sobre as diferenças entre planos, estamos disponíveis para ajudar.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "technical_issue"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o contacto e lamentamos o problema técnico.\n\nA ocorrência foi registada e a nossa equipa de suporte técnico está a investigar a situação. Esperamos ter uma resolução no prazo de 4 horas úteis.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nRecebemos a sua comunicação sobre o problema técnico e estamos a trabalhar na resolução.\n\nComo medida imediata, sugerimos limpar a cache do browser e tentar novamente. Se o problema persistir, a nossa equipa técnica contactará por telefone nas próximas horas.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "password_reset"): [
        "Exmo(a). Sr(a).,\n\nSegue em anexo o link para redefinição da palavra-passe.\n\nO link é válido por 24 horas. Caso expire, pode solicitar um novo através da página de início de sessão.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nEnviámos um e-mail de recuperação de palavra-passe para o endereço registado na sua conta.\n\nCaso não o receba nos próximos minutos, verifique a pasta de spam. Se o problema persistir, podemos repor a palavra-passe manualmente após verificação de identidade.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "account_access"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o contacto relativamente ao problema de acesso à conta.\n\nVerificámos que a sua conta foi temporariamente bloqueada por motivos de segurança. Para proceder ao desbloqueio, é necessário verificar a sua identidade. Por favor responda a este e-mail com o número do documento de identificação.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nO problema de acesso foi identificado e estamos a trabalhar na resolução.\n\nO acesso à sua conta foi reactivado. Pode tentar iniciar sessão agora e, se persistir o problema, por favor contacte-nos novamente.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "complaint"): [
        "Exmo(a). Sr(a).,\n\nAcusamos a recepção da sua reclamação e lamentamos profundamente a experiência negativa que vivenciou.\n\nA sua reclamação foi registada sob o número [número] e será analisada com prioridade pela direcção. Comprometemo-nos a apresentar uma resposta fundamentada no prazo de 5 dias úteis.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nRecebemos a sua reclamação e pedimos desculpa pelo sucedido.\n\nO assunto foi encaminhado para o responsável da área. Pode esperar uma resposta detalhada no prazo de 48 horas. Agradecemos a oportunidade de melhorarmos o nosso serviço.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "escalation_request"): [
        "Exmo(a). Sr(a).,\n\nAcusamos a recepção do seu pedido de escalamento.\n\nA sua situação foi encaminhada para a direcção de serviço ao cliente. Um responsável sénior entrará em contacto consigo nas próximas 4 horas úteis.\n\nPedimos desculpa pelo transtorno e agradecemos a sua paciência.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nO seu pedido de escalamento foi recebido e tratado com prioridade máxima.\n\nO supervisor responsável pela sua conta irá contactá-lo/a directamente por telefone hoje. Lamentamos que a situação tenha chegado a este ponto.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "booking_change"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o seu contacto relativamente à alteração da reserva.\n\nConfirmamos que a reserva n.º [número] foi alterada para [nova data/hora], conforme solicitado. Segue em anexo a confirmação actualizada.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nA alteração da sua reserva foi processada com sucesso.\n\nNova data: [data] | Nova hora: [hora] | Referência: [número de reserva]\n\nCaso necessite de efectuar mais alterações, por favor contacte-nos com pelo menos 48 horas de antecedência.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "booking_cancellation"): [
        "Exmo(a). Sr(a).,\n\nAcusamos a recepção do seu pedido de cancelamento da reserva n.º [número].\n\nO cancelamento foi processado. De acordo com as condições da tarifa contratada, será reembolsado/a no valor de [€X] no prazo de 5 a 10 dias úteis.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nConfirmamos o cancelamento da sua reserva conforme solicitado.\n\nLamentamos não o/a poder receber. O reembolso, quando aplicável, será processado para o meio de pagamento original em breve.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "payment_failure"): [
        "Exmo(a). Sr(a).,\n\nInformamos que o pagamento referente à sua encomenda/serviço não foi processado com sucesso.\n\nAs causas mais comuns são dados de cartão incorrectos ou limite insuficiente. Por favor actualize os dados de pagamento através da sua área de cliente ou contacte-nos para outras opções.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nO seu pagamento não foi concluído com sucesso.\n\nPode tentar novamente com um cartão diferente ou através de transferência bancária para o NIB [número]. Caso necessite de assistência, estamos disponíveis por telefone.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    ("email_reply", "duplicate_charge"): [
        "Exmo(a). Sr(a).,\n\nAgradecemos o alerta relativamente à cobrança duplicada.\n\nVerificámos os registos e confirmamos que efectivamente foi cobrado o valor em duplicado. O montante de [€X] será reembolsado para o cartão original no prazo de 5 a 10 dias úteis.\n\nPedimos desculpa pelo erro.\n\nCom os melhores cumprimentos,\n[Nome da Empresa]",
        "Caro/a cliente,\n\nAcusamos a recepção da sua comunicação sobre a cobrança em duplicado.\n\nEstamos a verificar os registos de pagamento com urgência. Assim que confirmarmos a duplicação, o reembolso será processado de imediato. Agradecemos a sua paciência.\n\nAtenciosamente,\n[Nome da Empresa]",
    ],

    # ── summarization ──────────────────────────────────────────────────────

    ("summarization", "refund_request"): [
        "O cliente solicita o reembolso de um valor considerado indevido ou incorrectamente cobrado.",
        "O cliente reporta um problema com uma cobrança ou compra e pretende ser reembolsado na totalidade.",
        "O cliente pede a devolução de um montante pago, indicando que o produto ou serviço não correspondeu ao esperado.",
        "O cliente efectuou um pagamento indevido e solicita o respectivo reembolso.",
    ],

    ("summarization", "return_request"): [
        "O cliente pretende devolver um artigo adquirido recentemente, apresentando insatisfação com o produto.",
        "O cliente solicita a abertura de um processo de devolução, indicando que o artigo não corresponde às suas expectativas.",
        "O cliente deseja proceder à devolução da encomenda dentro do prazo permitido pela política de devoluções.",
    ],

    ("summarization", "order_status"): [
        "O cliente questiona o estado actual da sua encomenda e aguarda informação sobre a data prevista de entrega.",
        "O cliente não recebeu actualizações sobre o estado da encomenda e solicita esclarecimento.",
        "O cliente pede confirmação do estado de expedição e do prazo de entrega estimado.",
    ],

    ("summarization", "delivery_delay"): [
        "O cliente reporta que o envio não chegou dentro do prazo previsto e solicita uma explicação para o atraso.",
        "O cliente informa que o prazo de entrega foi ultrapassado e pede uma actualização sobre o estado do envio.",
        "O cliente está preocupado com o atraso na entrega do equipamento ou encomenda e pretende saber quando pode esperar recebê-los.",
        "O cliente aguarda uma entrega já em atraso e solicita contacto urgente para esclarecimento.",
    ],

    ("summarization", "damaged_item"): [
        "O cliente recebeu um artigo danificado e reporta o problema, solicitando substituição ou reembolso.",
        "O cliente informa que a embalagem e o artigo chegaram em mau estado, pedindo resolução urgente.",
        "O cliente recebeu a encomenda com danos visíveis e pretende formalizar a reclamação para obter compensação.",
    ],

    ("summarization", "billing_question"): [
        "O cliente tem uma dúvida relativamente ao valor ou detalhe de um item na sua fatura.",
        "O cliente questiona uma cobrança específica na fatura e pede esclarecimento sobre a sua origem.",
        "O cliente não reconhece um valor na fatura e solicita informação adicional sobre o que está a ser cobrado.",
    ],

    ("summarization", "invoice_request"): [
        "O cliente solicita a emissão ou reenvio de fatura referente a uma compra ou serviço.",
        "O cliente necessita de fatura com os dados da empresa para efeitos contabilísticos.",
        "O cliente pede o envio da fatura para o endereço de e-mail registado.",
    ],

    ("summarization", "cancel_subscription"): [
        "O cliente pretende cancelar a sua subscrição, solicitando que o serviço seja terminado.",
        "O cliente deseja encerrar a conta e deixar de ser cobrado pelo serviço.",
        "O cliente solicita o cancelamento da subscrição com efeitos imediatos ou no final do período de faturação.",
    ],

    ("summarization", "change_plan"): [
        "O cliente pretende alterar o plano de subscrição actual para um plano diferente.",
        "O cliente solicita a mudança para um plano superior ou inferior, conforme as suas necessidades.",
        "O cliente quer actualizar o plano contratado e questiona as opções disponíveis.",
    ],

    ("summarization", "technical_issue"): [
        "O cliente reporta um problema técnico na plataforma que está a impedir o uso normal do serviço.",
        "O cliente está a experienciar erros no acesso ou funcionamento da aplicação e solicita suporte técnico.",
        "O cliente informa que o serviço está com falhas e pede assistência para resolver o problema.",
        "O cliente reporta uma falha técnica em {domain_label} que impede o uso normal do serviço. O problema ocorre desde [data/hora indicada] e afecta [função específica descrita]. Requer análise técnica prioritária.",
    ],

    ("summarization", "password_reset"): [
        "O cliente esqueceu-se da palavra-passe e não consegue aceder à conta, solicitando recuperação.",
        "O cliente não está a receber o e-mail de reposição de palavra-passe e pede assistência.",
        "O cliente solicita a reposição da palavra-passe para recuperar o acesso à sua conta.",
    ],

    ("summarization", "account_access"): [
        "O cliente não consegue aceder à sua conta e reporta problemas de autenticação.",
        "O cliente informa que a conta está bloqueada ou inacessível e necessita de suporte para recuperar o acesso.",
        "O cliente está a receber erros ao tentar iniciar sessão e pede ajuda para resolver o problema.",
    ],

    ("summarization", "complaint"): [
        "O cliente está insatisfeito com o serviço prestado e deseja registar uma reclamação formal.",
        "O cliente reporta uma experiência negativa e solicita que o assunto seja tratado com urgência.",
        "O cliente apresenta uma reclamação sobre a qualidade do serviço ou atendimento recebido.",
    ],

    ("summarization", "escalation_request"): [
        "O cliente está insatisfeito com as respostas recebidas e solicita falar com um responsável ou supervisor.",
        "O cliente pretende escalar o problema para um nível superior de suporte, pois considera que a situação não foi resolvida.",
        "O cliente exige contacto com um supervisor após não obter resolução satisfatória para o seu problema.",
    ],

    ("summarization", "booking_change"): [
        "O cliente solicita alteração da data, hora ou outros detalhes da sua reserva.",
        "O cliente pretende modificar os dados de uma reserva existente, indicando as novas preferências.",
        "O cliente quer alterar a sua reserva antes da data confirmada.",
    ],

    ("summarization", "booking_cancellation"): [
        "O cliente pretende cancelar uma reserva e questiona as condições de reembolso aplicáveis.",
        "O cliente necessita de cancelar a viagem ou serviço reservado e solicita a devolução do valor pago.",
        "O cliente solicita o cancelamento da reserva devido a um imprevisto.",
    ],

    ("summarization", "payment_failure"): [
        "O cliente informa que a tentativa de pagamento foi recusada e pede ajuda para resolver o problema.",
        "O cliente não conseguiu concluir o pagamento e solicita assistência para identificar a causa.",
        "O cliente reporta falha no processamento do pagamento e pede alternativas.",
    ],

    ("summarization", "duplicate_charge"): [
        "O cliente detectou uma cobrança duplicada na sua fatura e solicita o reembolso do valor cobrado em excesso.",
        "O cliente informa que foi debitado duas vezes pelo mesmo serviço ou produto e pretende resolução.",
        "O cliente reporta uma cobrança repetida e pede verificação urgente dos registos de pagamento.",
    ],

    # ── rewrite_professional ───────────────────────────────────────────────

    ("rewrite_professional", "refund_request"): [
        "Venho por este meio solicitar o reembolso do valor pago, dado que o artigo recebido apresenta defeito. Agradeço que me indiquem os procedimentos necessários para formalizar o pedido.",
        "Solicito formalmente o reembolso referente à encomenda n.º [número], uma vez que o produto recebido não está em conformidade com o descrito. Aguardo indicação dos passos a seguir.",
    ],

    ("rewrite_professional", "return_request"): [
        "Venho por este meio solicitar a devolução do artigo adquirido, o qual não corresponde às minhas expectativas. Agradeço que me indiquem o procedimento a seguir.",
        "Solicito formalmente a abertura de um processo de devolução relativo à encomenda n.º [número]. Aguardo as instruções necessárias para proceder à devolução.",
    ],

    ("rewrite_professional", "order_status"): [
        "Venho solicitar informação actualizada sobre o estado da encomenda n.º [número], efetuada em [data]. Agradeço que me confirmem o prazo previsto de entrega.",
        "Solicito informação relativamente ao estado actual da minha encomenda. Agradeço que me indiquem se a mesma já foi expedida e qual a data estimada de entrega.",
    ],

    ("rewrite_professional", "delivery_delay"): [
        "Venho informar que a encomenda n.º [número], com entrega prevista para [data], ainda não foi recebida. Solicito esclarecimentos sobre o motivo do atraso e nova data prevista.",
        "Verifico que o prazo de entrega da minha encomenda foi ultrapassado. Solicito, por favor, uma actualização urgente sobre o estado do envio.",
    ],

    ("rewrite_professional", "damaged_item"): [
        "Venho comunicar que a encomenda n.º [número] foi recebida com o artigo danificado. Solicito indicação sobre os procedimentos para substituição ou reembolso.",
        "Informo que o produto recebido apresenta danos visíveis. Solicito a abertura de reclamação e indicação das opções de substituição ou reembolso disponíveis.",
    ],

    ("rewrite_professional", "billing_question"): [
        "Venho solicitar esclarecimento relativamente a um item constante na fatura n.º [número], cujo valor não reconheço. Agradeço informação detalhada sobre a origem desta cobrança.",
        "Solicito esclarecimento sobre o montante faturado no período de [data]. O valor apresentado não está de acordo com o contratado. Aguardo confirmação dos detalhes.",
    ],

    ("rewrite_professional", "invoice_request"): [
        "Venho solicitar a emissão de fatura referente à compra efectuada em [data], com os dados fiscais indicados em anexo.",
        "Solicito, por favor, o envio da fatura relativa ao serviço prestado no mês de [mês]. Os dados de facturação constam da minha conta.",
    ],

    ("rewrite_professional", "cancel_subscription"): [
        "Venho comunicar a minha intenção de cancelar a subscrição actualmente activa, com efeitos a partir do final do período de facturação em curso.",
        "Solicito formalmente o cancelamento da minha subscrição. Agradeço que confirmem a data de efectivação do cancelamento e as condições aplicáveis.",
    ],

    ("rewrite_professional", "change_plan"): [
        "Venho solicitar a alteração do meu plano actual para o plano [nome do plano]. Agradeço que confirmem a data de efectivação e o novo valor a cobrar.",
        "Solicito a mudança do meu plano de subscrição para o nível imediatamente superior. Aguardo confirmação da alteração e respectivos custos.",
    ],

    ("rewrite_professional", "technical_issue"): [
        "Venho reportar um problema técnico que está a afectar o acesso ao serviço. O problema ocorre desde [data] e impede a realização normal das minhas tarefas. Solicito assistência com urgência.",
        "Comunico que estou a experienciar dificuldades técnicas no acesso à plataforma. Solicito que a situação seja analisada e resolvida com a maior brevidade possível.",
    ],

    ("rewrite_professional", "password_reset"): [
        "Venho solicitar a reposição da palavra-passe da minha conta, pois não estou a conseguir aceder com as credenciais actuais.",
        "Solicito apoio na recuperação de acesso à minha conta. Não me é possível concluir a reposição da palavra-passe através do processo automático.",
    ],

    ("rewrite_professional", "account_access"): [
        "Venho informar que não me é possível aceder à minha conta de utilizador. Solicito que verifiquem a situação e procedam ao desbloqueio com urgência.",
        "Solicito apoio na resolução de um problema de acesso à conta. Continuo a receber mensagem de erro ao tentar iniciar sessão.",
    ],

    ("rewrite_professional", "complaint"): [
        "Venho apresentar reclamação formal relativamente ao serviço prestado, o qual ficou abaixo das expectativas. Solicito que o assunto seja analisado e que me seja apresentada uma resposta fundamentada.",
        "Solicito o registo formal de uma reclamação relativa ao atendimento recebido. A situação causou-me transtorno significativo e aguardo resolução adequada.",
    ],

    ("rewrite_professional", "escalation_request"): [
        "Dado que as respostas recebidas não resolveram o problema em questão, solicito formalmente o escalamento do caso para um responsável superior.",
        "Venho solicitar que o meu processo seja reencaminhado para um supervisor, uma vez que não obtive resolução satisfatória através dos canais habituais.",
    ],

    ("rewrite_professional", "booking_change"): [
        "Venho solicitar a alteração da minha reserva n.º [número] para a data de [nova data]. Agradeço confirmação da disponibilidade e eventuais custos adicionais.",
        "Solicito a modificação dos dados da reserva efectuada, nomeadamente a alteração da data de [data actual] para [nova data].",
    ],

    ("rewrite_professional", "booking_cancellation"): [
        "Venho comunicar o cancelamento da reserva n.º [número], com pedido de reembolso nos termos da política aplicável.",
        "Solicito o cancelamento da reserva efectuada em [data], informando que as condições para reembolso integral se encontram reunidas.",
    ],

    ("rewrite_professional", "payment_failure"): [
        "Venho informar que a tentativa de pagamento referente à encomenda n.º [número] não foi concluída com sucesso. Solicito assistência para identificar a causa e concluir o pagamento.",
        "Solicito ajuda na resolução de um problema no processamento do pagamento. A transacção foi recusada sem que tenha sido apresentado o motivo.",
    ],

    ("rewrite_professional", "duplicate_charge"): [
        "Venho informar que foi efectuada uma cobrança duplicada referente ao serviço/produto [descrição]. Solicito a devolução do montante cobrado em excesso com a maior brevidade.",
        "Verifico que fui debitado/a duas vezes pelo mesmo valor. Solicito a confirmação da duplicação e o reembolso do valor indevidamente cobrado.",
    ],

    # ── next_action_suggestion ─────────────────────────────────────────────

    ("next_action_suggestion", "refund_request"): [
        "1. Solicitar o número da encomenda e prova de compra ao cliente.\n2. Verificar o estado da encomenda no sistema.\n3. Confirmar se o artigo foi devolvido ou se ainda está com o cliente.\n4. Processar o reembolso para o meio de pagamento original.",
        "1. Pedir ao cliente fotografias do artigo com defeito.\n2. Registar a ocorrência no sistema de reclamações.\n3. Aprovar o pedido de reembolso após verificação.\n4. Notificar o cliente por e-mail sobre o prazo de reembolso.",
    ],

    ("next_action_suggestion", "return_request"): [
        "1. Confirmar o número da encomenda e a elegibilidade para devolução (prazo de 30 dias).\n2. Enviar a etiqueta de devolução por e-mail.\n3. Aguardar a recepção do artigo devolvido.\n4. Processar o reembolso após inspecção do artigo.",
        "1. Verificar se a encomenda está dentro do prazo de devolução.\n2. Fornecer ao cliente as instruções de embalagem e recolha.\n3. Registar o pedido de devolução no sistema.\n4. Confirmar ao cliente quando o reembolso será processado.",
    ],

    ("next_action_suggestion", "order_status"): [
        "1. Pesquisar a encomenda no sistema com o número fornecido pelo cliente.\n2. Verificar o estado actual junto do parceiro logístico.\n3. Fornecer ao cliente o link de tracking activo.\n4. Se houver atraso, escalar para equipa de logística.",
        "1. Localizar a encomenda no sistema de gestão.\n2. Verificar se a encomenda foi expedida e o tracking disponível.\n3. Informar o cliente do estado actual e data estimada.\n4. Registar o contacto para follow-up se necessário.",
    ],

    ("next_action_suggestion", "delivery_delay"): [
        "1. Verificar o tracking da encomenda junto do transportador.\n2. Identificar a causa do atraso (operacional, logístico ou meteorológico).\n3. Comunicar ao cliente a nova data prevista de entrega.\n4. Oferecer compensação se o atraso for significativo.",
        "1. Contactar o transportador para localização da encomenda.\n2. Registar o atraso no sistema e associar à encomenda.\n3. Informar o cliente com actualização e novo prazo.\n4. Se o atraso superar 7 dias, oferecer reembolso ou reenvio.",
    ],

    ("next_action_suggestion", "damaged_item"): [
        "1. Solicitar fotografias do artigo e da embalagem danificada.\n2. Registar a ocorrência no sistema de qualidade.\n3. Decidir entre substituição ou reembolso com base na disponibilidade.\n4. Organizar a recolha do artigo danificado, se necessário.",
        "1. Documentar o dano com base nas fotografias recebidas.\n2. Aprovar substituição imediata do artigo.\n3. Enviar nova encomenda com tracking prioritário.\n4. Notificar o cliente e fechar a ocorrência.",
    ],

    ("next_action_suggestion", "billing_question"): [
        "1. Localizar a fatura em questão no sistema.\n2. Detalhar os itens que compõem o valor cobrado.\n3. Comparar com o contrato ou encomenda original.\n4. Emitir nota de crédito se existir erro de facturação.",
        "1. Verificar o histórico de facturação do cliente.\n2. Identificar o item ou período em questão.\n3. Fornecer explicação detalhada por escrito.\n4. Corrigir a fatura se necessário e reenviar.",
    ],

    ("next_action_suggestion", "invoice_request"): [
        "1. Verificar os dados fiscais do cliente no sistema.\n2. Emitir a fatura com o NIF e morada indicados.\n3. Enviar por e-mail no prazo de 24 horas úteis.\n4. Confirmar recepção com o cliente.",
        "1. Aceder ao registo da compra ou serviço.\n2. Gerar a fatura com os dados de facturação fornecidos.\n3. Enviar a fatura em formato PDF para o e-mail do cliente.\n4. Arquivar cópia no sistema.",
    ],

    ("next_action_suggestion", "cancel_subscription"): [
        "1. Verificar o tipo de plano e as condições de cancelamento.\n2. Confirmar a data de efectivação pretendida pelo cliente.\n3. Processar o cancelamento no sistema.\n4. Enviar confirmação por e-mail com a data de término.",
        "1. Informar o cliente sobre o que acontece após o cancelamento (acesso até ao fim do período).\n2. Confirmar a intenção de cancelamento.\n3. Processar o pedido no sistema.\n4. Enviar e-mail de confirmação com resumo.",
    ],

    ("next_action_suggestion", "change_plan"): [
        "1. Apresentar as opções de plano disponíveis com preços e funcionalidades.\n2. Confirmar a escolha do cliente.\n3. Processar a alteração no sistema com efeitos imediatos.\n4. Enviar confirmação e nova fatura pro-rata se aplicável.",
        "1. Verificar o plano actual e os planos disponíveis.\n2. Informar o cliente sobre diferenças e custos.\n3. Efectuar a alteração após confirmação.\n4. Confirmar por e-mail a alteração e a data de efectivação.",
    ],

    ("next_action_suggestion", "technical_issue"): [
        "1. Recolher detalhes do problema: browser, sistema operativo, mensagem de erro.\n2. Tentar reproduzir o erro internamente.\n3. Aplicar solução de primeiro nível (limpar cache, reiniciar sessão).\n4. Escalar para equipa técnica se não resolver.",
        "1. Registar o incidente no sistema de suporte técnico.\n2. Enviar ao cliente passos básicos de diagnóstico.\n3. Verificar se outros clientes reportam o mesmo problema.\n4. Fornecer prazo estimado de resolução.",
    ],

    ("next_action_suggestion", "password_reset"): [
        "1. Verificar se o e-mail de recuperação foi enviado.\n2. Orientar o cliente a verificar a pasta de spam.\n3. Reenviar o link de recuperação se necessário.\n4. Se persistir, repor a palavra-passe manualmente após verificação de identidade.",
        "1. Confirmar o endereço de e-mail associado à conta.\n2. Acionar o processo de recuperação de palavra-passe.\n3. Confirmar que o cliente recebeu o e-mail.\n4. Acompanhar até ao acesso bem-sucedido.",
    ],

    ("next_action_suggestion", "account_access"): [
        "1. Verificar o estado da conta no sistema (activa, bloqueada, suspensa).\n2. Identificar a causa do bloqueio.\n3. Desbloquear a conta após verificação de identidade.\n4. Confirmar o acesso com o cliente.",
        "1. Pesquisar a conta pelo e-mail ou número de cliente.\n2. Verificar o registo de tentativas de acesso falhadas.\n3. Proceder ao desbloqueio ou redefinição de credenciais.\n4. Informar o cliente e recomendar alteração de palavra-passe.",
    ],

    ("next_action_suggestion", "complaint"): [
        "1. Registar a reclamação formalmente no sistema com número de referência.\n2. Escalar para o departamento responsável.\n3. Contactar o cliente no prazo de 24 horas com acuse de recibo.\n4. Apresentar resposta fundamentada no prazo de 5 dias úteis.",
        "1. Ouvir o cliente e documentar todos os factos da reclamação.\n2. Pedir desculpa e reconhecer o problema.\n3. Definir um plano de resolução com prazo.\n4. Fazer follow-up após resolução para garantir satisfação.",
    ],

    ("next_action_suggestion", "escalation_request"): [
        "1. Reconhecer a insatisfação do cliente e pedir desculpa.\n2. Registar o pedido de escalamento com urgência máxima.\n3. Transferir para supervisor disponível de imediato.\n4. Confirmar ao cliente o nome e contacto do supervisor.",
        "1. Notificar o supervisor responsável da situação.\n2. Fornecer ao supervisor o histórico completo do caso.\n3. Confirmar ao cliente o tempo de resposta (máx. 4 horas).\n4. Monitorizar até à resolução.",
        "1. Verificar o histórico completo de interacções do cliente em {domain_label}.\n2. Escalar o caso para supervisor de {domain_label} com sumário do problema.\n3. Contactar o cliente em menos de duas horas com confirmação do escalamento.\n4. Agendar chamada com o cliente para resolução directa.",
    ],

    ("next_action_suggestion", "booking_change"): [
        "1. Verificar a disponibilidade para as novas datas/condições solicitadas.\n2. Informar o cliente sobre eventuais custos de alteração.\n3. Processar a alteração após confirmação.\n4. Enviar nova confirmação de reserva por e-mail.",
        "1. Consultar a política de alterações da tarifa contratada.\n2. Verificar disponibilidade para a nova data.\n3. Efectuar a alteração no sistema.\n4. Confirmar e enviar nova documentação de reserva.",
    ],

    ("next_action_suggestion", "booking_cancellation"): [
        "1. Verificar as condições de cancelamento da tarifa (reembolsável/não reembolsável).\n2. Calcular o valor de reembolso aplicável.\n3. Processar o cancelamento.\n4. Informar o cliente e processar o reembolso.",
        "1. Confirmar a identidade do cliente e o número de reserva.\n2. Verificar a política de cancelamento.\n3. Processar o cancelamento no sistema.\n4. Enviar confirmação por e-mail com detalhe do reembolso.",
    ],

    ("next_action_suggestion", "payment_failure"): [
        "1. Verificar o erro de pagamento no sistema (código de recusa).\n2. Informar o cliente sobre a causa provável.\n3. Orientar sobre como actualizar os dados de pagamento.\n4. Oferecer métodos de pagamento alternativos.",
        "1. Analisar o log de pagamento para identificar o erro.\n2. Sugerir ao cliente que contacte o banco emissor.\n3. Disponibilizar link para nova tentativa de pagamento.\n4. Confirmar quando o pagamento for concluído com sucesso.",
    ],

    ("next_action_suggestion", "duplicate_charge"): [
        "1. Verificar os registos de pagamento para confirmar a duplicação.\n2. Identificar a transacção original e a duplicada.\n3. Iniciar o processo de reembolso do valor cobrado a mais.\n4. Notificar o cliente com confirmação e prazo de devolução.",
        "1. Aceder ao histórico de transacções do cliente.\n2. Confirmar as duas cobranças pelo mesmo valor/referência.\n3. Cancelar ou estornar a transacção duplicada.\n4. Enviar comprovativo de reembolso ao cliente.",
    ],

    # ── faq_answer ─────────────────────────────────────────────────────────

    ("faq_answer", "refund_request"): [
        "Para solicitar um reembolso, aceda à sua área de cliente, seleccione a encomenda e clique em 'Pedir Reembolso'. O prazo de devolução é de 30 dias após a entrega. O reembolso é processado no prazo de 5 a 10 dias úteis para o meio de pagamento original.",
        "Os reembolsos são processados no prazo de 5 a 10 dias úteis após aprovação. Para iniciar o pedido, é necessário indicar o número de encomenda e, em caso de defeito, enviar fotografias do artigo.",
    ],

    ("faq_answer", "return_request"): [
        "Aceita-se a devolução de artigos no prazo de 30 dias após a data de entrega. O artigo deve estar em perfeitas condições e na embalagem original. Para iniciar a devolução, contacte o suporte ou aceda à área de cliente.",
        "Para devolver um artigo, aceda à sua conta, seleccione a encomenda e solicite a devolução. Receberá uma etiqueta de envio gratuita por e-mail. Após recepção e verificação do artigo, o reembolso é processado em 5 dias úteis.",
    ],

    ("faq_answer", "order_status"): [
        "Pode verificar o estado da sua encomenda em tempo real através da área de cliente ou do link de tracking enviado por e-mail após a expedição. O estado é actualizado automaticamente pelo transportador.",
        "O estado da encomenda está disponível na área de cliente em 'As Minhas Encomendas'. Após expedição, receberá um e-mail com o número de tracking para acompanhar a entrega.",
    ],

    ("faq_answer", "delivery_delay"): [
        "Em caso de atraso na entrega, pode verificar o estado no link de tracking ou contactar o suporte. Se a encomenda não chegar no prazo de 7 dias após a data prevista, tem direito a reembolso integral.",
        "Os prazos de entrega podem variar por motivos logísticos ou meteorológicos. Em caso de atraso, será notificado por e-mail com a nova data estimada. Para reclamações, contacte o suporte indicando o número de encomenda.",
    ],

    ("faq_answer", "damaged_item"): [
        "Se recebeu um artigo danificado, deve reportá-lo no prazo de 48 horas após entrega, através do suporte ou da área de cliente. Envie fotografias do dano para agilizar o processo de substituição ou reembolso.",
        "Em caso de artigo danificado, a substituição é efectuada sem custos adicionais. Para iniciar o processo, contacte o suporte com o número de encomenda e fotografias do estado do artigo.",
    ],

    ("faq_answer", "billing_question"): [
        "Todas as faturas estão disponíveis na área de cliente em 'Faturas e Pagamentos'. Caso identifique um erro numa cobrança, contacte o suporte com o número de fatura e o item em questão para verificação.",
        "Para esclarecer dúvidas sobre faturas, pode aceder ao histórico de faturas na sua área de cliente. Cada fatura detalha os serviços cobrados, o período correspondente e o método de pagamento utilizado.",
    ],

    ("faq_answer", "invoice_request"): [
        "As faturas são emitidas automaticamente após cada compra e enviadas para o e-mail registado. Pode também solicitar a emissão ou reenvio através do suporte, indicando os dados fiscais correctos.",
        "Para obter uma fatura com dados de empresa, deve indicar o NIF e morada fiscal antes de finalizar a compra. Caso já tenha efectuado a compra, pode solicitar a rectificação da fatura contactando o suporte no prazo de 30 dias.",
    ],

    ("faq_answer", "cancel_subscription"): [
        "Para cancelar a subscrição, aceda a 'Definições de Conta' e seleccione 'Cancelar Subscrição'. O cancelamento é efectuado no final do período de faturação em curso, mantendo o acesso até essa data.",
        "O cancelamento pode ser solicitado a qualquer momento. Continuará a ter acesso ao serviço até ao final do período já pago. Não são efectuados reembolsos por períodos parciais.",
    ],

    ("faq_answer", "change_plan"): [
        "Para alterar o plano, aceda a 'Definições de Conta' e seleccione 'Alterar Plano'. A alteração entra em vigor imediatamente. Em caso de upgrade, o valor é cobrado pro-rata; em downgrade, o novo valor aplica-se no próximo ciclo.",
        "Pode alterar o plano em qualquer momento através da área de cliente. Upgrades são aplicados de imediato; downgrades entram em vigor no próximo ciclo de faturação.",
    ],

    ("faq_answer", "technical_issue"): [
        "Para problemas técnicos, sugerimos: (1) limpar a cache do browser, (2) tentar noutro browser ou dispositivo, (3) verificar a ligação à internet. Se o problema persistir, contacte o suporte técnico com descrição do erro.",
        "Em caso de problema técnico, verifique primeiro o estado do serviço em [página de status]. Se o serviço estiver operacional, limpe a cache e tente novamente. Para assistência directa, contacte o suporte.",
    ],

    ("faq_answer", "password_reset"): [
        "Para repor a palavra-passe, clique em 'Esqueceu a palavra-passe?' na página de início de sessão. Receberá um e-mail com um link de recuperação válido por 24 horas. Verifique também a pasta de spam.",
        "A reposição de palavra-passe é feita através do link enviado para o e-mail registado na conta. Se não receber o e-mail, verifique a pasta de spam ou contacte o suporte para reposição manual.",
    ],

    ("faq_answer", "account_access"): [
        "Se não consegue aceder à conta, verifique: (1) se está a utilizar o e-mail correcto, (2) se a palavra-passe está correcta, (3) se a conta foi bloqueada por tentativas falhadas. Em caso de bloqueio, contacte o suporte.",
        "Problemas de acesso podem ser resolvidos através da reposição de palavra-passe ou desbloqueio de conta. Se a conta estiver suspensa, é necessário contactar o suporte para verificar a situação.",
    ],

    ("faq_answer", "complaint"): [
        "Para registar uma reclamação formal, pode utilizar o formulário de contacto, enviar e-mail para [endereço de reclamações] ou contactar o livro de reclamações electrónico em [portal]. O prazo de resposta é de 5 dias úteis.",
        "As reclamações podem ser submetidas através do portal de suporte ou por escrito. Todas as reclamações são registadas e respondidas no prazo máximo de 5 dias úteis por um responsável de qualidade.",
    ],

    ("faq_answer", "escalation_request"): [
        "Para falar com um supervisor, pode solicitar escalamento através do suporte ou indicar explicitamente que deseja falar com um responsável. O prazo de resposta de um supervisor é de 4 horas úteis.",
        "Em caso de insatisfação com a resposta recebida, pode pedir o escalamento do caso. Um supervisor ou gestor de conta entrará em contacto no prazo máximo de um dia útil.",
    ],

    ("faq_answer", "booking_change"): [
        "Alterações de reserva são possíveis até [X] horas antes da data marcada, sujeitas a disponibilidade. Algumas tarifas podem incluir taxas de alteração. Para modificar a reserva, aceda à área de cliente ou contacte o suporte.",
        "Para alterar uma reserva, aceda a 'As Minhas Reservas' na área de cliente e seleccione a opção de alteração. As condições variam conforme a tarifa contratada.",
    ],

    ("faq_answer", "booking_cancellation"): [
        "O cancelamento de reservas está sujeito às condições da tarifa contratada. Tarifas reembolsáveis permitem cancelamento gratuito até [X] dias antes. Tarifas não reembolsáveis não dão direito a reembolso.",
        "Para cancelar uma reserva, aceda à área de cliente e seleccione a opção de cancelamento. O reembolso, quando aplicável, é processado em 5 a 10 dias úteis para o meio de pagamento original.",
    ],

    ("faq_answer", "payment_failure"): [
        "Pagamentos recusados podem ocorrer por: dados incorrectos do cartão, limite insuficiente, ou recusa do banco emissor. Verifique os dados do cartão e tente novamente. Se persistir, contacte o seu banco ou utilize outro método de pagamento.",
        "Em caso de falha de pagamento, verifique se os dados do cartão estão actualizados e se existe saldo disponível. Pode também utilizar transferência bancária ou outro método de pagamento disponível.",
    ],

    ("faq_answer", "duplicate_charge"): [
        "Se detectou uma cobrança duplicada, contacte o suporte com as referências das duas transacções. Após confirmação, o reembolso é processado no prazo de 5 a 10 dias úteis para o meio de pagamento original.",
        "Cobranças duplicadas são corrigidas mediante verificação. Apresente o extracto bancário ou as referências das transacções ao suporte. O valor cobrado em excesso será reembolsado assim que a duplicação for confirmada.",
    ],
}


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
