def mark_text(text: str, markers: list[str]) -> list[str]:
    if not text or any(not marker for marker in markers):
        raise ValueError("texto e marcadores não podem ser vazios")

    ordered_markers = sorted(set(markers), key=len, reverse=True)
    tokens: list[str] = []
    buffer = ""
    position = 0

    while position < len(text):
        marker = next((m for m in ordered_markers if text.startswith(m, position)), None)
        if marker is not None:
            if buffer.strip():
                tokens.append(buffer.strip())
            buffer = ""
            tokens.append(marker)
            position += len(marker)
        else:
            buffer += text[position]
            position += 1

    if buffer.strip():
        tokens.append(buffer.strip())

    return tokens
