"""Small heuristic language detector with no heavy dependencies."""
import re
_JA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")

def detect_language(text: str) -> str:
    clean = text.strip()
    if not clean:
        return "unsupported"
    if _JA_RE.search(clean):
        return "ja"
    letters = sum(ch.isalpha() and ch.isascii() for ch in clean)
    return "en" if letters >= max(3, len(clean) * 0.2) else "unsupported"
