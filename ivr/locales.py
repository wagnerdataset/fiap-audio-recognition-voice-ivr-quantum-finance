from .config import COMPANY

PT = {
    "GREETING": f"Bem-vindo à {COMPANY}!",
    "OPTIONS": ("Para prosseguir, diga uma das opções: "
                "(1) Consulta ao saldo da conta, "
                "(2) Simulação de compra internacional, "
                "(3) Falar com um atendente, "
                "(4) Sair do atendimento."),
    "CONFIRM": {
        1: "Você escolheu consulta ao saldo da conta.",
        2: "Você escolheu simulação de compra internacional.",
        3: "Você escolheu falar com um atendente.",
        4: "Você escolheu sair do atendimento."
    },
    "BYE": "Encerrando o atendimento. Obrigado!",
    "UNRECOGNIZED": "Desculpe, não consegui entender sua escolha. Vamos tentar novamente.",
    "HINT": "Após o sinal, diga sua opção.",
    "KEYWORDS": {
        1: {"saldo", "conta", "consulta", "ver saldo", "meu saldo"},
        2: {"simulação", "simular", "internacional", "compra internacional", "câmbio"},
        3: {"atendente", "falar", "humano", "pessoa", "suporte"},
        4: {"sair", "encerrar", "finalizar", "terminar", "fechar"}
    },
    "STT_LANG": "pt-BR",
    "TTS_LANG": "pt-br",

    # Submenu Saldo
    "BALANCE_INFO": "No momento, você não tem saldo disponível.",
    "BALANCE_FOLLOWUP": "Você quer ouvir novamente, voltar para o menu anterior, ou sair do atendimento?",
    "BALANCE_REPEAT_KWS": {"ouvir novamente","ouvir de novo","repetir","repete","de novo"},
    "BALANCE_BACK_KWS": {"voltar","retornar","menu anterior","voltar ao menu","retorno"},

    # Submenu Simulação de compra internacional
    "SIM_INFO": "No momento, não temos o produto disponível para compra internacional.",
    "SIM_FOLLOWUP": "Você quer ouvir novamente, voltar para o menu anterior, ou sair do atendimento?",
    "SIM_REPEAT_KWS": {"ouvir novamente","ouvir de novo","repetir","repete","de novo"},
    "SIM_BACK_KWS": {"voltar","retornar","menu anterior","voltar ao menu","retorno"},

    # Submenu Falar com atendente (fora do horário)
    "AGENT_INFO": ("Não estamos atendendo neste momento. "
                   "Retorne dentro do horário comercial de 8 às 18 horas, de segunda a sexta-feira."),
    "AGENT_FOLLOWUP": "Você quer ouvir novamente, voltar para o menu anterior, ou sair do atendimento?",
    "AGENT_REPEAT_KWS": {"ouvir novamente","ouvir de novo","repetir","repete","de novo"},
    "AGENT_BACK_KWS": {"voltar","retornar","menu anterior","voltar ao menu","retorno"},

    # Palavras de saída comuns (submenus)
    "EXIT_KWS": {"sair","encerrar","finalizar","terminar","fechar","encerrar atendimento","quero sair"},
}

EN = {
    "GREETING": f"Welcome to {COMPANY}!",
    "OPTIONS": ("Please say one of the following options: "
                "(1) Check account balance, "
                "(2) International purchase simulation, "
                "(3) Talk to an agent, "
                "(4) Exit."),
    "CONFIRM": {
        1: "You chose account balance inquiry.",
        2: "You chose international purchase simulation.",
        3: "You chose to talk to an agent.",
        4: "You chose to exit."
    },
    "BYE": "Exiting the service. Thank you!",
    "UNRECOGNIZED": "Sorry, I could not understand your choice. Let's try again.",
    "HINT": "After the beep, say your option.",
    "KEYWORDS": {
        1: {"balance", "account", "check"},
        2: {"simulation", "simulate", "international", "purchase"},
        3: {"agent", "talk", "representative", "support"},
        4: {"exit", "quit", "leave", "goodbye"}
    },
    "STT_LANG": "en-US",
    "TTS_LANG": "en",

    # Balance submenu
    "BALANCE_INFO": "You currently have no available balance.",
    "BALANCE_FOLLOWUP": "Would you like to hear it again, go back to the previous menu, or exit?",
    "BALANCE_REPEAT_KWS": {"hear again","repeat","again","once more"},
    "BALANCE_BACK_KWS": {"go back","back","previous menu","return","back to menu"},

    # International purchase simulation submenu
    "SIM_INFO": "The product is currently not available for international purchase.",
    "SIM_FOLLOWUP": "Would you like to hear it again, go back to the previous menu, or exit?",
    "SIM_REPEAT_KWS": {"hear again","repeat","again","once more"},
    "SIM_BACK_KWS": {"go back","back","previous menu","return","back to menu"},

    # Talk to an agent submenu (out of hours)
    "AGENT_INFO": ("We are not attending right now. "
                   "Please call back during business hours from 8 AM to 6 PM, Monday through Friday."),
    "AGENT_FOLLOWUP": "Would you like to hear it again, go back to the previous menu, or exit?",
    "AGENT_REPEAT_KWS": {"hear again","repeat","again","once more"},
    "AGENT_BACK_KWS": {"go back","back","previous menu","return","back to menu"},

    # Exit words (submenus)
    "EXIT_KWS": {"exit","quit","leave","goodbye","finish","end","i want to exit"},
}
