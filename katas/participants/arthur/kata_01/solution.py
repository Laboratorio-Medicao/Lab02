def compress_signals(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        raise ValueError("values must not be empty")

    ranges: list[tuple[int, int]] = []
    for value in sorted(set(values)):
        if ranges and value == ranges[-1][1] + 1:
            start, _ = ranges[-1]
            ranges[-1] = (start, value)
        else:
            ranges.append((value, value))

    return ranges