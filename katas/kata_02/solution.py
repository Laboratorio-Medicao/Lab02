def apply_inventory(initial: dict[str, int], operations: list[tuple[str, str, int]]) -> dict[str, int]:
    inventory = dict(initial)
    if any(quantity < 0 for quantity in inventory.values()):
        raise ValueError("estoque inicial invalido")
    for action, item, quantity in operations:
        if quantity <= 0 or action not in {"in", "out"}:
            raise ValueError("operacao invalida")
        current = inventory.get(item, 0)
        if action == "out" and quantity > current:
            raise ValueError("estoque insuficiente")
        updated = current + quantity if action == "in" else current - quantity
        if updated:
            inventory[item] = updated
        else:
            inventory.pop(item, None)
    return inventory