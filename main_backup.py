import os
import json
import sys
import wave
import tempfile
import traceback

import numpy as np
import sounddevice as sd
import wavio
import speech_recognition as sr
from gtts import gTTS
import pygame

# =========================
# Flags e constantes
# =========================
COMPANY = "QuantumFinance"
MODE = os.environ.get("IVR_MODE", "voice").lower()  # "voice" | "text"
DEBUG = os.environ.get("IVR_DEBUG", "0") == "1"
BASE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

def log(msg: str):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# =========================
# Dados por idioma
# =========================
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
    "SIM_INFO": "No momento, não temos o produto disponível para compra internacional. Fale com um atendente.",
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
    "SIM_INFO": "The product is currently not available for international purchase. Please speak to a representative.",
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

# =========================
# Player MP3 (pygame)
# =========================
_PYGAME_READY = False
def ensure_pygame():
    global _PYGAME_READY
    if not _PYGAME_READY:
        pygame.mixer.init()  # dispositivo padrão
        _PYGAME_READY = True

def play_mp3(path_mp3: str):
    if not os.path.exists(path_mp3):
        print(f"[WARN] Áudio não encontrado: {path_mp3}")
        return
    try:
        ensure_pygame()
        log(f"Tocando {path_mp3}")
        pygame.mixer.music.load(path_mp3)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(50)
    except Exception as e:
        print(f"[WARN] Falha ao tocar MP3 com pygame: {e}")
        if DEBUG:
            traceback.print_exc()

def beep(duration=0.2, freq=800):
    try:
        fs = 44100
        t = np.linspace(0, duration, int(fs * duration), False)
        tone = np.sin(freq * t * 2 * np.pi) * 0.2
        sd.play(tone.astype(np.float32), fs)
        sd.wait()
    except Exception as e:
        print(f"[WARN] Beep falhou: {e}")

# =========================
# TTS (gTTS → MP3)
# =========================
def tts_to_mp3(text: str, path_mp3: str, lang_code: str):
    # regrava sempre para garantir atualização
    try:
        if os.path.exists(path_mp3):
            os.remove(path_mp3)
    except Exception:
        pass
    log(f"gTTS [{lang_code}] -> {path_mp3}")
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(path_mp3)

