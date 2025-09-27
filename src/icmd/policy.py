import os, re, pathlib

FORBID = [r"\brm\s+-rf\s+/", r">\s*/dev/sd[a-z]", r"\bmkfs\.", r"\bdd\s+if=", r"\bchmod\s+-R\s+777\b"]

SCRUB_PRESETS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "token": re.compile(r"\b(AKI[0-9A-Z]{16}|ya29\.[A-Za-z0-9\-_]+|ghp_[A-Za-z0-9]{36,})\b")
}

def dangerous(cmd: str) -> bool:
    t = cmd.strip().lower()
    return any(re.search(rx, t) for rx in FORBID)

def apply_redaction(text: str, kinds):
    if not kinds: return text
    for k in kinds:
        rx = SCRUB_PRESETS.get(k)
        if rx: text = rx.sub(f"<redacted:{k}>", text)
    return text

def assert_within_root(_=None):
    return True
