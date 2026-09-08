import pytest

from .solution import neighbor_scores


def test_sums_existing_neighbors():
    assert neighbor_scores([2, 5, 3]) == [7, 10, 8]


def test_handles_single_score():
    assert neighbor_scores([9]) == [9]


def test_handles_negative_scores():
    assert neighbor_scores([-2, 4, -1, 3]) == [2, 1, 6, 2]


def test_returns_a_new_list():
    scores = [1, 2]
    result = neighbor_scores(scores)
    assert result == [3, 3]
    assert result is not scores


def test_rejects_empty_input():
    with pytest.raises(ValueError):
        neighbor_scores([])