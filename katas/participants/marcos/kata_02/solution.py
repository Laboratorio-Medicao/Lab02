def apply_inventory(initial: dict[str, int], operations: list[tuple[str, str, int]]) -> dict[str, int]:

    inv = initial.copy()

    for act, item, qtd in operations:

        if qtd<=0:
         raise ValueError()
        
        if item in inv:
            atual = inv[item]

        else: 
           atual = 0

        if act == "in":
           atual = atual + qtd

        if act == "out":
           if qtd > atual:
               raise ValueError()

           atual = atual - qtd

        if atual == 0:
            if item in inv:
                del inv[item]

        else:
            inv[item] = atual

    return inv