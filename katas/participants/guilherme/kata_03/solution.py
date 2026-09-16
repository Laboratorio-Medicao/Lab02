def delivery_slots(deliveries: list[dict]) -> list[list[str]]:
    groups: dict[int, list[str]] = {}
    for delivery in deliveries:
        if "name" not in delivery or "slot" not in delivery or delivery["slot"] <= 0:
            raise ValueError("entrega inválida")
        groups.setdefault(delivery["slot"], []).append(delivery["name"])
    return [groups[slot] for slot in sorted(groups)]
