import pytest

from .solution import rotate_teams


def test_moves_last_full_team_to_front():
    assert rotate_teams(["A", "B", "C", "D"], 2) == [["C", "D"], ["A", "B"]]


def test_keeps_remainder_as_initial_team_after_rotation():
    assert rotate_teams(["A", "B", "C", "D", "E"], 2) == [["E"], ["A", "B"], ["C", "D"]]


def test_team_size_larger_than_people_creates_one_team():
    assert rotate_teams(["A", "B"], 5) == [["A", "B"]]


def test_does_not_mutate_people():
    people = ["A", "B", "C"]
    rotate_teams(people, 2)
    assert people == ["A", "B", "C"]


@pytest.mark.parametrize("people,size", [([], 2), (["A"], 0), (["A"], -1)])
def test_rejects_invalid_arguments(people, size):
    with pytest.raises(ValueError):
        rotate_teams(people, size)