def mark_text(text: str, markers: list[str]) -> list[str]:
    if not text or any(not marker for marker in markers):
        raise ValueError("texto ou marcador invalido")
    ordered = sorted(set(markers), key=len, reverse=True)
    tokens = []
    current = ""
    index = 0
    while index < len(text):
        match = next((marker for marker in ordered if text.startswith(marker, index)), None)
        if match:
            if current.strip():
                tokens.append(current.strip())
            current = ""
            tokens.append(match)
            index += len(match)
        else:
            current += text[index]
            index += 1
    if current.strip():
        tokens.append(current.strip())
    return tokens