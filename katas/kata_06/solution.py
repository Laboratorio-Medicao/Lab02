def neighbor_scores(scores: list[int]) -> list[int]:
    if not scores:
        raise ValueError("scores nao pode ser vazio")
    result = []
    for index, score in enumerate(scores):
        total = score
        if index:
            total += scores[index - 1]
        if index + 1 < len(scores):
            total += scores[index + 1]
        result.append(total)
    return result