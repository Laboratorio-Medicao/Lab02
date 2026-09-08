# Kata 02 — Inventário de bolsos

Implemente `apply_inventory(initial, operations)`. `initial` é um dicionário
com itens e quantidades. Cada operação é uma tupla `(acao, item, quantidade)`:
`"in"` adiciona e `"out"` remove. Retorne um novo dicionário, sem alterar a
entrada original. Itens que terminarem com quantidade zero devem ser omitidos.

Uma remoção que exceda o estoque disponível deve lançar `ValueError`. Quantidades
zero ou negativas também são inválidas.