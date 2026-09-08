import pytest

from .solution import delivery_slots


def test_groups_names_by_ascending_slot():
    deliveries = [{"name": "Bia", "slot": 2}, {"name": "Ana", "slot": 1}, {"name": "Caio", "slot": 2}]
    assert delivery_slots(deliveries) == [["Ana"], ["Bia", "Caio"]]


def test_preserves_order_inside_slot():
    deliveries = [{"name": "first", "slot": 3}, {"name": "second", "slot": 3}]
    assert delivery_slots(deliveries) == [["first", "second"]]


def test_empty_input_returns_empty_groups():
    assert delivery_slots([]) == []


def test_does_not_mutate_input():
    deliveries = [{"name": "Ana", "slot": 1}]
    delivery_slots(deliveries)
    assert deliveries == [{"name": "Ana", "slot": 1}]


@pytest.mark.parametrize("delivery", [{"name": "Ana"}, {"slot": 1}, {"name": "Ana", "slot": 0}])
def test_rejects_invalid_delivery(delivery):
    with pytest.raises(ValueError):
        delivery_slots([delivery])