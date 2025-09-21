from pathlib import Path

from .audio import tts_to_mp3, play_mp3, beep, ensure_assets, lang_prompt_files
from .stt import recognize_speech
from .match import match_keywords
from .locales import PT, EN

def select_language():
    ask_pt, ask_en = lang_prompt_files()
    # Gera prompts bilíngues
    tts_to_mp3("Você deseja atendimento em português ou inglês?", str(ask_pt), lang_code="pt-br")
    tts_to_mp3("Which language do you prefer, Portuguese or English?", str(ask_en), lang_code="en")

    # Toca PT + EN, depois bip e escuta
    play_mp3(str(ask_pt))
    play_mp3(str(ask_en))
    beep(0.15, 900)

    # tenta reconhecer em PT, depois EN
    answer = recognize_speech("pt-BR", 4) or recognize_speech("en-US", 4) or ""
    ans_low = (answer or "").lower()

    # heurística
    if any(w in ans_low for w in ["english", "inglês", "ingles", "en"]):
        return EN, "en"
    return PT, "pt"

def balance_submenu(lang_data: dict, audio_dir: Path, stt_lang: str):
    info_path = audio_dir / "balance_info.mp3"
    follow_path = audio_dir / "balance_followup.mp3"
    unk_path = audio_dir / "unk.mp3"
    bye_path = audio_dir / "bye.mp3"

    repeat_kws = lang_data["BALANCE_REPEAT_KWS"]
    back_kws = lang_data["BALANCE_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(str(info_path))
        play_mp3(str(follow_path))
        beep(0.15, 900)
        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Saldo] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue
        if match_keywords(ans or "", back_kws):
            return "back"
        if match_keywords(ans or "", exit_kws):
            play_mp3(str(bye_path))
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            return "exit"

        play_mp3(str(unk_path))

def simulation_submenu(lang_data: dict, audio_dir: Path, stt_lang: str):
    info_path = audio_dir / "sim_info.mp3"
    follow_path = audio_dir / "sim_followup.mp3"
    unk_path = audio_dir / "unk.mp3"
    bye_path = audio_dir / "bye.mp3"

    repeat_kws = lang_data["SIM_REPEAT_KWS"]
    back_kws = lang_data["SIM_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(str(info_path))
        play_mp3(str(follow_path))
        beep(0.15, 900)
        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Simulação] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue
        if match_keywords(ans or "", back_kws):
            return "back"
        if match_keywords(ans or "", exit_kws):
            play_mp3(str(bye_path))
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            return "exit"

        play_mp3(str(unk_path))

def agent_submenu(lang_data: dict, audio_dir: Path, stt_lang: str):
    info_path = audio_dir / "agent_info.mp3"
    follow_path = audio_dir / "agent_followup.mp3"
    unk_path = audio_dir / "unk.mp3"
    bye_path = audio_dir / "bye.mp3"

    repeat_kws = lang_data["AGENT_REPEAT_KWS"]
    back_kws = lang_data["AGENT_BACK_KWS"]
    exit_kws = lang_data["EXIT_KWS"]

    while True:
        play_mp3(str(info_path))
        play_mp3(str(follow_path))
        beep(0.15, 900)
        ans = recognize_speech(stt_lang, phrase_time_limit=4)
        print(f"[STT][Atendente] Você disse / You said: {ans!r}")

        if match_keywords(ans or "", repeat_kws):
            continue
        if match_keywords(ans or "", back_kws):
            return "back"
        if match_keywords(ans or "", exit_kws):
            play_mp3(str(bye_path))
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            return "exit"

        play_mp3(str(unk_path))

def run_ivr(lang_data: dict, code: str):
    """
    Executa o fluxo principal do IVR no idioma selecionado.
    """
    from .audio import play_mp3  # evitar import circular
    from .stt import recognize_speech
    from .match import identify_option
    from .config import AUDIO_BASE_DIR

    stt_lang = lang_data["STT_LANG"]
    audio_dir = AUDIO_BASE_DIR / code
    ensure_assets(lang_data, audio_dir)

    # Saudação e menu
    play_mp3(str(audio_dir / "welcome.mp3"))
    play_mp3(str(audio_dir / "options.mp3"))

    # Loop principal
    while True:
        play_mp3(str(audio_dir / "hint.mp3"))
        beep(0.15, 900)

        transcript = recognize_speech(stt_lang, phrase_time_limit=5)
        print(f"[STT] Você disse / You said: {transcript!r}")

        opt = identify_option(transcript or "", lang_data["KEYWORDS"])
        if opt is None:
            play_mp3(str(audio_dir / "unk.mp3"))
            play_mp3(str(audio_dir / "options.mp3"))
            continue

        play_mp3(str(audio_dir / f"confirm_{opt}.mp3"))

        if opt == 1:
            res = balance_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(str(audio_dir / "options.mp3"))
            continue

        if opt == 2:
            res = simulation_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(str(audio_dir / "options.mp3"))
            continue

        if opt == 3:
            res = agent_submenu(lang_data, audio_dir, stt_lang)
            if res == "exit":
                break
            play_mp3(str(audio_dir / "options.mp3"))
            continue

        if opt == 4:
            play_mp3(str(audio_dir / "bye.mp3"))
            print("Atendimento encerrado. Obrigado! / Exiting. Goodbye!")
            break

        play_mp3(str(audio_dir / "options.mp3"))
