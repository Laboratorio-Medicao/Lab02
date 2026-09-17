def neighbor_scores(scores: list[int]) -> list[int]:
    if not scores:
        raise ValueError("scores não pode ser vazio")

    total = len(scores)
    result = []
    for index in range(total):
        value = scores[index]
        if index > 0:
            value += scores[index - 1]
        if index + 1 < total:
            value += scores[index + 1]
        result.append(value)

    return result
