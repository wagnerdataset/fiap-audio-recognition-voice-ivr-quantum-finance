import os, tempfile
import azure.cognitiveservices.speech as speechsdk

# IMPORTAR O MÓDULO, NÃO OS NOMES
from .. import config as cfg

VOICE_MAP = {
    "pt-br": "pt-BR-AntonioNeural",
    "pt":    "pt-BR-AntonioNeural",
    "en":    "en-US-GuyNeural",
    "en-us": "en-US-GuyNeural",
}

def _speech_config(lang_code_hint: str = "pt-BR") -> speechsdk.SpeechConfig:
    if not cfg.AZURE_SPEECH_KEY:
        raise RuntimeError("AZURE_SPEECH_KEY não configurada.")
    if cfg.AZURE_SPEECH_ENDPOINT:
        conf = speechsdk.SpeechConfig(endpoint=cfg.AZURE_SPEECH_ENDPOINT,
                                      subscription=cfg.AZURE_SPEECH_KEY)
    else:
        if not cfg.AZURE_SPEECH_REGION:
            raise RuntimeError("AZURE_SPEECH_REGION não configurada.")
        conf = speechsdk.SpeechConfig(subscription=cfg.AZURE_SPEECH_KEY,
                                      region=cfg.AZURE_SPEECH_REGION)
    conf.speech_recognition_language = lang_code_hint
    return conf

def validate_azure_credentials(return_details: bool = False):
    try:
        if not cfg.AZURE_SPEECH_KEY:
            return (False, "chave vazia") if return_details else False
        conf = _speech_config("en-US")
        conf.speech_synthesis_voice_name = VOICE_MAP.get("en", "en-US-GuyNeural")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tmp_path = tf.name
        try:
            out_cfg = speechsdk.audio.AudioOutputConfig(filename=tmp_path)
            synth = speechsdk.SpeechSynthesizer(speech_config=conf, audio_config=out_cfg)
            res = synth.speak_text_async("credentials check").get()
            if res.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return (True, "") if return_details else True
            if res.reason == speechsdk.ResultReason.Canceled:
                details = speechsdk.CancellationDetails(res)
                msg = f"Canceled: reason={details.reason}, code={getattr(details,'error_code',None)}, details={details.error_details}"
                if cfg.DEBUG: cfg.log(f"[Azure SDK] {msg}")
                return (False, msg) if return_details else False
            return (False, f"Unexpected reason: {res.reason}") if return_details else False
        finally:
            try: os.remove(tmp_path)
            except Exception: pass
    except Exception as e:
        if cfg.DEBUG: cfg.log(f"validate_azure_credentials exception: {e}")
        return (False, str(e)) if return_details else False

def synth_to_file(text: str, out_path: str, tts_lang_code: str):
    conf = _speech_config()
    voice = VOICE_MAP.get(tts_lang_code.lower(), VOICE_MAP.get("pt-br"))
    if voice: conf.speech_synthesis_voice_name = voice
    out_cfg = speechsdk.audio.AudioOutputConfig(filename=out_path)
    synth = speechsdk.SpeechSynthesizer(speech_config=conf, audio_config=out_cfg)
    if cfg.DEBUG: cfg.log(f"Azure TTS [{tts_lang_code} | {voice}] -> {out_path}")
    result = synth.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted: return
    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails(result)
        raise RuntimeError(f"Azure TTS cancelado: {details.reason} ({getattr(details,'error_code',None)}) {details.error_details}")
    raise RuntimeError(f"Azure TTS falhou: {result.reason}")

def recognize_once(stt_lang_code: str = "pt-BR", phrase_time_limit: int = 5) -> str | None:
    conf = _speech_config(stt_lang_code)
    conf.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, str(800))
    audio_in = speechsdk.audio.AudioConfig(use_default_microphone=True)
    rec = speechsdk.SpeechRecognizer(speech_config=conf, audio_config=audio_in)
    if cfg.DEBUG: cfg.log(f"Azure STT listening once ({stt_lang_code})...")
    result = rec.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return (result.text or "").strip()
    return None
