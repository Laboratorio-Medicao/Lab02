# Seleção dos katas

## Decisão

Foram selecionados seis exercícios autorais, escritos especificamente para
este experimento em 07/09/2026. A fonte de cada enunciado é a própria equipe
do Lab02; não há URL externa, nome de problema conhecido ou solução pública a
ser reutilizada. Essa escolha atende à recomendação do enunciado de preferir
exercícios pouco indexados e reduz o risco de o assistente recuperar uma
solução memorizada.

Os diretórios usam `_` no nome (`kata_01`) para serem pacotes Python válidos,
mas os identificadores experimentais permanecem `kata-01` a `kata-06`.

## Catálogo

| ID | Exercício | Fonte | Dificuldade | Testes | Justificativa |
|---|---|---|---|---:|---|
| kata-01 | Faixas de sinal | Autoral, grupo Lab02 | Média | 5 | Ordenação, remoção de duplicatas, agrupamento de consecutivos e erro de entrada vazia. |
| kata-02 | Inventário de bolsos | Autoral, grupo Lab02 | Média | 6 | Atualização de estado, duas operações, cópia defensiva, remoção de zero e validações. |
| kata-03 | Grade de entregas | Autoral, grupo Lab02 | Média | 7 | Agrupamento por chave, ordenação dos grupos, preservação de ordem e validação de registros (3 casos parametrizados). |
| kata-04 | Marcadores de texto | Autoral, grupo Lab02 | Média | 6 | Percurso de string, marcadores multi-caractere, sobreposição e descarte de espaços (2 casos parametrizados). |
| kata-05 | Rodízio de equipes | Autoral, grupo Lab02 | Média | 7 | Particionamento, resto de divisão, rotação e preservação da entrada (3 casos parametrizados). |
| kata-06 | Pontuação por vizinhança | Autoral, grupo Lab02 | Média | 5 | Percurso indexado, tratamento das bordas, valores negativos e cópia do resultado. |

## Equivalência estimada

Os seis exercícios exigem uma única função principal, usam apenas tipos básicos
de Python e possuem entre 5 e 6 testes de aceitação. Cada um combina um caso
normal, um caso de borda, uma regra de transformação e uma validação de entrada.
As soluções de referência têm tamanho semelhante e devem ser resolvíveis no
time-box de 35 minutos por um estudante familiarizado com Python.

A classificação "Média" é uma estimativa de planejamento, não uma medição dos
participantes. Ela deverá ser revisada após um piloto com pelo menos um
participante que não tenha visto as soluções.

## Baixa indexação

Como os seis enunciados, títulos, nomes de funções e exemplos foram criados
para este repositório, a seleção não depende de uma plataforma pública e não
possui fonte externa a ser indexada. Antes da execução oficial, a equipe deve
fazer uma busca pelos títulos e por frases distintivas dos enunciados, registrar
a data e anexar os resultados ao relatório final. Qualquer resultado que revele
uma solução equivalente deve provocar a substituição do kata.

## Testes de aceitação

Cada diretório em [`katas/`](../katas/) contém `test_solution.py` e uma
`solution.py` de referência. A referência é usada somente para validar o
oráculo; os participantes devem iniciar o trial com a implementação removida,
mantendo os testes inalterados.

Validação executada:

```text
python -m pytest katas -q
36 passed
```

Os testes cobrem o comportamento funcional e não devem ser considerados parte
do código produzido pelo participante nas métricas de RQ3.