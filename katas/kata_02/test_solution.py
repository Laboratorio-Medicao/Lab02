import pytest

from .solution import apply_inventory


def test_applies_entries_and_withdrawals():
    assert apply_inventory({"cable": 3}, [("in", "cable", 2), ("out", "cable", 1)]) == {"cable": 4}


def test_does_not_mutate_initial_inventory():
    initial = {"bolt": 2}
    apply_inventory(initial, [("in", "nut", 1)])
    assert initial == {"bolt": 2}


def test_adds_new_item():
    assert apply_inventory({}, [("in", "clip", 4)]) == {"clip": 4}


def test_removes_zero_quantity_items():
    assert apply_inventory({"pin": 2}, [("out", "pin", 2)]) == {}


def test_rejects_overdraft():
    with pytest.raises(ValueError):
        apply_inventory({"pin": 1}, [("out", "pin", 2)])


def test_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        apply_inventory({}, [("in", "clip", 0)])