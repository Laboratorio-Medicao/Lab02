def compress_signals(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        raise ValueError("Input list cannot be empty")

    nums = sorted(set(values))
    ranges = []

    start = nums[0]
    end = nums[0]

    for i in nums[1:]:
        if i == end + 1:
            end = i
        else:
            ranges.append((start, end))
            start = i
            end = i

    ranges.append((start, end))

    return ranges