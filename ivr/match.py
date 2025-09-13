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
