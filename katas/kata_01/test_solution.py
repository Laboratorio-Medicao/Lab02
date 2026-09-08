import pytest

from .solution import compress_signals


def test_compresses_sorted_consecutive_values():
    assert compress_signals([4, 5, 7, 6, 10]) == [(4, 7), (10, 10)]


def test_ignores_duplicates():
    assert compress_signals([2, 2, 3, 5, 5]) == [(2, 3), (5, 5)]


def test_handles_negative_values():
    assert compress_signals([-3, -1, -2, 2]) == [(-3, -1), (2, 2)]


def test_single_value_is_a_single_range():
    assert compress_signals([8]) == [(8, 8)]


def test_empty_input_is_invalid():
    with pytest.raises(ValueError):
        compress_signals([])