# =========================
# Captura de áudio
# =========================
def record_mono(seconds=5, fs=16000):
    log(f"Gravando {seconds}s @ {fs}Hz ...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    return audio, fs

# =========================
# STT (Vosk offline se disponível; senão Google)
# =========================
def recognize_speech(stt_lang="pt-BR", phrase_time_limit=5):
    if MODE == "text":
        return input("(digite sua resposta)\n> ").strip()

    # 1) Vosk offline se VOSK_MODEL estiver setado
    model_path = os.environ.get("VOSK_MODEL")
    if model_path:
        try:
            from vosk import Model, KaldiRecognizer  # type: ignore
            audio, fs = record_mono(seconds=phrase_time_limit, fs=16000)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                wavio.write(tf.name, audio, fs, sampwidth=2)
                tmp_path = tf.name

            wf = wave.open(tmp_path, "rb")
            rec = KaldiRecognizer(Model(model_path), wf.getframerate())
            rec.SetWords(False)

            parts = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    parts.append(res.get("text", ""))
            res = json.loads(rec.FinalResult())
            parts.append(res.get("text", ""))
            wf.close()
            os.unlink(tmp_path)
            text = " ".join(p for p in parts if p).strip()
            return text or None
        except Exception as e:
            print(f"[WARN] Vosk indisponível: {e}. Usando Google...")

    # 2) Google Web Speech (online)
    r = sr.Recognizer()
    try:
        audio, fs = record_mono(seconds=phrase_time_limit, fs=16000)
        wav_bytes = audio.tobytes()
        audio_data = sr.AudioData(wav_bytes, fs, 2)  # 16-bit
        return r.recognize_google(audio_data, language=stt_lang)
    except Exception as e2:
        print(f"[ERROR] STT Google falhou: {e2}")
        if DEBUG:
            traceback.print_exc()
        return None

# =========================
# Matching utilitários
# =========================
def identify_option(transcript: str, keywords: dict):
    if not transcript:
        return None
    txt = transcript.casefold()

    numeric_words = {
        "um","uma","dois","duas","três","tres","quatro","1","2","3","4","1.","2.","3.","4.",
        "one","two","three","four"
    }
    tokens = {t.strip(".,;:!?") for t in txt.split() if t.strip()}
    if tokens and tokens.issubset(numeric_words):
        return None  # apenas números => rejeita

    for opt, kws in keywords.items():
        if any(kw in txt for kw in kws):
            return opt
    return None

def match_keywords(transcript: str, kws: set):
    if not transcript:
        return False
    txt = transcript.casefold()
    return any(kw in txt for kw in kws)

# =========================
# Seleção inicial de idioma (voz)
# =========================
def select_language():
    ask_pt = os.path.join(BASE_AUDIO_DIR, "ask_lang_pt.mp3")
    ask_en = os.path.join(BASE_AUDIO_DIR, "ask_lang_en.mp3")
    os.makedirs(BASE_AUDIO_DIR, exist_ok=True)

    tts_to_mp3("Você deseja atendimento em português ou inglês?", ask_pt, lang_code="pt-br")
    tts_to_mp3("Which language do you prefer, Portuguese or English?", ask_en, lang_code="en")

    play_mp3(ask_pt)
    play_mp3(ask_en)
    beep(0.15, 900)

    # primeiro tenta em PT; se vazio, tenta em EN
    answer = recognize_speech("pt-BR", 4) or recognize_speech("en-US", 4) or ""
    ans_low = answer.lower()

    # heurística simples
    if any(w in ans_low for w in ["english", "inglês", "ingles", "en"]):
        return EN, "en"
    return PT, "pt"

# =========================
# Geração de assets (por idioma)
# =========================
def ensure_assets(lang_data: dict, audio_dir: str):
    assets = {
        "welcome.mp3": lang_data["GREETING"],
        "options.mp3": lang_data["OPTIONS"],
        "hint.mp3": lang_data["HINT"],
        "unk.mp3": lang_data["UNRECOGNIZED"],
        # Bye DIFERENTE da confirmação 4
        "bye.mp3": lang_data["BYE"],
        "confirm_1.mp3": lang_data["CONFIRM"][1],
        "confirm_2.mp3": lang_data["CONFIRM"][2],
        "confirm_3.mp3": lang_data["CONFIRM"][3],
        "confirm_4.mp3": lang_data["CONFIRM"][4],

        # Submenu Saldo
        "balance_info.mp3": lang_data["BALANCE_INFO"],
        "balance_followup.mp3": lang_data["BALANCE_FOLLOWUP"],

        # Submenu Simulação internacional
        "sim_info.mp3": lang_data["SIM_INFO"],
        "sim_followup.mp3": lang_data["SIM_FOLLOWUP"],

        # Submenu Atendente (fora do horário)
        "agent_info.mp3": lang_data["AGENT_INFO"],
        "agent_followup.mp3": lang_data["AGENT_FOLLOWUP"],
    }
    tts_lang = lang_data["TTS_LANG"]
    for fname, text in assets.items():
        tts_to_mp3(text, os.path.join(audio_dir, fname), lang_code=tts_lang)

# =========================
# Submenus (retornam "back" ou "exit")
# =========================
def balance_submenu(lang_data: dict, audio_dir: str, stt_lang: str):
    info_path = os.path.join(audio_dir, "balance_info.mp3")
    follow_path = os.path.join(audio_dir, "balance_followup.mp3")
    unk_path = os.path.join(audio_dir, "unk.mp3")
    bye_path = os.path.join(audio_dir, "bye.mp3")

    repeat_kws = lang_data["BALANCE_REPEAT_KWS"]
    back_kws = lang_data["BALANCE_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(info_path)
        play_mp3(follow_path)
        beep(0.15, 900)

        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Saldo] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue  # repete a informação

        if match_keywords(ans or "", back_kws):
            return "back"  # volta ao menu principal

        if match_keywords(ans or "", exit_kws):
            play_mp3(bye_path)
            print("Atendimento encerrado. Obrigada! / Exiting. Goodbye!")
            return "exit"

        play_mp3(unk_path)

def simulation_submenu(lang_data: dict, audio_dir: str, stt_lang: str):
    info_path = os.path.join(audio_dir, "sim_info.mp3")
    follow_path = os.path.join(audio_dir, "sim_followup.mp3")
    unk_path = os.path.join(audio_dir, "unk.mp3")
    bye_path = os.path.join(audio_dir, "bye.mp3")

    repeat_kws = lang_data["SIM_REPEAT_KWS"]
    back_kws = lang_data["SIM_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(info_path)
        play_mp3(follow_path)
        beep(0.15, 900)

        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Simulação] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue

        if match_keywords(ans or "", back_kws):
            return "back"

        if match_keywords(ans or "", exit_kws):
            play_mp3(bye_path)
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            return "exit"

        play_mp3(unk_path)

def agent_submenu(lang_data: dict, audio_dir: str, stt_lang: str):
    info_path = os.path.join(audio_dir, "agent_info.mp3")
    follow_path = os.path.join(audio_dir, "agent_followup.mp3")
    unk_path = os.path.join(audio_dir, "unk.mp3")
    bye_path = os.path.join(audio_dir, "bye.mp3")

    repeat_kws = lang_data["AGENT_REPEAT_KWS"]
    back_kws = lang_data["AGENT_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(info_path)
        play_mp3(follow_path)
        beep(0.15, 900)

        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Atendente] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue  # repete a informação

        if match_keywords(ans or "", back_kws):
            return "back"  # volta ao menu principal

        if match_keywords(ans or "", exit_kws):
            play_mp3(bye_path)
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            return "exit"

        play_mp3(unk_path)

# =========================
# Main
# =========================
def main():
    print(f"== {COMPANY} — Atendimento por Voz ==")
    print(f"MODE={MODE} | DEBUG={DEBUG}")

    # (Opcional: diagnosticar dispositivos)
    try:
        devs = sd.query_devices()
        log(f"Dispositivos: {len(devs)} | Default IN/OUT: {sd.default.device}")
    except Exception as e:
        print("[WARN] Não consegui listar dispositivos de áudio:", e)

    # 1) Seleção inicial de idioma
    lang_data, code = select_language()
    stt_lang = lang_data["STT_LANG"]
    audio_dir = os.path.join(BASE_AUDIO_DIR, code)
    os.makedirs(audio_dir, exist_ok=True)

    # 2) Gera assets e inicia
    ensure_assets(lang_data, audio_dir)
    play_mp3(os.path.join(audio_dir, "welcome.mp3"))
    play_mp3(os.path.join(audio_dir, "options.mp3"))

    # 3) Loop principal
    while True:
        play_mp3(os.path.join(audio_dir, "hint.mp3"))
        beep(0.15, 900)

        transcript = recognize_speech(stt_lang, phrase_time_limit=5)
        print(f"[STT] Você disse / You said: {transcript!r}")

        opt = identify_option(transcript or "", lang_data["KEYWORDS"])
        if opt is None:
            play_mp3(os.path.join(audio_dir, "unk.mp3"))
            play_mp3(os.path.join(audio_dir, "options.mp3"))
            continue

        # Confirma a opção escolhida
        play_mp3(os.path.join(audio_dir, f"confirm_{opt}.mp3"))

        # Roteamento por opção
        if opt == 1:
            res = balance_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(os.path.join(audio_dir, "options.mp3"))
            continue

        if opt == 2:
            res = simulation_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(os.path.join(audio_dir, "options.mp3"))
            continue

        if opt == 3:
            res = agent_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(os.path.join(audio_dir, "options.mp3"))
            continue

        if opt == 4:
            play_mp3(os.path.join(audio_dir, "bye.mp3"))
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            break

        # fallback — volta ao menu
        play_mp3(os.path.join(audio_dir, "options.mp3"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
    except Exception as e:
        print("[FATAL] Erro inesperado:", e)
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)
