# ivr/providers/azure_validate.py
import requests

def voices_list_url(region: str) -> str:
    region = (region or "").strip().lower()
    return f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"

def validate_credentials_rest(key: str, region: str, timeout: float = 6.0) -> tuple[bool, str]:
    """
    Valida credenciais fazendo um GET no /voices/list.
    Retorna (ok, detalhe). ok=True se HTTP 200.
    """
    url = voices_list_url(region)
    headers = {"Ocp-Apim-Subscription-Key": key}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return True, f"OK 200 em {url}"
        elif resp.status_code in (401, 403):
            return False, f"Credenciais inválidas? HTTP {resp.status_code} em {url}"
        else:
            return False, f"HTTP {resp.status_code} em {url}: {resp.text[:200]}"
    except requests.exceptions.RequestException as e:
        return False, f"Falha de rede ao acessar {url}: {e}"
