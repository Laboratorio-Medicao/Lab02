def apply_inventory(initial: dict[str, int], operations: list[tuple[str, str, int]]) -> dict[str, int]:
    inventory = dict(initial)
    for action, item, quantity in operations:
        if quantity <= 0 or action not in {"in", "out"}:
            raise ValueError("operação inválida")
        current = inventory.get(item, 0)
        if action == "out" and quantity > current:
            raise ValueError("estoque insuficiente")
        new_quantity = current + quantity if action == "in" else current - quantity
        if new_quantity == 0:
            inventory.pop(item, None)
        else:
            inventory[item] = new_quantity
    return inventory
