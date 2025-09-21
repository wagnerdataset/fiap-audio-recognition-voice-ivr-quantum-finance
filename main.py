# main.py
import os
from getpass import getpass
from ivr.providers.azure_utils import split_region_or_endpoint

from ivr.menus import select_language, run_ivr
from ivr.config import (
    set_provider,
    AZURE_SPEECH_KEY,
    AZURE_SPEECH_REGION,
    set_azure_credentials,
)

def select_provider_cli():
    """
    Pergunta (em texto) qual provedor usar ANTES de iniciar a conversa.
    Só pula se IVR_PROVIDER estiver definida no ambiente.
    """
    env_provider = os.environ.get("IVR_PROVIDER", "").strip().lower()
    if env_provider in ("azure", "default"):
        print(f"Provedor atual: {env_provider} (definido por IVR_PROVIDER).")
        return env_provider

    print("=== Selecione o provedor de voz/STT ===")
    print("[1] Azure Speech Services  (requer chave e região)")
    print("[2] Padrão (gTTS + Google/Vosk)")
    choice = (input("> ").strip() or "2")
    return "azure" if choice == "1" else "default"

def ensure_azure_ready():
    """Verifica se o SDK Azure está instalado (import)."""
    try:
        import azure.cognitiveservices.speech as _  # noqa: F401
        return True
    except Exception:
        print("Azure SDK não encontrado. Instale com:")
        print("  pip install azure-cognitiveservices-speech")
        return False

def prompt_azure_credentials_if_needed():
    key = AZURE_SPEECH_KEY or os.environ.get("AZURE_SPEECH_KEY", "")
    region_in = os.environ.get("AZURE_SPEECH_REGION", "")  # legado
    endpoint_in = os.environ.get("AZURE_SPEECH_ENDPOINT", "")

    if not key:
        print("Informe sua chave do Azure Speech (AZURE_SPEECH_KEY).")
        key = getpass("AZURE_SPEECH_KEY: ")

    if not (region_in or endpoint_in):
        print("Informe sua região OU cole seu endpoint (ex.: 'eastus2' ou 'https://eastus2.api.cognitive.microsoft.com').")
        typed = input("AZURE_REGION or ENDPOINT: ").strip()
    else:
        typed = endpoint_in or region_in

    region, endpoint = split_region_or_endpoint(typed)

    key = (key or "").strip()
    if not key or (not region and not endpoint):
        print("Credenciais/Região/Endpoint inválidos. Não é possível continuar com o provedor Azure.")
        return False

    # Seta internamente: se veio URL, salvamos 'endpoint' e também a 'region' extraída
    set_azure_credentials(key, region=region, endpoint=endpoint)

    # SDK instalado?
    try:
        import azure.cognitiveservices.speech as _  # noqa: F401
    except Exception:
        print("Azure SDK não encontrado. Instale com: pip install azure-cognitiveservices-speech")
        return False

    # Validação real via SDK (TTS → arquivo temporário)
    try:
        from ivr.providers.azure_speech import validate_azure_credentials
        ok = validate_azure_credentials()
    except Exception as e:
        print(f"Falha ao validar via SDK: {e}")
        return False

    if not ok:
        shown = endpoint if endpoint else region
        print("Falha na validação das credenciais no SDK (chave/região/endpoint incorretos ou recurso inválido).")
        print(f"  • Usando: {shown}")
        print("  • Dica: para multi-service use o endpoint completo (ex.: https://eastus2.api.cognitive.microsoft.com)")
        return False

    return True

def main():
    # 1) Provedor
    prov = select_provider_cli()
    set_provider(prov)

    # 2) Se Azure, colete e **valide** credenciais antes de qualquer áudio
    if prov == "azure":
        if not prompt_azure_credentials_if_needed():
            print("Encerrando. Ajuste as credenciais Azure ou selecione o provedor Padrão.")
            return

    # 3) Seleção de idioma e execução do IVR
    lang_data, code = select_language()
    run_ivr(lang_data, code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
