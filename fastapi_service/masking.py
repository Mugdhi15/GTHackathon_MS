# masking.py
import re

PHONE_RE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
NAME_RE = re.compile(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b")

def mask_pii(text: str):
    text = PHONE_RE.sub("[PHONE]", text)
    text = NAME_RE.sub("[NAME]", text)
    # mask order numbers like #1234
    text = re.sub(r"#\d+", "[ORDER_ID]", text)
    return text
