# Kata 03 — Grade de entregas

Implemente `delivery_slots(deliveries)`. Cada entrega é um dicionário com
`"name"` e `"slot"`, onde `slot` é um inteiro positivo. Retorne uma lista com
os nomes agrupados por horário, em ordem crescente de horário. Dentro do mesmo
horário, preserve a ordem original. Não altere a lista recebida.

Uma entrega sem os campos exigidos ou com horário não positivo deve lançar
`ValueError`.