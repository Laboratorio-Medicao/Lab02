# Kata 06 — Pontuação por vizinhança

Implemente `neighbor_scores(scores)`. Para cada posição de uma lista não vazia
de inteiros, calcule `valor + vizinhos`, somando o elemento imediatamente à
esquerda e o imediatamente à direita quando existirem. Retorne uma nova lista.

Exemplo: `[2, 5, 3]` produz `[7, 10, 8]`. Para entrada vazia, lance
`ValueError`.