# Kata 04 — Marcadores de texto

Implemente `mark_text(text, markers)`. A função recebe um texto e uma lista de
marcadores. Retorne o texto dividido em tokens, mantendo os marcadores como
tokens próprios e removendo espaços vazios. Marcadores podem ter mais de um
caractere; quando houver sobreposição, o marcador mais longo deve ser escolhido.

O texto não pode ser vazio e os marcadores não podem ser vazios. Em qualquer
uma dessas situações, lance `ValueError`.