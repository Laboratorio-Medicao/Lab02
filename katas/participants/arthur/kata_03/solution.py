def delivery_slots(deliveries: list[dict]) -> list[list[str]]:
    groups: dict[int, list[str]] = {}

    for delivery in deliveries:
        if "name" not in delivery or "slot" not in delivery:
            raise ValueError("delivery must have 'name' and 'slot'")

        slot = delivery["slot"]
        if not isinstance(slot, int) or slot <= 0:
            raise ValueError("slot must be a positive integer")

        groups.setdefault(slot, []).append(delivery["name"])

    return [groups[slot] for slot in sorted(groups)]