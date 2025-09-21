import json
import wave
import tempfile
import os

import wavio
import sounddevice as sd
import speech_recognition as sr

from . import config as cfg

try:
    from .providers.azure_speech import recognize_once as azure_recognize_once
except Exception:
    azure_recognize_once = None

def record_mono(seconds=5, fs=16000):
    if cfg.DEBUG:
        cfg.log(f"Gravando {seconds}s @ {fs}Hz ...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    return audio, fs

def recognize_speech(stt_lang="pt-BR", phrase_time_limit=5):
    if cfg.MODE == "text":
        return input("(digite sua resposta)\n> ").strip()

    # Provider Azure primeiro (se selecionado)
    if cfg.PROVIDER == "azure":
        try:
            if azure_recognize_once is None:
                raise RuntimeError("Módulo Azure não disponível.")
            return azure_recognize_once(stt_lang_code=stt_lang, phrase_time_limit=phrase_time_limit)
        except Exception as e:
            print(f"[WARN] Azure STT falhou ({e}). Caindo para Vosk/Google...")

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
        if cfg.DEBUG:
            import traceback; traceback.print_exc()
        return None
