import os
from pathlib import Path

COMPANY = "QuantumFinance"

# Flags de execução
MODE = os.environ.get("IVR_MODE", "voice").lower()  # "voice" | "text"
DEBUG = os.environ.get("IVR_DEBUG", "0") == "1"

# Provedor de Voz/STT: "default" (gTTS+Google/Vosk) | "azure"
PROVIDER = os.environ.get("IVR_PROVIDER", "").strip().lower() or "default"

# Credenciais Azure (podem vir por env ou ser definidas via set_azure_credentials)
AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY", "").strip()
AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "").strip()
AZURE_SPEECH_ENDPOINT = os.environ.get("AZURE_SPEECH_ENDPOINT", "").strip()

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
AUDIO_BASE_DIR = BASE_DIR / "audio"
AUDIO_BASE_DIR.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def set_provider(p: str):
    """Define o provedor em runtime (antes de iniciar a conversa)."""
    global PROVIDER
    PROVIDER = (p or "default").lower()
    log(f"Provider set to: {PROVIDER}")

def set_azure_credentials(key: str, region: str = "", endpoint: str = ""):
    """Define credenciais Azure em runtime (podem vir como região OU endpoint)."""
    global AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_SPEECH_ENDPOINT
    AZURE_SPEECH_KEY = (key or "").strip()
    AZURE_SPEECH_REGION = (region or "").strip()
    AZURE_SPEECH_ENDPOINT = (endpoint or "").strip()
    if DEBUG:
        masked = AZURE_SPEECH_KEY[:4] + "..." if AZURE_SPEECH_KEY else "(vazia)"
        log(f"Azure region='{AZURE_SPEECH_REGION}' endpoint='{AZURE_SPEECH_ENDPOINT}' key={masked}")