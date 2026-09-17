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

## Evidência empírica observada (atualizado em 2026-09-17, após S02)

A estimativa acima permanece uma estimativa de planejamento — nenhum piloto
formal com participante isento foi executado. Porém, a execução real da S02
já produz duas fontes de evidência complementares, registradas aqui por
transparência (não substituem um piloto formal, mas dão um primeiro sinal
empírico):

**(a) Estrutura da solução de referência** (`katas/kata_0N/solution.py`, via Radon):

| Kata | LOC | Complexidade ciclomática | Testes |
|---|---:|---:|---:|
| kata-01 | 14 | 4.0 | 5 |
| kata-02 | 17 | 10.0 | 6 |
| kata-03 | 8 | 6.0 | 7 |
| kata-04 | 22 | 10.0 | 6 |
| kata-05 | 6 | 4.0 | 5 |
| kata-06 | 13 | 5.0 | 6 |

LOC varia de 6 a 22 e complexidade de 4 a 10 entre as soluções de referência —
uma variação relevante, que qualifica "dificuldade comparável" como
aproximada, não uniforme.

**(b) Tempo real observado no tratamento "sem IA"** (`data/trials.csv`,
mediana por kata, N = nº de participantes com trial "sem IA" registrado para
aquele kata até o momento):

| Kata | Tempo mediano sem IA | N | Participantes |
|---|---:|---:|---|
| kata-01 | 1815,1 s (30 min 15 s) | 1 | Marcos |
| kata-02 | 821,6 s | 2 | Marcos, Arthur |
| kata-03 | 982,1 s | 1 | Marcos |
| kata-04 | 629,5 s | 2 | Guilherme, Arthur |
| kata-05 | 263,7 s | 1 | Guilherme |
| kata-06 | 410,6 s | 2 | Guilherme, Arthur |

**Leitura honesta desses números, sem tirar conclusão de RQ (isso é tarefa da
S03):** a amostra por kata é muito pequena (1 ou 2 participantes, nunca os 3,
porque o contrabalanceamento faz cada participante resolver cada kata em só
um dos dois tratamentos) para validar formalmente a equivalência de
dificuldade. Ainda assim, o dado chama atenção: kata-01 levou 1815 s (quase o
time-box inteiro) contra 264–982 s nos demais — a maior discrepância
observada entre os seis katas.

**Hipótese mais provável para a discrepância de kata-01 (registrada aqui, não
confirmada):** kata-01 **não** é a solução de referência mais complexa — pelo
contrário, tem a segunda menor complexidade ciclomática (4.0) e o segundo
menor LOC (14) das seis, empatada com kata-05, que levou só 263,7 s. Ou seja,
a estrutura do enunciado não explica o tempo alto. A explicação mais
parcimoniosa está na ordem de execução: kata-01 foi o **primeiro** trial do
único participante que o resolveu sem IA (Marcos, que fez kata-01 → kata-02 →
kata-03 sem IA, nessa ordem, segundo `data/trials.csv`). Isso é exatamente o
padrão descrito na ameaça "Efeito de aprendizado entre katas" já documentada
em [`docs/experiment_design.md`](experiment_design.md) — o participante
melhora ao longo dos trials pela prática repetida, independentemente do
tratamento. Sob essa hipótese, o tempo alto de kata-01 reflete o custo de ser
o primeiro trial (familiarização com o ambiente, com o formato dos testes,
com o próprio ato de cronometrar), não uma dificuldade estrutural maior do
kata em si.

Esta é uma leitura, não um fato comprovado — não há timestamp de início por
trial que permita confirmar a ordem cronológica real (ver também o "Registro
de desvio de protocolo" em `docs/experiment_design.md`). A recomendação
permanece: registrar essa discrepância e a hipótese acima no Relatório Final,
junto com a mediana e IQR completos que a S03 vai calcular, em vez de tratar
"dificuldade comparável" como validada só porque os enunciados têm estrutura
e contagem de testes parecidas.

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

Validação executada (S01, antes da execução dos trials):

```text
python -m pytest katas/kata_01 katas/kata_02 katas/kata_03 katas/kata_04 katas/kata_05 katas/kata_06 -q
36 passed
```

Os 36 testes correspondem exclusivamente às seis soluções de referência
(`katas/kata_0N/`), usadas apenas para validar o oráculo de cada kata.

**Nota (atualizada em 2026-09-17, após a S02):** a partir da execução dos
trials, `katas/participants/` passou a conter as soluções de cada
participante para cada kata, cada uma com sua própria cópia de
`test_solution.py`. Isso significa que `python -m pytest katas -q` — o
comando literal documentado acima até esta atualização — hoje recolhe
também esses testes e retorna **144 passed** (36 das soluções de referência
+ 108 das soluções dos três participantes, 6 katas × 3 participantes × testes
por kata), não mais 36. O número 36 continua correto para o que ele sempre
mediu (as soluções de referência), mas deixou de ser reproduzível
executando o comando `python -m pytest katas -q` tal como estava escrito.
Para reproduzir especificamente a validação original das soluções de
referência, use o comando acima, restrito aos seis diretórios `katas/kata_0N`.

Os testes cobrem o comportamento funcional e não devem ser considerados parte
do código produzido pelo participante nas métricas de RQ3.