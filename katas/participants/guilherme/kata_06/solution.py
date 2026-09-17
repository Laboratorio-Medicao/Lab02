def neighbor_scores(scores: list[int]) -> list[int]:
    if not scores:
        raise ValueError("A lista de pontuações não pode ser vazia")
    if any(not isinstance(score, int) for score in scores):
        raise ValueError("Todos os elementos da lista devem ser inteiros")
    result = []
    if len(scores) == 1: 
        return list(scores)
    
    for i in range(len(scores)):
        if i == 0:
            result.append(scores[i] + scores[i + 1])
        elif i == len(scores) - 1:
            result.append(scores[i] + scores[i-1])
        else:
            result.append(scores[i] + scores[i-1] + scores[i+1])
    return result
