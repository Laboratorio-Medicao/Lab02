def mark_text(text: str, markers: list[str]) -> list[str]:
    if text == "":
        raise ValueError("Texto não pode ser vazio")
    if any(not isinstance(marker, str) or marker == "" for marker in markers):
        raise ValueError("Todos os marcadores devem ser strings não vazias")
    markers = sorted(markers, key=len, reverse=True)
    token = []
    current = ""
    i = 0
    while i < len(text):
        for marker in markers:
            if text[i:].startswith(marker):
                if current:
                    token.append(current)
                token.append(marker)
                i += len(marker)
                current = ""
                break
        else:
            current += text[i]
            i += 1
    if current:
        token.append(current)
    return [t for t in (t.strip() for t in token) if t]
