# QuantumFinance — Atendimento por Voz (TTS/STT)

Este projeto implementa um **IVR simplificado** (menu de atendimento por voz) para a QuantumFinance:

- **Seleção inicial de idioma**: ao iniciar, o sistema pergunta:
  - “Você deseja atendimento em português ou inglês?”
  - “Which language do you prefer, Portuguese or English?”
- **TTS (Text-to-Speech)** via [gTTS](https://pypi.org/project/gTTS/) → gera arquivos `.mp3`.
- **Áudio player** via [pygame](https://pypi.org/project/pygame/).
- **STT (Speech-to-Text)** via [SpeechRecognition](https://pypi.org/project/SpeechRecognition/):  
  - offline com [Vosk](https://alphacephei.com/vosk/models) (se configurado),  
  - online via Google Web Speech (default).
- **Submenus dedicados** para cada opção.  
- **Encerramento** pode ser feito no menu principal (opção 4) ou dentro de qualquer submenu.

---

## ✅ Funcionalidades
### Menu Principal
1. **Consulta ao saldo da conta**  
   - Abre submenu:  
     - Informa que **não há saldo disponível**.  
     - Pergunta se deseja **ouvir novamente**, **voltar ao menu principal**, ou **sair do atendimento**.
2. **Simulação de compra internacional**  
   - Abre submenu:  
     - Informa que o **produto não está disponível** para compra internacional.  
     - Pergunta se deseja **ouvir novamente**, **voltar ao menu principal**, ou **sair do atendimento**.
3. **Falar com um atendente**  
   - Abre submenu:  
     - Informa que **não há atendimento neste momento**, apenas em horário comercial (8h–18h, seg–sex).  
     - Pergunta se deseja **ouvir novamente**, **voltar ao menu principal**, ou **sair do atendimento**.
4. **Sair do atendimento**  
   - Toca a mensagem de encerramento e finaliza o programa.

### Seleção de idioma (início)
- Pergunta (PT/EN), toca um **beep**, e ouve a resposta.
- Se detectar “português” → PT-BR. Se “english/inglês” → EN-US.
- Se não entender → default PT-BR.

---

## 🔧 Tecnologias utilizadas
- **gTTS** → geração de fala (online, precisa de internet).  
- **pygame** → player de MP3.  
- **SpeechRecognition** → STT.  
- **sounddevice + wavio** → captura de áudio (sem PyAudio).  
- **numpy** → beep sonoro.  
- **vosk** (opcional) → STT offline.  

---

## 📁 Estrutura de diretórios

ivr-system/
├── main.py          # Arquivo principal de execução
├── .gitignore
├── requirements.txt
├── README.md
├── ivr/
│   ├── __init__.py
│   ├── config.py    # flags, paths e logger
│   ├── audio.py     # Configurações de áudio e TTS
│   ├── stt.py       # Reconhecimento de fala (STT)
│   ├── locales.py   # Textos e palavras-chave em PT/EN
│   ├── match.py     # Utilitários de matching por palavra-chave
│   └── menus.py     # Seleção de idioma, submenus e loop principal
└── audio/
    ├── pt/          # Arquivos de áudio em português
    └── en/          # Arquivos de áudio em inglês

---

## 📦 Instalação
Requisitos: **Python 3.9+**

Clone o repositório e instale as dependências:
```bash
pip install -r requirements.txt

---

## ▶️ Execução
```bash
python main.py
```

### Fluxo da primeira execução
1. Pergunta o idioma (PT/EN).
2. Gera os arquivos MP3 em `audio/pt` ou `audio/en`.
3. Entra no menu principal no idioma escolhido.

---

## 🔧 Modos e variáveis (opcionais)

### Modo texto (sem microfone)
Permite digitar as respostas no console (útil para testes):

**Windows (PowerShell):**
```powershell
setx IVR_MODE "text"
```

**Linux/macOS (bash/zsh):**
```bash
export IVR_MODE=text
```

### Logs de depuração
**Windows (PowerShell):**
```powershell
setx IVR_DEBUG "1"
```

**Linux/macOS (bash/zsh):**
```bash
export IVR_DEBUG=1
```

### STT offline com Vosk (opcional)
1. Instale:
```bash
pip install vosk
```

2. Baixe um modelo em: [Vosk Models](https://alphacephei.com/vosk/models)
   - Exemplo: `vosk-model-small-pt-0.3` ou `vosk-model-small-en-us-0.15`

3. Configure a variável `VOSK_MODEL` para a pasta do modelo descompactado:

**Windows (PowerShell):**
```powershell
setx VOSK_MODEL "C:\modelos\vosk-model-small-pt-0.3"
```

**Linux/macOS (bash/zsh):**
```bash
export VOSK_MODEL=/home/usuario/modelos/vosk-model-small-pt-0.3
```

📌 Se `VOSK_MODEL` não estiver configurada, o sistema usa **Google Web Speech** (online) automaticamente.

---

## 🗣️ Exemplos de frases

### Português
- "Quero consultar o saldo."
- "Simulação internacional."
- "Quero falar com um atendente."
- "Quero sair."

### Inglês
- "Check my balance."
- "International purchase simulation."
- "Talk to an agent."
- "I want to exit."

⚠️ O reconhecimento por palavras-chave **não aceita apenas números** (1/2/3/4).

---

## 🧩 Customização rápida
- **Adicionar palavras-chave**: edite `ivr/locales.py` nos conjuntos `KEYWORDS`, `*_REPEAT_KWS`, `*_BACK_KWS`, `EXIT_KWS`.
- **Trocar textos/vozes**: ajuste os textos em `ivr/locales.py`. Os MP3 são regerados automaticamente.
- **Mudar TTS/STT**: altere implementações em `ivr/audio.py` (TTS/player) e `ivr/stt.py` (captura/reconhecimento).

---

## 🛠️ Solução de problemas

### Sem áudio de saída
- Verifique o volume e o dispositivo padrão do sistema.
- Alguns ambientes exigem fechar outros apps que “seguram” o áudio.

### Microfone não funciona / Permissão negada
- **Windows**: Configurações → Privacidade → Microfone → permitir para apps de desktop.
- Teste o **Modo texto** para isolar se é problema de microfone.

### Estouro/erro de sample rate
- Ajuste a taxa em `stt.py` (parâmetro `fs` em `record_mono` e no `Recognizer`).

### Pygame não inicializa o mixer
- Feche apps que utilizam o dispositivo de áudio.
- Em VMs/WSL, use o host (nativo) ou configure o driver de áudio.

---

## 🎥 Roteiro para o vídeo de entrega
1. Visão geral do projeto e estrutura de diretórios.
2. Execução: seleção de idioma PT/EN.
3. Demonstração de cada submenu:
   - ouvir novamente
   - voltar ao menu
   - sair (encerrando por dentro do submenu)
4. Encerramento pelo menu principal (opção 4).
