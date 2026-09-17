def apply_inventory(initial: dict[str, int], operations: list[tuple[str, str, int]]) -> dict[str, int]:
    inventory = initial.copy()

    for acao, item, quantidade in operations:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que 0.")
        if acao == "in":
            inventory[item] = inventory.get(item, 0) + quantidade
        elif acao == "out":
            atual = inventory.get(item, 0)
            if quantidade > atual:
                raise ValueError("Quantidade de retirada maior que a quantidade no inventário.")
            inventory[item] = atual - quantidade
        else:
            raise ValueError("Ação inválida. Use 'in' ou 'out'.")
    return {item: qtd for item, qtd in inventory.items() if qtd > 0}

    raise NotImplementedError