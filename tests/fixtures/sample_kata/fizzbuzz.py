def fizzbuzz(n: int) -> str:
    if n <= 0:
        raise ValueError("n deve ser positivo")
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def fizzbuzz_sequence(limit: int) -> list[str]:
    return [fizzbuzz(n) for n in range(1, limit + 1)]
