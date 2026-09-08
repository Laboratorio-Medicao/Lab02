# Kata 05 — Rodízio de equipes

Implemente `rotate_teams(people, team_size)`. Divida a lista de pessoas em
equipes consecutivas de tamanho `team_size`, mas mova a última equipe para o
início do resultado. Se a quantidade não for divisível, a equipe inicial pode
ser menor; todas as pessoas devem aparecer uma única vez.

Retorne uma nova lista de listas. A entrada vazia ou um tamanho não positivo
deve lançar `ValueError`.