# Kata 01 — Faixas de sinal

Implemente `compress_signals(values)`. A função recebe uma lista não vazia de
números inteiros e deve retornar uma lista de tuplas `(inicio, fim)` que
representam faixas de valores consecutivos presentes na lista, em ordem de
aparecimento. Valores repetidos não devem criar novas faixas.

Exemplo: `[4, 5, 7, 6, 10]` produz `[(4, 7), (10, 10)]`. A entrada pode estar
desordenada. Para uma lista vazia, lance `ValueError`.