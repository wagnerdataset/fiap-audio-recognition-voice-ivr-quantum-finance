import os
from pathlib import Path

COMPANY = "QuantumFinance"

# Flags de execução
MODE = os.environ.get("IVR_MODE", "voice").lower()  # "voice" | "text"
DEBUG = os.environ.get("IVR_DEBUG", "0") == "1"

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
AUDIO_BASE_DIR = BASE_DIR / "audio"
AUDIO_BASE_DIR.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    if DEBUG:
        print(f"[DEBUG] {msg}")
