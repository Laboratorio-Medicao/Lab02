def neighbor_scores(scores: list[int]) -> list[int]:

    if not scores:
        raise ValueError("A lista de pontuações não pode estar vazia.")

    result = []
    tamanho = len(scores)

    for i in range(tamanho):
        soma = scores[i]
        
        if i > 0:
            soma += scores[i - 1]
        if i < tamanho - 1:
            soma += scores[i + 1]
        
        result.append(soma)
    return result