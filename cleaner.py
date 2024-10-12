import re


def sanitize(text: str, lower: bool = False) -> str:
    if lower:
        text = text.lower()

    text = re.sub(r"[-. ]", "_", text)
    pattern = r"[^a-zA-Z0-9_]"

    return re.sub(pattern=pattern, string=text, repl="")
