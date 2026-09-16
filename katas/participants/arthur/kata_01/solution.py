def compress_signals(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        raise ValueError("values nao pode ser vazio")
    unique = sorted(set(values))
    ranges = []
    start = previous = unique[0]
    for value in unique[1:]:
        if value != previous + 1:
            ranges.append((start, previous))
            start = value
        previous = value
    ranges.append((start, previous))
    return ranges