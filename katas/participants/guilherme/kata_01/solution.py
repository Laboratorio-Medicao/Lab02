def compress_signals(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        raise ValueError("values não pode ser vazio")
    unique = sorted(set(values))
    ranges = []
    start = end = unique[0]
    for value in unique[1:]:
        if value == end + 1:
            end = value
        else:
            ranges.append((start, end))
            start = end = value
    ranges.append((start, end))
    return ranges
