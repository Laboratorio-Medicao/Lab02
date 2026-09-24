# Análise Estatística — RQ1 e RQ2 — Lab02

Gerado por `python analyze_rq1_rq2.py` a partir de `data/trials.csv` (Issue #15).

**Método:** mediana e IQR por tratamento; quartis por `statistics.quantiles(method="inclusive")` (interpolação linear, igual ao padrão do numpy/pandas). Teste confirmatório: Wilcoxon signed-rank pareado por participante (um valor com IA contra um sem IA de cada integrante: a mediana dos tempos na RQ1 e a média dos trials na RQ2), unilateral porque as H1 são direcionais, com α = 0,05. W é a soma dos postos das diferenças positivas (com IA − sem IA), a estatística retornada pelo scipy no teste unilateral.

## RQ1 — Tempo até green

> H0: o uso de assistente de IA não reduz o tempo necessário para resolver uma tarefa de programação. H1: reduz.

### Estatística descritiva por tratamento

| Tratamento | n | Mediana (s) | Q1 – Q3 | IQR | Mín – Máx |
|---|---:|---:|---:|---:|---:|
| Com IA | 9 | 37,6 | 36,8 – 44,3 | 7,5 | 27,6 – 71,8 |
| Sem IA | 9 | 721,6 | 537,4 – 848,7 | 311,3 | 246,9 – 1815,1 |

**Trials censurados** (time-box de 2100 s atingido): Com IA: 0; Sem IA: 0. Trials censurados entram na análise com o tempo travado no time-box — nunca são descartados. Como o tempo real seria ao menos o time-box e não há censura no tratamento com IA, travar o tempo só pode subestimar o tempo sem IA: o tratamento é conservador quanto a H1.

**Separação completa:** todos os tempos com IA (máx. 71,8 s) ficaram abaixo de todos os tempos sem IA (mín. 246,9 s).

### Por participante (unidade do teste pareado)

Com n = 3 trials por célula, o IQR diz pouco; por isso são mostrados mínimo, mediana e máximo.

| Participante | Com IA: mín / mediana / máx (s) | Sem IA: mín / mediana / máx (s) | Diferença das medianas (s) | Com IA / sem IA |
|---|---:|---:|---:|---:|
| Guilherme | 37,6 / 44,3 / 71,8 | 263,7 / 537,4 / 574,3 | -493,1 | 8,2% |
| Arthur | 27,6 / 38,4 / 54,7 | 246,9 / 721,6 / 794,4 | -683,2 | 5,3% |
| Marcos | 36,8 / 36,8 / 36,8 | 848,7 / 982,1 / 1815,1 | -945,3 | 3,7% |

**Tamanho de efeito:** diferença entre as medianas gerais = -684,0 s. A correlação rank-biserial não é reportada: com todas as diferenças no mesmo sinal ela vale ±1 e não informa nada.

### Teste de hipótese

- **Wilcoxon pareado por participante (n = 3), método exato:** W = 0,0; p unilateral (H1: com IA < sem IA) = 0,125; p bilateral = 0,250; α = 0,05.
- **Conclusão:** **H0 não rejeitada** (p unilateral = 0,125 ≥ α = 0,05). Com 3 par(es) com diferença não nula, o menor p possível é 1/2^3 = 0,125, maior que α: o teste não tem poder para rejeitar H0 nesta amostra, por maior que seja o efeito. A não rejeição **não** é evidência de ausência de efeito.

### Por kata (exploratório — não pareado)

Cada kata foi resolvido por participantes diferentes em cada tratamento (2 trials de um tratamento contra 1 do outro), e os katas reutilizam os mesmos 3 participantes — as observações não são pareadas nem independentes. A tabela é apenas descritiva; nenhum teste nem decisão sobre H0 é feito sobre ela.

| Kata | Com IA (s) | Sem IA (s) | Mediana com IA | Mediana sem IA |
|---|---|---|---:|---:|
| kata-01 | Guilherme: 44,3, Arthur: 54,7 | Marcos: 1815,1 | 49,5 | 1815,1 |
| kata-02 | Guilherme: 71,8 | Marcos: 848,7, Arthur: 794,4 | 71,8 | 821,6 |
| kata-03 | Guilherme: 37,6, Arthur: 38,4 | Marcos: 982,1 | 38,0 | 982,1 |
| kata-04 | Marcos: 36,8 | Guilherme: 537,4, Arthur: 721,6 | 36,8 | 629,5 |
| kata-05 | Marcos: 36,8, Arthur: 27,6 | Guilherme: 263,7 | 32,2 | 263,7 |
| kata-06 | Marcos: 36,8 | Guilherme: 574,3, Arthur: 246,9 | 36,8 | 410,6 |

### Outliers (cercas de Tukey)

Cercas Q1 − 1,5·IQR e Q3 + 1,5·IQR, calculadas sobre todos os trials de cada tratamento. Os outliers são **sinalizados e mantidos**: o teste usa a mediana de cada participante, que é pouco sensível a um valor extremo.

| Tratamento | Cerca inferior (s) | Cerca superior (s) | Outliers |
|---|---:|---:|---|
| Com IA | 25,5 | 55,6 | Guilherme kata-02 (71,8 s) |
| Sem IA | 70,5 | 1315,6 | Marcos kata-01 (1815,1 s) |

### Robustez: sem Marcos (descritivo)

Os trials com IA de Marcos (36,781 / 36,824 / 36,757 s) não têm log independente de execução (ver ressalvas). Excluindo esse participante:

| Tratamento | n | Mediana (s) | Q1 – Q3 | IQR | Mín – Máx |
|---|---:|---:|---:|---:|---:|
| Com IA | 6 | 41,4 | 37,8 – 52,1 | 14,3 | 27,6 – 71,8 |
| Sem IA | 6 | 555,9 | 332,1 – 684,8 | 352,7 | 246,9 – 794,4 |

Sem esse participante, todos os tempos com IA ficam abaixo de todos os tempos sem IA. Nenhum teste é aplicado: com 2 participante(s) o menor p possível seria 0,250.

## RQ2 — Defeitos (testes de aceitação falhando)

> H0: o uso de assistente de IA não reduz a quantidade de defeitos (testes que falham) no código produzido. H1: reduz.

### Taxa de sucesso (% de testes passando ao final do trial)

| Tratamento | n | Mediana (%) | Q1 – Q3 | IQR | Mín – Máx |
|---|---:|---:|---:|---:|---:|
| Com IA | 9 | 100,0 | 100,0 – 100,0 | 0,0 | 100,0 – 100,0 |
| Sem IA | 9 | 100,0 | 100,0 – 100,0 | 0,0 | 100,0 – 100,0 |

### Nº de testes falhando ao final do trial

| Tratamento | n | Mediana (testes) | Q1 – Q3 | IQR | Mín – Máx |
|---|---:|---:|---:|---:|---:|
| Com IA | 9 | 0 | 0 – 0 | 0 | 0 – 0 |
| Sem IA | 9 | 0 | 0 – 0 | 0 | 0 – 0 |

### Por participante (unidade do teste pareado)

Na RQ2 o par de cada participante usa a **média** dos seus trials em cada tratamento, e não a mediana: com a mediana, um único trial com testes falhando não alteraria o par.

| Participante | Taxa de sucesso média com IA (%) | sem IA (%) | Testes falhando (média/trial) com IA | sem IA |
|---|---:|---:|---:|---:|
| Guilherme | 100,0 | 100,0 | 0,00 | 0,00 |
| Arthur | 100,0 | 100,0 | 0,00 | 0,00 |
| Marcos | 100,0 | 100,0 | 0,00 | 0,00 |

### Teste de hipótese

**Taxa de sucesso:**

- **Wilcoxon pareado por participante (n = 3):** não aplicável — as médias por participante não diferem entre os tratamentos (todas as diferenças são zero). Não há p-valor a reportar.
- **Conclusão:** **H0 não rejeitada** — as médias por participante são iguais nos dois tratamentos; não há diferença pareada para testar.

**Testes falhando:**

- **Wilcoxon pareado por participante (n = 3):** não aplicável — as médias por participante não diferem entre os tratamentos (todas as diferenças são zero). Não há p-valor a reportar.
- **Conclusão:** **H0 não rejeitada** — as médias por participante são iguais nos dois tratamentos; não há diferença pareada para testar.

Como nenhuma das duas métricas de RQ2 chegou a ser testada, não há correção para comparações múltiplas a aplicar.

**Efeito de teto (validade de construto):** o cronômetro encerra o trial no green, isto é, quando todos os testes passam. Uma taxa de sucesso abaixo de 100% só pode aparecer em um trial censurado, então a RQ2 não é independente da censura da RQ1. Como nenhum trial foi censurado, a RQ2 não tem variação possível nesta coleta.

## Ressalvas

- **Desvio de contrabalanceamento:** Arthur e Marcos executaram uma ordem de tratamentos diferente da fechada na S01 (ver `docs/experiment_design.md`, "Registro de desvio de protocolo").
- **Tempos com IA de Marcos** (36,781 / 36,824 / 36,757 s, amplitude de 0,067 s): confirmados apenas por autorrelato, sem log independente.
- **Resolução do cronômetro:** com `--kata-path`, o green é verificado a cada 5 s (padrão), uma resolução próxima da escala dos tempos com IA (28–72 s).
- **Confusão tratamento × kata × ordem:** Guilherme e Marcos fizeram os tratamentos em blocos, então para eles tratamento, kata e ordem de execução andam juntos.
- **Leitura do CSV:** os valores de `data/trials.csv` são lidos numericamente, não como texto, porque nem todas as linhas precisam seguir o formato exato de `TrialRecord.to_row` (número de casas decimais).
- **Tamanho amostral:** com 3 participantes, o teste pareado não tem poder para rejeitar H0 a α = 0,05; os resultados devem ser lidos principalmente pela estatística descritiva.
