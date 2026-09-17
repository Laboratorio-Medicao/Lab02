def mark_text(text: str, markers: list[str]) -> list[str]:
    
    if not text:
        raise ValueError("O texto não pode ser vazio.")
    
    if not markers:
        raise ValueError("A lista de marcadores não pode ser vazia.")
    
    if any(marker == "" for marker in markers):
        raise ValueError("Nenhum marcador pode ser uma string vazia.")

    sorted_markers = sorted(markers, key=len, reverse=True);

    tokens = [];
    buffer = "";
    i = 0;
    
    while i < len(text):
        matched = False

        for marker in sorted_markers:
            if text.startswith(marker, i):
                stripped_buffer = buffer.strip()
                if stripped_buffer:
                    tokens.append(stripped_buffer)
                tokens.append(marker)

                i += len(marker)
                buffer = ""
                matched = True
                break
        if not matched:
            buffer += text[i]
            i += 1
        
    final_buffer = buffer.strip()
    if final_buffer:
        tokens.append(final_buffer)
    return tokens