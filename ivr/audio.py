import os
from pathlib import Path
import numpy as np
import sounddevice as sd
from gtts import gTTS
import pygame

from .config import AUDIO_BASE_DIR, DEBUG, log

_PYGAME_READY = False

def ensure_pygame():
    global _PYGAME_READY
    if not _PYGAME_READY:
        pygame.mixer.init()
        _PYGAME_READY = True

def play_mp3(path_mp3: str):
    if not os.path.exists(path_mp3):
        print(f"[WARN] Áudio não encontrado: {path_mp3}")
        return
    try:
        ensure_pygame()
        if DEBUG:
            log(f"Tocando {path_mp3}")
        pygame.mixer.music.load(path_mp3)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(50)
    except Exception as e:
        print(f"[WARN] Falha ao tocar MP3 com pygame: {e}")

def beep(duration=0.2, freq=800):
    try:
        fs = 44100
        t = np.linspace(0, duration, int(fs * duration), False)
        tone = np.sin(freq * t * 2 * np.pi) * 0.2
        sd.play(tone.astype(np.float32), fs)
        sd.wait()
    except Exception as e:
        print(f"[WARN] Beep falhou: {e}")

def tts_to_mp3(text: str, path_mp3: str, lang_code: str):
    try:
        if os.path.exists(path_mp3):
            os.remove(path_mp3)
    except Exception:
        pass
    if DEBUG:
        log(f"gTTS [{lang_code}] -> {path_mp3}")
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(path_mp3)

def ensure_assets(lang_data: dict, audio_dir: Path):
    """
    Gera todos os áudios do idioma escolhido no diretório audio/<pt|en>
    """
    audio_dir.mkdir(parents=True, exist_ok=True)
    assets = {
        "welcome.mp3": lang_data["GREETING"],
        "options.mp3": lang_data["OPTIONS"],
        "hint.mp3": lang_data["HINT"],
        "unk.mp3": lang_data["UNRECOGNIZED"],
        "bye.mp3": lang_data["BYE"],
        "confirm_1.mp3": lang_data["CONFIRM"][1],
        "confirm_2.mp3": lang_data["CONFIRM"][2],
        "confirm_3.mp3": lang_data["CONFIRM"][3],
        "confirm_4.mp3": lang_data["CONFIRM"][4],
        # Submenus
        "balance_info.mp3": lang_data["BALANCE_INFO"],
        "balance_followup.mp3": lang_data["BALANCE_FOLLOWUP"],
        "sim_info.mp3": lang_data["SIM_INFO"],
        "sim_followup.mp3": lang_data["SIM_FOLLOWUP"],
        "agent_info.mp3": lang_data["AGENT_INFO"],
        "agent_followup.mp3": lang_data["AGENT_FOLLOWUP"],
    }
    tts_lang = lang_data["TTS_LANG"]
    for fname, text in assets.items():
        tts_to_mp3(text, str(audio_dir / fname), lang_code=tts_lang)

def lang_prompt_files():
    """
    Retorna paths dos prompts bilíngues de seleção de idioma (em audio/)
    """
    ask_pt = AUDIO_BASE_DIR / "ask_lang_pt.mp3"
    ask_en = AUDIO_BASE_DIR / "ask_lang_en.mp3"
    return ask_pt, ask_en
