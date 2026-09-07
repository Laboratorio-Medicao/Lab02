from fizzbuzz import fizzbuzz, fizzbuzz_sequence


def test_multiples_of_three_return_fizz():
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(9) == "Fizz"


def test_multiples_of_five_return_buzz():
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(10) == "Buzz"


def test_multiples_of_fifteen_return_fizzbuzz():
    assert fizzbuzz(15) == "FizzBuzz"


def test_other_numbers_return_the_number_as_string():
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(7) == "7"


def test_sequence_up_to_limit():
    assert fizzbuzz_sequence(5) == ["1", "2", "Fizz", "4", "Buzz"]
