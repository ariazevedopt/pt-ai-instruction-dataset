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


TONE_MESSAGES: dict[str, dict[str, list[str]]] = {
    "refund_request": {
        "calm": [
            "Gostaria de solicitar o reembolso relativo à minha encomenda.",
            "Seria possível processar o reembolso do valor pago?",
            "Venho solicitar, de forma cordial, a devolução do montante pago.",
            "Gostaria de saber como proceder para obter o reembolso da encomenda.",
        ],
        "confused": [
            "Não percebo bem como funciona o processo de reembolso — podem ajudar-me?",
            "Fiz uma devolução mas não sei se o reembolso já foi processado.",
            "Não sei se tenho direito ao reembolso — alguém me pode explicar?",
            "Recebi uma mensagem sobre o reembolso mas não entendi o que fazer a seguir.",
        ],
        "frustrated": [
            "Já pedi o reembolso há semanas e ainda não recebi nada — isto é inaceitável!",
            "Exijo o reembolso imediato — não vou continuar a esperar por uma resposta.",
            "Já contactei o apoio três vezes e o reembolso continua por resolver. Vergonha!",
            "O produto chegou com defeito e ainda estou à espera do dinheiro de volta. Absurdo!",
        ],
        "urgent": [
            "Preciso do reembolso com urgência — o valor é significativo para mim.",
            "É urgente que processem o reembolso hoje, caso contrário terei de escalar.",
            "Necessito que o reembolso seja efectuado imediatamente, por favor.",
            "Aguardo o reembolso com urgência — já passaram os prazos acordados.",
        ],
        "formal": [
            "Venho por este meio solicitar formalmente o reembolso referente à encomenda n.º [X].",
            "Requeiro a devolução do montante cobrado indevidamente, ao abrigo dos direitos do consumidor.",
            "Em cumprimento da legislação aplicável, solicito o reembolso no prazo legal previsto.",
        ],
        "informal": [
            "Olá, queria pedir o reembolso da encomenda, ok?",
            "Olá, podem devolver o dinheiro da compra que fiz?",
            "Ok, preciso do reembolso — como faço isso?",
            "Olá, devolvi o artigo e quero o dinheiro de volta, pode ser?",
        ],
    },
    "return_request": {
        "calm": [
            "Gostaria de devolver o produto que recebi — como devo proceder?",
            "Seria possível iniciar uma devolução para a encomenda recente?",
            "Quero devolver o artigo e gostaria de conhecer o processo.",
            "Podem indicar-me os passos para efectuar a devolução, por favor?",
        ],
        "confused": [
            "Não sei bem como funciona a política de devoluções — podem explicar?",
            "Tentei perceber como devolver o artigo mas não encontrei a informação.",
            "Não estou a perceber se posso devolver — qual é o prazo?",
            "Tenho dúvidas sobre se o artigo é elegível para devolução.",
        ],
        "frustrated": [
            "O produto não corresponde ao que encomendei e quero devolvê-lo já!",
            "Já tentei devolver este artigo duas vezes sem sucesso — é inaceitável.",
            "A qualidade é péssima e exijo poder devolver sem complicações.",
            "Fui enganado com a descrição do produto e quero a devolução imediata.",
        ],
        "urgent": [
            "Preciso de devolver o produto urgentemente — está dentro do prazo?",
            "O prazo de devolução termina amanhã — precisam de processar isto hoje.",
            "Necessito de devolver com urgência antes que o prazo expire.",
        ],
        "formal": [
            "Solicito formalmente a devolução do produto, ao abrigo da garantia legal de conformidade.",
            "Venho requerer a devolução do artigo adquirido, por não estar em conformidade com o descrito.",
            "Requeiro a activação do processo de devolução no prazo regulamentar.",
        ],
        "informal": [
            "Olá, quero devolver este produto — como faço?",
            "Olá, não gostei do artigo e quero devolvê-lo.",
            "Ok, o produto chegou errado — posso devolver?",
        ],
    },
    "order_status": {
        "calm": [
            "Gostaria de saber qual é o estado actual da minha encomenda.",
            "Podem informar-me sobre a situação da encomenda que efectuei?",
            "Gostaria de consultar o estado de entrega da minha encomenda.",
        ],
        "confused": [
            "Não estou a perceber onde está a minha encomenda — alguém me pode ajudar?",
            "Recebi um e-mail de confirmação mas não sei o que aconteceu a seguir.",
            "Não encontrei o número de rastreamento — como posso saber onde está?",
            "A aplicação mostra estados diferentes — qual é o correcto?",
        ],
        "frustrated": [
            "A minha encomenda deveria ter chegado há dias e não há qualquer actualização!",
            "Ninguém me informa sobre a encomenda — isto é um serviço péssimo.",
            "Já passaram duas semanas e ainda não sei onde está o meu pedido.",
        ],
        "urgent": [
            "Preciso urgentemente de saber se a encomenda chega hoje.",
            "É urgente — preciso da encomenda para amanhã cedo.",
            "Necessito confirmar o estado de entrega com urgência.",
        ],
        "formal": [
            "Solicito informação sobre o estado actual da encomenda efectuada.",
            "Venho solicitar a confirmação do estado de processamento da minha encomenda.",
            "Requeiro uma actualização formal sobre o ponto de situação da entrega.",
        ],
        "informal": [
            "Olá, onde está a minha encomenda?",
            "Olá, já fiz o pedido há uns dias — quando chega?",
            "Ok, queria saber quando chega a minha encomenda.",
        ],
    },
    "delivery_delay": {
        "calm": [
            "A minha encomenda ainda não chegou — podem verificar o que se passa?",
            "O prazo de entrega já passou — podem ajudar-me a perceber a situação?",
            "Gostaria de perceber o motivo do atraso na entrega, por favor.",
        ],
        "confused": [
            "O tracking mostra 'em trânsito' há vários dias — é normal?",
            "Não percebo porque é que a encomenda está atrasada.",
            "O prazo indicado já passou mas não recebi nenhuma comunicação.",
        ],
        "frustrated": [
            "O equipamento que encomendei devia ter chegado esta semana e ainda nada!",
            "Já estou à espera há demasiado tempo — este atraso é inadmissível.",
            "Ninguém me avisou do atraso e eu precisava urgentemente do produto.",
        ],
        "urgent": [
            "Preciso da encomenda com urgência — o atraso está a causar problemas sérios.",
            "É urgente que me informem quando chegará — tenho um compromisso amanhã.",
            "O atraso na entrega está a prejudicar o meu trabalho — precisam de resolver já.",
        ],
        "formal": [
            "Verifico que a entrega não foi efectuada no prazo contratualmente acordado.",
            "Solicito esclarecimentos formais sobre o atraso na entrega da encomenda.",
            "Venho exigir uma justificação para o incumprimento do prazo de entrega.",
        ],
        "informal": [
            "Olá, a encomenda ainda não chegou — o que se passa?",
            "Olá, deveria ter recebido ontem mas ainda nada.",
            "Tá atrasado — quando chega mesmo?",
        ],
    },
    "damaged_item": {
        "calm": [
            "Recebi um produto danificado e gostaria de saber como proceder.",
            "O artigo chegou com danos — podem ajudar-me com a resolução?",
            "A embalagem estava em mau estado e o produto veio danificado.",
        ],
        "confused": [
            "Não sei se devo fotografar o dano antes de contactar o apoio.",
            "O produto chegou partido — não sei se devo devolver ou pedir substituição.",
            "Tenho dúvidas sobre como reportar o artigo danificado.",
        ],
        "frustrated": [
            "A embalagem estava completamente destruída e o produto está inutilizável!",
            "Paguei muito dinheiro por este produto e chegou todo partido — vergonha!",
            "Já é a segunda vez que recebo um artigo danificado. É inaceitável!",
        ],
        "urgent": [
            "Preciso urgentemente de uma substituição — o produto danificado era essencial.",
            "O artigo danificado afecta o meu trabalho — preciso de solução imediata.",
            "Necessito de substituição urgente do produto danificado.",
        ],
        "formal": [
            "Venho comunicar que o produto recebido apresenta danos visíveis não imputáveis ao transporte.",
            "Solicito a substituição do produto danificado ao abrigo da garantia de conformidade.",
            "Requeiro a resolução formal da situação relativa ao artigo recebido com defeito.",
        ],
        "informal": [
            "Olá, o produto chegou partido — o que faço?",
            "Olá, recebi o artigo todo danificado.",
            "Ok, chegou partido mesmo — podem trocar?",
        ],
    },
    "billing_question": {
        "calm": [
            "Gostaria de esclarecer uma dúvida sobre o valor cobrado na última fatura.",
            "Podem explicar-me a composição da fatura deste mês?",
            "Tenho uma questão sobre a fatura — seria possível clarificá-la?",
        ],
        "confused": [
            "Não percebo um item na fatura — podem explicar o que representa?",
            "O montante cobrado não corresponde ao que esperava — como é calculado?",
            "Há um valor na fatura que não reconheço — o que é?",
        ],
        "frustrated": [
            "O montante debitado não corresponde ao que foi acordado — exijo explicações!",
            "Já é a terceira fatura com erros — isto é inaceitável!",
            "Continuam a cobrar valores incorrectos e ninguém resolve.",
        ],
        "urgent": [
            "Preciso de esclarecer urgentemente a cobrança — o débito automático é amanhã.",
            "É urgente verificar a fatura — tenho de pagar hoje.",
            "Necessito de confirmação urgente sobre o valor a pagar.",
        ],
        "formal": [
            "Venho solicitar esclarecimentos formais sobre os valores constantes da fatura.",
            "Solicito a rectificação da fatura referente ao período indicado.",
            "Requeiro informação detalhada sobre a composição da facturação.",
        ],
        "informal": [
            "Olá, não percebo a fatura — podem ajudar?",
            "Olá, tenho uma dúvida sobre o que me cobraram.",
            "Ok, há um valor esquisito na fatura.",
        ],
    },
    "invoice_request": {
        "calm": [
            "Gostaria de solicitar a fatura referente à compra efectuada.",
            "Podem enviar-me a fatura do serviço contratado?",
            "Necessito da fatura para efeitos de contabilidade.",
        ],
        "confused": [
            "Não recebi a fatura por e-mail — onde a posso encontrar?",
            "Não sei como solicitar a segunda via da fatura.",
            "Não estou a perceber onde estão as minhas faturas no portal.",
        ],
        "frustrated": [
            "Já pedi a fatura várias vezes e nunca a recebo — é impossível!",
            "Preciso da fatura há semanas e ninguém me envia — inaceitável.",
            "Sem fatura não consigo processar o reembolso fiscal — resolvam isto.",
        ],
        "urgent": [
            "Preciso da fatura urgentemente para entrega até ao fim do dia.",
            "É urgente — o prazo fiscal termina hoje e ainda não tenho a fatura.",
            "Necessito da fatura com carácter de urgência.",
        ],
        "formal": [
            "Venho solicitar a emissão da fatura referente ao serviço prestado.",
            "Requeiro a segunda via da fatura para efeitos de declaração fiscal.",
            "Solicito formalmente o envio da factura correspondente à encomenda.",
        ],
        "informal": [
            "Olá, podem mandar-me a fatura?",
            "Olá, preciso da fatura para a contabilidade.",
            "Ok, onde está a fatura do mês passado?",
        ],
    },
    "cancel_subscription": {
        "calm": [
            "Gostaria de cancelar a minha subscrição — podem indicar-me o processo?",
            "Desejo cancelar o plano actual — como devo proceder?",
            "Quero terminar a subscrição — podem ajudar-me?",
        ],
        "confused": [
            "Não estou a perceber como cancelar a subscrição na aplicação.",
            "Tentei cancelar mas continua a cobrar — o cancelamento foi efectuado?",
            "Não sei se o cancelamento afecta o serviço imediatamente.",
        ],
        "frustrated": [
            "Já tentei cancelar três vezes e o sistema não deixa — isto é ridículo!",
            "Continuam a cobrar depois de eu ter cancelado — exijo resolução.",
            "O cancelamento devia ser simples mas puseram obstáculos a tudo.",
        ],
        "urgent": [
            "Preciso de cancelar com urgência antes da próxima cobrança.",
            "O débito é amanhã — cancelem a subscrição hoje, por favor.",
            "Necessito de cancelamento imediato para evitar nova cobrança.",
        ],
        "formal": [
            "Venho formalizar o cancelamento da subscrição activa na minha conta.",
            "Solicito o término imediato do contrato de subscrição.",
            "Requeiro o cancelamento do plano subscrito, com efeitos imediatos.",
        ],
        "informal": [
            "Olá, quero cancelar a subscrição — como faço?",
            "Olá, não quero continuar — como cancelo?",
            "Ok, quero sair do plano.",
        ],
    },
    "change_plan": {
        "calm": [
            "Gostaria de mudar para um plano diferente — quais são as opções?",
            "Podem informar-me sobre como alterar o meu plano actual?",
            "Tenho interesse em fazer upgrade do plano — como proceder?",
        ],
        "confused": [
            "Não sei qual é o plano mais adequado para as minhas necessidades.",
            "Podem explicar as diferenças entre os planos disponíveis?",
            "Não entendo bem o que inclui cada plano — podem ajudar?",
        ],
        "frustrated": [
            "Já tentei mudar o plano mas o sistema não deixa — é uma confusão.",
            "Cada vez que peço a mudança de plano há um problema diferente.",
            "A mudança de plano deveria ser simples mas está a ser um pesadelo.",
        ],
        "urgent": [
            "Preciso de mudar de plano urgentemente — o actual não cobre as minhas necessidades.",
            "É urgente fazer o upgrade antes do fim do ciclo de facturação.",
            "Necessito da mudança de plano hoje para não perder acesso.",
        ],
        "formal": [
            "Solicito a alteração do plano actual para o plano superior disponível.",
            "Venho requerer a modificação do plano de serviço subscrito.",
            "Requeiro a transição para um plano com as funcionalidades adequadas às minhas necessidades.",
        ],
        "informal": [
            "Olá, quero mudar de plano — como faço?",
            "Olá, quero fazer upgrade do plano.",
            "Ok, preciso de um plano maior.",
        ],
    },
    "technical_issue": {
        "calm": [
            "Estou a ter um problema técnico com o serviço — podem ajudar-me?",
            "O serviço apresenta um comportamento inesperado — podem verificar?",
            "Gostaria de reportar uma anomalia técnica que encontrei.",
        ],
        "confused": [
            "Não sei se o problema é do meu lado ou do sistema — podem verificar?",
            "Aparece uma mensagem de erro mas não percebo o que significa.",
            "O serviço às vezes funciona e às vezes não — não sei o que se passa.",
        ],
        "frustrated": [
            "O serviço apresenta erros e não consigo completar as minhas tarefas — inaceitável!",
            "Já reportei este problema há uma semana e continua sem resolução.",
            "A aplicação está constantemente a falhar e perco trabalho por isso.",
        ],
        "urgent": [
            "É urgente — o sistema está em baixo e está a afectar operações críticas.",
            "Preciso de resolução imediata — o problema está a impedir o trabalho.",
            "Necessito de apoio técnico urgente — o serviço está inacessível.",
        ],
        "formal": [
            "Venho reportar uma falha técnica que impede a utilização normal do serviço.",
            "Solicito a análise e resolução do problema técnico identificado.",
            "Requeiro intervenção técnica urgente para resolver a anomalia detectada.",
        ],
        "informal": [
            "Olá, o sistema está a dar erro — podem ver?",
            "Olá, a aplicação não funciona bem.",
            "Tá com bug — precisam de arranjar.",
        ],
    },
    "password_reset": {
        "calm": [
            "Não consigo repor a palavra-passe — podem ajudar-me?",
            "Gostaria de redefinir a minha palavra-passe — como procedo?",
            "Preciso de alterar a palavra-passe e não consigo fazê-lo sozinho.",
        ],
        "confused": [
            "Não estou a receber o e-mail de reposição de palavra-passe.",
            "Não sei como alterar a palavra-passe na nova versão da aplicação.",
            "Tentei repor a palavra-passe mas diz que o link expirou.",
        ],
        "frustrated": [
            "Já pedi a reposição de palavra-passe cinco vezes e nunca recebo o e-mail!",
            "O sistema não me deixa repor a palavra-passe — é completamente absurdo.",
            "Estou bloqueado da conta por causa da palavra-passe há horas — inaceitável.",
        ],
        "urgent": [
            "Preciso de repor a palavra-passe urgentemente — tenho uma reunião daqui a pouco.",
            "É urgente — estou bloqueado da conta e preciso de aceder já.",
            "Necessito de resolução imediata para a reposição de palavra-passe.",
        ],
        "formal": [
            "Solicito o reset da palavra-passe da minha conta de forma segura.",
            "Venho requerer o procedimento formal de reposição de credenciais de acesso.",
            "Requeiro assistência para a redefinição da palavra-passe associada à conta.",
        ],
        "informal": [
            "Olá, esqueci a palavra-passe — como recupero?",
            "Olá, não consigo entrar — preciso de nova palavra-passe.",
            "Ok, preciso de repor a palavra-passe.",
        ],
    },
    "account_access": {
        "calm": [
            "Estou com dificuldades em aceder à minha conta — podem ajudar?",
            "Não consigo entrar na minha conta — podem verificar a situação?",
            "Gostaria de recuperar o acesso à minha conta, por favor.",
        ],
        "confused": [
            "Não percebo porque é que não consigo entrar na conta.",
            "A minha conta parece estar bloqueada mas não sei porquê.",
            "Já introduzi as credenciais correctas mas continua a dar erro.",
        ],
        "frustrated": [
            "A minha conta foi bloqueada sem aviso prévio — é completamente inaceitável!",
            "Perdi o acesso à conta e ninguém me ajuda a recuperar — que serviço péssimo.",
            "Já tentei entrar várias vezes e continuo bloqueado — exijo resolução imediata.",
        ],
        "urgent": [
            "Preciso de aceder à conta com urgência — tenho informação crítica lá dentro.",
            "É urgente — estou sem acesso à conta e isso está a bloquear o meu trabalho.",
            "Necessito de acesso imediato à conta — a situação é crítica.",
        ],
        "formal": [
            "Solicito o restabelecimento do acesso à minha conta de forma segura.",
            "Venho requerer a desbloqueio formal da conta de utilizador.",
            "Requeiro a verificação e reactivação da minha conta.",
        ],
        "informal": [
            "Olá, não consigo entrar na conta — ajudem-me?",
            "Olá, a minha conta está bloqueada.",
            "Ok, perdi o acesso — o que faço?",
        ],
    },
    "complaint": {
        "calm": [
            "Gostaria de registar uma reclamação relativamente ao serviço prestado.",
            "Tenho uma reclamação formal a apresentar — como procedo?",
            "Quero registar a minha insatisfação de forma construtiva.",
        ],
        "confused": [
            "Não sei qual é o processo correcto para apresentar uma reclamação.",
            "Não estou certo se devo reclamar aqui ou noutro canal.",
            "Tentei submeter a reclamação mas não sei se foi registada.",
        ],
        "frustrated": [
            "Quero apresentar uma queixa formal — o serviço que recebi foi inaceitável.",
            "Estou extremamente insatisfeito e exijo uma resposta escrita à minha reclamação.",
            "Já apresentei a reclamação e não recebi qualquer resposta — vou escalar.",
        ],
        "urgent": [
            "Preciso de registar uma reclamação urgente — o problema está a agravar-se.",
            "É urgente que a reclamação seja tratada hoje.",
            "Necessito de resolução imediata para a situação alvo de reclamação.",
        ],
        "formal": [
            "Venho por este meio apresentar reclamação formal nos termos legais aplicáveis.",
            "Requeiro o registo oficial da reclamação e resposta nos prazos legais.",
            "Solicito a abertura de processo de reclamação ao abrigo dos direitos do consumidor.",
        ],
        "informal": [
            "Olá, quero reclamar — como faço?",
            "Olá, não estou nada satisfeito com o serviço.",
            "Ok, quero queixar-me formalmente.",
        ],
    },
    "escalation_request": {
        "calm": [
            "Gostaria de escalar esta situação para um responsável, por favor.",
            "Solicito que o meu caso seja encaminhado para um nível superior de apoio.",
            "Gostaria de falar com um supervisor ou responsável da equipa.",
        ],
        "confused": [
            "Não sei a quem me devo dirigir para resolver esta situação.",
            "Já contactei o apoio básico mas não resolveram — a quem escalo?",
            "Não sei qual é o processo de escalada para situações complexas.",
        ],
        "frustrated": [
            "Exijo falar com um supervisor — o apoio de primeiro nível não resolve nada!",
            "Vou escalar esta situação se não receber resposta imediata.",
            "Já esperei demasiado — quero falar com a direcção agora.",
        ],
        "urgent": [
            "É urgente escalar — o problema está a causar prejuízos.",
            "Preciso de falar com um responsável imediatamente — a situação é crítica.",
            "Necessito de escalada urgente para resolver o problema hoje.",
        ],
        "formal": [
            "Solicito formalmente a escalada deste processo para o nível hierárquico superior.",
            "Venho requerer que o presente caso seja encaminhado para decisão superior.",
            "Requeiro o envolvimento de um responsável de nível sénior nesta situação.",
        ],
        "informal": [
            "Olá, quero falar com um supervisor.",
            "Olá, preciso de escalar este problema.",
            "Ok, quero falar com o chefe — isso não está resolvido.",
        ],
    },
    "booking_change": {
        "calm": [
            "Gostaria de alterar a data da minha reserva — é possível?",
            "Necessito de modificar os detalhes da reserva efectuada.",
            "Podem ajudar-me a alterar a minha reserva para outra data?",
        ],
        "confused": [
            "Não sei se posso alterar a reserva sem custos adicionais.",
            "Tentei alterar a reserva mas não sei se a alteração foi guardada.",
            "Não percebo quais são as condições para mudar a data.",
        ],
        "frustrated": [
            "Já tentei alterar a reserva online mas o sistema não deixa — que frustração!",
            "Paguei para mudar a reserva e ninguém confirmou a alteração.",
            "Ninguém me responde sobre a alteração da reserva — é inaceitável.",
        ],
        "urgent": [
            "Preciso de alterar a reserva urgentemente — mudei de planos.",
            "É urgente modificar a data — o check-in é amanhã.",
            "Necessito da alteração da reserva confirmada hoje.",
        ],
        "formal": [
            "Solicito a alteração da reserva para a data indicada, sem penalização.",
            "Venho requerer a modificação dos dados da reserva efectuada.",
            "Requeiro a confirmação da alteração da reserva nos termos acordados.",
        ],
        "informal": [
            "Olá, precisei de mudar a reserva — como faço?",
            "Olá, quero mudar a data da reserva.",
            "Ok, mudei de planos — podem alterar a reserva?",
        ],
    },
    "booking_cancellation": {
        "calm": [
            "Gostaria de cancelar a minha reserva — quais são as condições?",
            "Quero cancelar a reserva e saber se tenho direito a reembolso.",
            "Podem ajudar-me a cancelar a reserva efectuada?",
        ],
        "confused": [
            "Não sei se o cancelamento tem custos — podem esclarecer?",
            "Tentei cancelar a reserva mas não sei se foi efectuado.",
            "Não percebo a política de cancelamento — podem explicar?",
        ],
        "frustrated": [
            "Preciso de cancelar e não me deixam — a política é injusta!",
            "Já cancelei a reserva mas ainda não recebi o reembolso — inadmissível.",
            "O cancelamento devia ser gratuito nesta fase e estão a querer cobrar.",
        ],
        "urgent": [
            "Preciso de cancelar a reserva com urgência — emergência familiar.",
            "É urgente cancelar — o check-in é amanhã e mudei de planos.",
            "Necessito do cancelamento imediato com confirmação por escrito.",
        ],
        "formal": [
            "Venho solicitar o cancelamento da reserva ao abrigo das condições contratadas.",
            "Requeiro o cancelamento formal da reserva com reembolso integral.",
            "Solicito a rescisão da reserva, com devolução do valor pago.",
        ],
        "informal": [
            "Olá, quero cancelar a reserva — pode ser?",
            "Olá, preciso de cancelar — como faço?",
            "Ok, precisei de cancelar a reserva.",
        ],
    },
    "payment_failure": {
        "calm": [
            "Tentei efectuar o pagamento e não foi processado — podem ajudar?",
            "O pagamento falhou e não sei qual foi o motivo.",
            "Gostaria de perceber porque é que o meu pagamento não foi aceite.",
        ],
        "confused": [
            "O pagamento foi recusado mas tenho saldo suficiente — não percebo.",
            "Tentei várias vezes pagar e continua a dar erro — o que está errado?",
            "Não sei se o problema é do meu cartão ou do vosso sistema.",
        ],
        "frustrated": [
            "Tentei efectuar o pagamento várias vezes e continua a falhar — ridículo!",
            "O sistema rejeita o pagamento sem explicação — exijo que resolvam.",
            "Já perdi muito tempo a tentar pagar e nada funciona.",
        ],
        "urgent": [
            "Preciso de resolver a falha de pagamento urgentemente — o prazo é hoje.",
            "É urgente processar o pagamento — o serviço vai ser suspenso.",
            "Necessito de resolução imediata para a falha de pagamento.",
        ],
        "formal": [
            "Venho comunicar a falha no processamento do pagamento e solicitar assistência.",
            "Solicito análise da falha de pagamento e indicação de método alternativo.",
            "Requeiro esclarecimento sobre o motivo da recusa do pagamento efectuado.",
        ],
        "informal": [
            "Olá, o pagamento não passou — o que faço?",
            "Olá, tentei pagar e deu erro.",
            "Ok, o pagamento falhou — como resolvo?",
        ],
    },
    "duplicate_charge": {
        "calm": [
            "Verifiquei que fui cobrado duas vezes pelo mesmo serviço — podem verificar?",
            "Parece haver uma cobrança duplicada na minha conta — podem confirmar?",
            "Gostaria de reportar uma possível cobrança duplicada.",
        ],
        "confused": [
            "Vejo dois débitos iguais na conta mas não sei se é erro ou intencional.",
            "Não percebo porque é que aparece a mesma cobrança duas vezes.",
            "Fui cobrado duas vezes — é um erro do sistema?",
        ],
        "frustrated": [
            "Foi cobrado o mesmo valor duas vezes — exijo o reembolso imediato!",
            "Já é a segunda vez que me cobram em duplicado — isto é inaceitável.",
            "Fui duplamente debitado sem autorização — exijo explicações e devolução.",
        ],
        "urgent": [
            "É urgente anular a cobrança duplicada — o valor é significativo.",
            "Preciso de resolução urgente — a cobrança duplicada afecta o meu saldo.",
            "Necessito do reembolso da cobrança duplicada com urgência.",
        ],
        "formal": [
            "Venho comunicar a existência de uma cobrança duplicada não autorizada.",
            "Solicito a análise e rectificação da duplicação de débito verificada.",
            "Requeiro o reembolso imediato do valor cobrado indevidamente em duplicado.",
        ],
        "informal": [
            "Olá, cobrararam-me duas vezes — podem ver?",
            "Olá, há uma cobrança dupla na conta.",
            "Ok, fui cobrado duas vezes pelo mesmo.",
        ],
    },
}

# Backward-compatibility alias: flat union of all tone pools per intent.
# Existing code that uses INTENT_MESSAGES[intent] continues to work unchanged.
INTENT_MESSAGES: dict[str, list[str]] = {
    intent: [msg for pool in tones.values() for msg in pool]
    for intent, tones in TONE_MESSAGES.items()
}
