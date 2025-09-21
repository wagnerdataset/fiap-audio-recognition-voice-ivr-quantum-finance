# ivr/providers/azure_utils.py
from urllib.parse import urlparse
import re

def split_region_or_endpoint(val: str) -> tuple[str, str]:
    """
    Retorna (region, endpoint). Se 'val' for URL, extrai a região do host e retorna endpoint=URL.
    Se 'val' for apenas região (ex.: 'eastus2'), retorna (region, "").
    """
    v = (val or "").strip()
    if not v:
        return "", ""

    if v.lower().startswith(("http://", "https://")):
        url = urlparse(v)
        host = (url.hostname or "").lower()
        # tenta capturar prefixo da região no host
        m = re.match(r"^([a-z0-9-]+)\.(api\.cognitive\.microsoft\.com|tts\.speech\.microsoft\.com|stt\.speech\.microsoft\.com)$", host)
        region = m.group(1) if m else (host.split(".", 1)[0] if "." in host else host)
        return region, v  # mantém a URL original como endpoint
    else:
        return v.lower(), ""
