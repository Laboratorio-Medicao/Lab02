<h1 align="center">Relatório de Laboratório</h1>

| | |
|---|---|
| **Curso** | Engenharia de Software |
| **Disciplina** | Laboratório de Experimentação de Software |
| **Turno / Período** | Noite / 6º |
| **Professor(a)** | Danilo Maia |
| **Laboratório** | Lab02 — Impacto do Uso de Assistentes de IA na Resolução de Katas de Programação |
| **Grupo (trio)** | Arthur Luiz Alves Soares · Guilherme de Almeida Rocha Vieira · Marcos Alberto Ferreira Pinto |
| **Link do repositório / GitHub Projects** | https://github.com/Laboratorio-Medicao/Lab02 / https://github.com/orgs/Laboratorio-Medicao/projects/1 |
| **Data de entrega** | *(a preencher)* |

---

## 1. Introdução

O uso de assistentes de inteligência artificial generativa no desenvolvimento de software tem crescido rapidamente, com ferramentas como GitHub Copilot, ChatGPT e Claude sendo adotadas por desenvolvedores para geração de código, debugging e sugestão de abordagens. Apesar da adoção crescente, há escassez de evidências controladas sobre o real impacto dessas ferramentas em dimensões como tempo de resolução, qualidade funcional e estrutura do código produzido.

Este laboratório conduz um experimento controlado para investigar se o uso de um assistente de IA generativa altera o desempenho de estudantes de graduação na resolução de exercícios de programação (*katas*). O experimento adota um design *crossover within-subject* contrabalanceado: cada participante resolve todos os katas, sendo metade com assistente de IA habilitado e metade sem, garantindo que o mesmo indivíduo sirva como seu próprio controle.

O estudo responde às seguintes questões de pesquisa:

- **RQ1.** O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação? *(métrica: tempo até passar nos testes — *time-to-green* — em segundos, censurado no time-box de 35 min)*
- **RQ2.** O uso de assistente de IA reduz a quantidade de defeitos no código produzido? *(métrica: taxa de sucesso nos testes de aceitação e número de testes falhando ao final do trial)*
- **RQ3.** O uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido? *(métricas: complexidade ciclomática média — CC — e percentual de linhas duplicadas, com LOC como métrica de controle e índice de manutenibilidade — MI — como aprofundamento)*

---

## 2. Metodologia

### 2.1 Design experimental

O experimento utiliza um design **crossover within-subject**. Cada um dos três participantes resolve os seis katas individualmente, sob time-box de 35 minutos por trial. A variável independente é a presença ou ausência do assistente de IA durante a resolução. Cada participante realizou metade dos trials com IA e metade sem IA (3 + 3), totalizando 18 trials: 9 com IA e 9 sem IA.

**Atribuição executada** (a que gerou os dados; conferida em `data/trials.csv` e em `docs/experiment_design.md`):

| Participante | Com IA | Sem IA |
|---|---|---|
| Guilherme | kata-01, kata-02, kata-03 | kata-04, kata-05, kata-06 |
| Arthur | kata-01, kata-03, kata-05 | kata-02, kata-04, kata-06 |
| Marcos | kata-04, kata-05, kata-06 | kata-01, kata-02, kata-03 |

**Atribuição planejada na S01** (Issue #3, commit `e9478c3`): Guilherme 1–3 com IA / 4–6 sem IA; Arthur 1–3 sem IA / 4–6 com IA; Marcos 1–3 com IA / 4–6 sem IA.

> **Desvio de protocolo.** A execução divergiu do plano em dois participantes. Arthur passou de blocos para a atribuição alternada, e Marcos teve o bloco invertido; Guilherme seguiu o plano. O motivo registrado (em 2026-09-17, por relato de Marcos em nome dos dois) é que a ordem fechada na S01 se mostrou inviável na prática. Não há confirmação independente de Arthur, nem registro de quando a mudança foi decidida (ver "Registro de desvio de protocolo" em `docs/experiment_design.md`). Consequências:
>
> - No executado, nenhum participante resolveu o mesmo kata nos dois tratamentos.
> - Os katas de cada tratamento não ficaram equilibrados em dificuldade (ver Seção 3.4).
> - `data/trials.csv` não registra data e hora de início dos trials, então a ordem cronológica real de execução não pode ser reconstruída a partir dos dados.

### 2.2 Participantes

O experimento envolve três participantes: Arthur Luiz Alves Soares, Guilherme de Almeida Rocha Vieira e Marcos Alberto Ferreira Pinto, todos estudantes do 6º período do curso de Engenharia de Software, com conhecimento de Python e sem experiência prévia formalizada com os katas utilizados. O assistente de IA definido para os trials com IA é o **Claude Code com o modelo Claude Sonnet 5** (`claude-sonnet-5`, Anthropic), conforme o ambiente fixado em `README.md`. A confirmação individual e registrada de uso desse assistente existe apenas para os três trials com IA de Marcos (autorrelato em `docs/experiment_design.md`); para Arthur e Guilherme não há confirmação equivalente por escrito.

### 2.3 Objetos experimentais (katas)

Foram selecionados seis exercícios autorais, escritos especificamente para este experimento em setembro de 2026, com o objetivo de reduzir o risco de memorização pelo assistente de IA. Os exercícios exigem uma única função principal, utilizam apenas tipos básicos de Python e possuem entre 5 e 7 testes de aceitação cada. No planejamento (S01), a dificuldade foi estimada como equivalente entre os seis. Os dados coletados mostraram, porém, variação relevante de tamanho e complexidade entre os katas; o kata-04, por exemplo, teve a maior CC (ver Seção 3.4).

| ID | Exercício | Testes |
|---|---|---:|
| kata-01 | Faixas de sinal | 5 |
| kata-02 | Inventário de bolsos | 6 |
| kata-03 | Grade de entregas | 7 |
| kata-04 | Marcadores de texto | 6 |
| kata-05 | Rodízio de equipes | 7 |
| kata-06 | Pontuação por vizinhança | 5 |

Os testes de aceitação são fixos e idênticos para todos os participantes, não podendo ser modificados durante o trial. A solução de cada participante é armazenada em `katas/participants/<participante>/kata_XX/solution.py`.

### 2.4 Coleta de dados

Para cada trial são registrados:

- **Tempo (RQ1):** o instrumento previsto é o script `experiment/collection/timer.py`. Ele inicia um cronômetro no início do trial e, no modo `--kata-path`, detecta automaticamente o *green* rodando `pytest` a cada 5 segundos. Trials que atingem o time-box sem sucesso são registrados como censurados, com tempo travado em 35 min. Os registros são salvos em `data/trials.csv`. **Proveniência:** os 12 tempos de Arthur e Marcos têm o formato que o script grava (3 casas decimais). Os 6 tempos de Guilherme têm 1 casa decimal. `TrialRecord.to_row()` (`experiment/collection/timer.py`, l. 123) sempre grava 3 casas, então esse formato não corresponde ao que o script produz. Os tempos de kata-01 a kata-03 foram inseridos diretamente em `data/trials.csv` no commit `0aff185`, cuja mensagem registra uma resolução de conflitos de merge, e não por execução do CLI do cronômetro (verificável com `git show 0aff185 -- data/trials.csv`). Esses tempos são usados como estão, com essa ressalva (Seção 3.2).

- **Defeitos (RQ2):** número de testes falhando e taxa de sucesso ao final do trial, derivados da execução do `pytest` sobre a solução do participante. Como o cronômetro encerra o trial no *green* (todos os testes passando) ou no time-box, um valor abaixo de 100% só pode ocorrer em trial censurado (ver Seção 3.3).

- **Métricas estáticas (RQ3):** coletadas via `experiment/collection/static_metrics.py` sobre o arquivo `solution.py` do participante ao final do trial. São extraídas:
  - **CC** (complexidade ciclomática média por função) via `radon cc`
  - **MI** (índice de manutenibilidade, escala 0–100) via `radon mi`
  - **LOC** (linhas de código) via `radon raw` — usada como variável de controle
  - **Duplicação** (% de linhas duplicadas) via `jscpd`

  Os resultados são acumulados em `data/static_metrics.csv`.

- **Dados qualitativos (bônus):** número de prompts utilizados, tipos de ajuda solicitada (geração de código, debugging, explicação de conceito, sugestão de abordagem) e percepção de produtividade (escala Likert 1–5), registrados interativamente via `register_prompts.py` ao final de cada trial com IA.

### 2.5 Análise estatística

As três RQs foram analisadas da mesma forma: **estatística descritiva** (mediana e IQR por tratamento, outliers pelas cercas de Tukey, sinalizados e mantidos) e **teste de Wilcoxon signed-rank pareado** (within-subject). O Wilcoxon foi escolhido por ser não paramétrico e adequado ao tamanho amostral reduzido.

- **Unidade de pareamento:** o participante (N = 3 pares). Na execução, nenhum participante resolveu o mesmo kata nos dois tratamentos (Seção 2.1), então não existe par participante × kata.
- **Direção do teste:** unilateral na RQ1 e na RQ2 (H1 "reduz"); bilateral na RQ3 (H1 "altera").
- **Nível de significância:** α = 0,05, adotado na análise da S03. Nenhum artefato da S01/S02 fixava um valor.
- **RQ3 — métricas:** CC e duplicação (as métricas da RQ), LOC como controle, CC/LOC (métrica derivada, para separar complexidade de tamanho) e MI como aprofundamento.
- **RQ3 — tamanho de efeito:** correlação bisserial de postos pareada.
- **RQ3 — multiplicidade:** correção de Bonferroni e Benjamini–Hochberg dentro de cada família de testes.
- **RQ3 — sensibilidade:** pareamento por kata (N = 6) e MI recalculado sob convenção única.

- **Mann-Whitney (exploratório):** a Issue #17 também calculou o teste de Mann-Whitney sobre os 9 trials de cada tratamento (`experiment/analysis/rank_sum.py`). Esse teste trata como independentes os trials do mesmo participante, o que o desenho não garante. Por isso é apenas descritivo: não entra na decisão sobre H0 nem nas famílias de correção de multiplicidade.

Os detalhes e as limitações de cada escolha estão na Seção 3.1. Com 3 participantes e 18 trials, os resultados devem ser interpretados com cautela quanto à generalização.

### 2.6 Ameaças à validade

- **Efeito de aprendizado** *(validade interna):* o plano da S01 previa mitigação por contrabalanceamento em blocos opostos entre participantes. Na execução houve desvio de protocolo (Seção 2.1): para Guilherme e Marcos, tratamento e bloco de katas andam juntos, e a mitigação ficou parcial.
- **Desvio de protocolo de contrabalanceamento** *(validade interna):* a atribuição de Arthur e Marcos diverge da fechada na S01, sem registro de quando a mudança foi decidida (Seção 2.1).
- **Memorização pelo assistente de IA** *(validade interna):* mitigado pelo uso de katas autorais com baixa indexação pública.
- **Vazamento de solução entre participantes** *(validade interna):* mitigado pelo isolamento em pastas individuais (`katas/participants/`) e pela orientação de não consultar soluções de colegas antes do próprio trial.
- **Tamanho amostral reduzido** *(conclusão estatística):* 3 participantes limitam o poder estatístico; análise não-paramétrica e interpretação qualitativa complementam os resultados.
- **Generalização limitada** *(validade externa):* os resultados se aplicam ao contexto de estudantes de graduação resolvendo katas em Python com o assistente Claude Code (Claude Sonnet 5).

---

## 3. Resultados

Os números das tabelas e dos testes desta seção são calculados pelos scripts da S03 a partir de `data/trials.csv` e `data/static_metrics.csv`, sem valores fixos no código: `python analyze_rq1_rq2.py` (RQ1 e RQ2, Issue #15, saída completa em [`docs/analysis_rq1_rq2.md`](analysis_rq1_rq2.md)) e `python -m experiment.analysis.rq3` (RQ3, Issue #16, saída completa em [`results/rq3/rq3_summary.md`](../results/rq3/rq3_summary.md)). As Figuras 1 a 8 são geradas por `python generate_figures.py` a partir dessas mesmas análises, em PNG e PDF, em `docs/figures/`. Cada figura responde a uma única pergunta e não traz p-valores, que ficam nas tabelas.

### 3.1 Dados analisados e procedimento estatístico

- **18 trials** (3 participantes × 6 katas, 9 com IA e 9 sem IA). Nenhum foi excluído e **nenhum foi censurado**: todos chegaram ao *green* antes do time-box de 35 min.
- **Estatística descritiva:** mediana e IQR (Q3 − Q1) por tratamento, como pede o enunciado para N pequeno. Média e desvio-padrão não são usados como estatística descritiva. A única média da análise é o resumo por participante da RQ2 (ver abaixo).
- **Outliers:** cercas de Tukey (Q1 − 1,5·IQR e Q3 + 1,5·IQR) calculadas por tratamento. Um outlier é uma observação extrema, não um dado inválido: todos foram **sinalizados e mantidos**, e nenhuma observação foi removida.
- **Teste inferencial:** Wilcoxon signed-rank pareado, com α = 0,05. Nenhum artefato da S01/S02 fixava um α; o valor foi declarado na S03.
- **Unidade de pareamento: o participante (N = 3 pares).** Nenhum participante resolveu o mesmo kata nos dois tratamentos, então não existe par participante × kata. O par de cada participante compara o resumo dos seus 3 trials com IA contra o resumo dos seus 3 trials sem IA: a mediana na RQ1 e na RQ3, e a média na RQ2. A RQ2 usa a média porque, com a mediana, um único trial com testes falhando não alteraria o par.
- **Tamanho de efeito:** o material da disciplina recomenda reportá-lo sempre (Cohen's d, Cliff's δ, A12). Esta análise usa medidas ligadas ao próprio teste pareado:
  - **RQ1:** diferença entre medianas e razão com IA / sem IA. A correlação bisserial de postos não é reportada porque, com as três diferenças no mesmo sinal, ela vale necessariamente ±1 e não informa nada.
  - **RQ3:** correlação bisserial de postos pareada (r_rb). Ela é definida a partir dos postos com sinal do próprio Wilcoxon signed-rank e não depende da aproximação normal com N pequeno (justificativa em `results/rq3/rq3_summary.md`, Seção 11, item 10).
- **Direção do teste:** unilateral na RQ1 e na RQ2, porque as H1 são direcionais ("reduz"); bilateral na RQ3, porque a H1 é "altera".
- **Limite de resolução do teste, que vale para todas as RQs:** com 3 pares não nulos, o menor p que o Wilcoxon exato pode produzir é 1/2³ = **0,125 (unilateral)** ou 2/2³ = **0,25 (bilateral)**. Os dois ficam acima de α = 0,05. Com esta amostra, portanto, o teste não tem resolução suficiente para rejeitar H0, qualquer que seja o tamanho da diferença. Por isso a leitura dos resultados se apoia principalmente na estatística descritiva, e uma H0 não rejeitada aqui **não** é evidência de ausência de efeito.

### 3.2 RQ1 — Tempo até *green*

> **H0:** o uso de assistente de IA não reduz o tempo necessário para resolver uma tarefa de programação. **H1:** reduz.

**Tabela 1 — Tempo até *green* por tratamento (segundos)**

| Tratamento | n | Mediana | Q1 – Q3 | IQR | Mín – Máx | Censurados |
|---|---:|---:|---:|---:|---:|---:|
| Com IA | 9 | 37,6 | 36,8 – 44,3 | 7,5 | 27,6 – 71,8 | 0 |
| Sem IA | 9 | 721,6 | 537,4 – 848,7 | 311,3 | 246,9 – 1815,1 | 0 |

![Figura 1 — RQ1: tempo até green por tratamento](figures/rq1_tempo_por_tratamento.png)

*Figura 1 — Tempo até todos os testes passarem, por tratamento (9 trials cada). A caixa marca o IQR e o traço a mediana (37,6 s e 721,6 s). Cada ponto é um trial. O eixo é logarítmico, com marcas em segundos e minutos, porque os tempos dos dois tratamentos diferem em uma a duas ordens de grandeza. A linha tracejada marca o time-box de 35 min (nenhum trial foi censurado). Os dois outliers de Tukey estão rotulados e foram mantidos.*

**Tabela 2 — Tempo por participante (unidade do teste pareado)**

| Participante | Com IA: mín / mediana / máx (s) | Sem IA: mín / mediana / máx (s) | Diferença das medianas (s) | Com IA / sem IA |
|---|---:|---:|---:|---:|
| Guilherme | 37,6 / 44,3 / 71,8 | 263,7 / 537,4 / 574,3 | −493,1 | 8,2% |
| Arthur | 27,6 / 38,4 / 54,7 | 246,9 / 721,6 / 794,4 | −683,2 | 5,3% |
| Marcos | 36,8 / 36,8 / 36,8 | 848,7 / 982,1 / 1815,1 | −945,3 | 3,7% |

![Figura 2 — RQ1: tempo por participante](figures/rq1_tempo_por_participante.png)

*Figura 2 — Os 6 trials de cada participante: 3 sem IA e 3 com IA, com o número do kata sobre cada ponto e a mediana de cada lado. É a comparação que o Wilcoxon faz (a mediana sem IA contra a mediana com IA de cada participante, N = 3). O subtítulo de cada painel indica a ressalva de proveniência: os tempos de Guilherme estão fora do formato do cronômetro, e os tempos com IA de Marcos são só autorrelato. Os números de kata também mostram o confundimento: cada lado contém katas diferentes.*

**Tamanho de efeito:** a diferença entre as medianas gerais é **−684,0 s**. Por participante, a diferença das medianas vai de −493,1 s a −945,3 s (Tabela 2).

**Teste de hipótese:** Wilcoxon pareado por participante, exato, n = 3 pares: **W = 0,0; p unilateral = 0,125** (p bilateral = 0,250). **H0 não rejeitada** a α = 0,05.

**Outliers:** Guilherme no kata-02 com IA (71,8 s; cerca superior 55,6 s) e Marcos no kata-01 sem IA (1815,1 s; cerca superior 1315,6 s). Os dois foram mantidos. Como o teste usa a mediana de cada participante, nenhum deles muda o par.

**Análise de sensibilidade (descritiva): sem Marcos.** Os três tempos de Marcos com IA (36,781 / 36,824 / 36,757 s) não têm log independente. Excluindo esse participante (6 trials por tratamento, 2 pares), a mediana é 41,4 s com IA contra 555,9 s sem IA, e a separação completa se mantém. Nenhum teste é aplicado: com 2 pares, o menor p unilateral possível seria 1/2² = 0,25. Esta análise só verifica se o padrão descritivo depende de um participante; ela não substitui o resultado principal, que usa os três participantes.

**Discussão estatística.**

- **Evidência descritiva:** os tempos observados foram muito menores no tratamento com IA. A mediana com IA (37,6 s) é cerca de **5%** da mediana sem IA (721,6 s). Houve **separação completa**: o tempo com IA mais lento (71,8 s) ficou abaixo do tempo sem IA mais rápido (246,9 s). A diferença tem a mesma direção nos três participantes, e a mediana com IA de cada um ficou entre 3,7% e 8,2% da sua mediana sem IA.
- **Inferência:** com p unilateral = 0,125, N = 3 pares e α = 0,05, **não foi possível rejeitar H0**. O valor de 0,125 é o menor que o teste pode produzir com 3 pares, então o teste não tem resolução para rejeitar H0 nesta amostra. A conclusão é "H0 não rejeitada", e não "a IA não reduz o tempo". A evidência descritiva aponta na direção de H1, mas não é confirmatória.

Ressalvas que limitam a leitura:

1. **Confundimento de ordem e kata:** para Guilherme e Marcos, que executaram os tratamentos em blocos, tratamento e bloco de katas andam juntos. A ordem cronológica não está registrada nos dados; se ela seguiu a numeração dos katas, tratamento e ordem de execução também estão confundidos.
2. **Resolução do cronômetro:** os tempos com IA (28–72 s) estão na mesma escala da resolução do cronômetro, que verifica o *green* a cada 5 s.
3. **Tempos de Marcos com IA:** são confirmados apenas por autorrelato.
4. **Proveniência dos tempos de Guilherme** (problema distinto do item 3). As 6 linhas têm 1 casa decimal, formato que `TrialRecord.to_row()` não produz (ele grava 3). Os tempos de kata-01 a kata-03 foram inseridos diretamente durante uma resolução de conflito de merge, e não pela execução normal do CLI do cronômetro (Seção 2.4). Esses tempos foram usados como estão, sem alteração, mas não têm o mesmo nível de confiança dos tempos registrados pelo cronômetro. Assim, as ressalvas 3 e 4 atingem 9 dos 18 tempos: 6 de Guilherme e 3 de Marcos. Apenas os 6 tempos de Arthur não têm ressalva de proveniência. A sensibilidade "sem Marcos" acima não trata esta ressalva.

### 3.3 RQ2 — Defeitos (testes de aceitação falhando)

> **H0:** o uso de assistente de IA não reduz a quantidade de defeitos (testes que falham) no código produzido. **H1:** reduz.

**Tabela 3 — Defeitos por tratamento**

| Tratamento | n | Taxa de sucesso — mediana (IQR) | Mín – Máx | Testes falhando — mediana (IQR) | Mín – Máx |
|---|---:|---:|---:|---:|---:|
| Com IA | 9 | 100,0% (0,0) | 100,0 – 100,0 | 0 (0) | 0 – 0 |
| Sem IA | 9 | 100,0% (0,0) | 100,0 – 100,0 | 0 (0) | 0 – 0 |

Por participante, a média da taxa de sucesso foi de 100% e a média de testes falhando foi de 0 nos dois tratamentos, para os três participantes.

**Teste de hipótese:** Wilcoxon pareado por participante (n = 3) **não aplicável** às duas métricas. Todas as diferenças pareadas são exatamente zero, então não há p-valor a reportar e nenhuma correção de multiplicidade se aplica. H0 não é rejeitada, mas não por um resultado do teste: não houve diferença a testar.

![Figura 3 — RQ2: como os trials terminaram](figures/rq2_desfecho_trials.png)

*Figura 3 — Como os 18 trials terminaram: 9 de 9 no green em cada tratamento, e nenhum no time-box (censurado). A figura mostra o mecanismo que impede a RQ2 de ser respondida: a taxa de sucesso só poderia ficar abaixo de 100% num trial encerrado pelo time-box. Ela não mede defeitos e não indica ausência de defeitos. Os valores da métrica estão na Tabela 3.*

**Discussão estatística.** Os 18 trials terminaram com todos os testes passando, então a RQ2 **não tem variância a comparar**. Isso não é evidência de que os tratamentos produzam a mesma quantidade de defeitos: decorre da forma como o protocolo mede defeitos (**efeito de teto**, uma questão de validade de construto). O cronômetro encerra o trial no *green*, isto é, quando todos os testes passam, e por isso uma taxa de sucesso abaixo de 100% só poderia aparecer em um trial censurado. Nenhum trial foi censurado, e com isso a métrica não teve como variar. A RQ2 depende, portanto, da censura da RQ1. Com a métrica coletada, **a RQ2 não pôde ser respondida**. O protocolo de encerramento condicionou o estado final de cada trial à aprovação de todos os testes, e isso eliminou a variação necessária para comparar os tratamentos. Os dados só permitem dizer que, sob os dois tratamentos, todos os participantes chegaram a uma solução que passa nos testes de aceitação dentro do time-box. Isso não mostra que "não houve defeitos": defeitos fora da cobertura dos testes de aceitação não são medidos.

### 3.4 RQ3 — Estrutura do código

> **H0:** o uso de assistente de IA não altera a complexidade ciclomática nem a duplicação do código produzido. **H1:** altera a complexidade ciclomática e/ou a duplicação.

As métricas foram coletadas na S02 com Radon 6.0.1 (CC, MI e LOC) e jscpd 4.0.5 (duplicação), uma observação por trial. Cada `solution.py` tem exatamente uma função, então a CC média do trial é a CC dessa função. **LOC** é o `loc` bruto do Radon, com linhas em branco e comentários, e é reportada como métrica de controle junto de CC e duplicação, como exige o enunciado.

**Tabela 4 — Métricas estáticas por tratamento e teste pareado por participante (bilateral)**

| Métrica | Sem IA — mediana (IQR) | Com IA — mediana (IQR) | Diferença | W | p | r_rb |
|---|---:|---:|---:|---:|---:|---:|
| LOC (linhas) | 21,0 (14,0) | 14,0 (4,0) | −7,0 | 0,0 | 0,25 | −1,00 |
| CC (complexidade ciclomática) | 8,00 (4,00) | 5,00 (2,00) | −3,00 | 0,0 | 0,25 | −1,00 |
| CC/LOC (complexidade por linha) | 0,282 (0,167) | 0,444 (0,115) | +0,162 | 0,0 | 0,25 | +1,00 |
| MI como coletado (0–100) ¹ | 77,93 (14,70) | 80,71 (13,95) | +2,78 | 0,0 | 0,25 | +1,00 |
| MI harmonizado (0–100) — sensibilidade ¹ | 58,85 (5,57) | 63,75 (3,68) | +4,90 | 0,0 | 0,25 | +1,00 |
| Duplicação (% de linhas) | 0,00 (0,00) | 0,00 (0,00) | 0,00 | — | não aplicável | — |

*Diferença = mediana com IA − mediana sem IA, sobre os 9 trials de cada tratamento. W, p e r_rb vêm do Wilcoxon pareado por participante (N = 3 pares). r_rb é a correlação bisserial de postos pareada: com 3 pares, ±1,00 significa apenas que os três pares foram na mesma direção. Na CC, as diferenças pareadas (−3, −2, −2) têm empates em módulo, e o p "exato" é aproximado nesse caso; como os três sinais são iguais, o valor 0,25 não se altera. ¹ As duas linhas de MI usam convenções de cálculo diferentes; ver "Índice de manutenibilidade" abaixo.*

![Figura 4 — RQ3: LOC e CC por tratamento](figures/rq3_loc_cc_por_tratamento.png)

*Figura 4 — Tamanho (LOC) e complexidade ciclomática (CC) por tratamento, com um painel por métrica. A caixa marca o IQR, o traço a mediana (LOC 21 × 14; CC 8 × 5), e cada ponto é um trial. O outlier de LOC (Marcos kata-04 com IA, 25 linhas) está rotulado e foi mantido. A LOC é o `loc` bruto do Radon.*

![Figura 5 — RQ3: LOC e CC por participante](figures/rq3_loc_cc_por_participante.png)

*Figura 5 — A comparação que o Wilcoxon faz (N = 3): uma linha por participante, da mediana sem IA à mediana com IA. Os três pares vão na mesma direção em LOC e em CC, mas cada lado contém katas diferentes. Essa unanimidade, sozinha, não é evidência de efeito (ver "Confundimento" abaixo).*

**Índice de manutenibilidade: duas séries.** O MI aparece em duas séries, que **não devem ser comparadas em nível absoluto**:

- **MI como coletado** — o resultado principal, gravado em `data/static_metrics.csv` na S02 e mantido sem alteração. O coletor grava a média do MI por arquivo `.py` do diretório do trial. Quando os 12 trials de Arthur e Marcos foram medidos, o diretório já continha um `__init__.py` vazio, que pontua MI = 100. Esses 12 valores são, portanto, a média entre o `solution.py` e esse arquivo vazio. Os 6 valores de Guilherme foram medidos antes de o arquivo existir e correspondem ao `solution.py` sozinho. O coletor atual não reproduz esses 6 valores. A série mistura as duas convenções, e por isso a mediana por tratamento (77,93 / 80,71) não é comparável entre participantes. No pareamento por participante, os dois lados de cada par usam a mesma convenção, e o sinal de cada diferença é preservado. **Esta série é a da Tabela 4 (linha "MI como coletado") e do painel esquerdo da Figura 6.**
- **MI harmonizado** — a análise de sensibilidade: o MI do `solution.py` sozinho, recalculado para os 18 trials a partir do código versionado (coluna `mi_source_only` de [`source_integrity_check.csv`](../results/rq3/source_integrity_check.csv)). É uma convenção única para todos, e por isso os valores ficam cerca de 20 pontos abaixo da série como coletada. **É o painel direito da Figura 6.**

**Interpretação:** as duas séries apontam na mesma direção nos três pares (MI maior com IA, r_rb = +1,00, p = 0,25). A diferença de nível entre elas vem da convenção de cálculo, não dos dados. Detalhes em [`data_quality_report.md`](../results/rq3/data_quality_report.md).

![Figura 6 — RQ3: MI por participante nas duas séries](figures/rq3_mi_duas_series.png)

*Figura 6 — MI por participante (mediana dos 3 trials de cada lado), nas duas séries: como coletado (principal, à esquerda) e harmonizado (sensibilidade, à direita). Nas duas, o MI foi maior com IA nos três participantes. Os níveis diferem entre os painéis pela convenção de cálculo; no painel da esquerda, o nível mais baixo de Guilherme vem dessa convenção. Por isso o MI é mostrado pareado, e não como distribuição conjunta dos 18 trials.*

**Normalização por LOC.** CC e LOC têm correlação moderada nos 18 trials (Spearman ρ = 0,63). Por isso foi calculada a razão CC/LOC, para separar "mais complexo porque é maior" de "mais complexo por linha". A CC/LOC é uma **métrica derivada** das duas anteriores, e não uma terceira evidência independente. Ela é sensível à definição de LOC: o `loc` bruto do Radon conta linhas em branco e comentários. Com as linhas de código-fonte sem essas linhas (SLOC, coluna `sloc_recomputed` de `source_integrity_check.csv`), as medianas de CC/SLOC ficam em 0,429 (sem IA) e 0,500 (com IA). A diferença cai de 0,162 para 0,071, para menos da metade. O MI não foi normalizado, porque já incorpora LOC na fórmula. A duplicação/LOC é zero por construção.

![Figura 7 — RQ3: CC × LOC](figures/rq3_cc_vs_loc.png)

*Figura 7 — CC contra LOC nos 18 trials (Spearman ρ = 0,63). A complexidade tende a acompanhar o tamanho, e os trials com IA ficam na região de menos linhas. É uma associação entre trials, não um efeito do tratamento.*

![Figura 8 — RQ3: complexidade ciclomática normalizada por LOC](figures/rq3_cc_normalizada.png)

*Figura 8 — Complexidade ciclomática normalizada por LOC, uma métrica derivada de CC e LOC, com duas definições de linha. À esquerda, CC/LOC com o `loc` bruto (medianas 0,282 × 0,444); à direita, CC/SLOC, só com linhas de código (0,429 × 0,500). A diferença entre os tratamentos cai de 0,162 para 0,071 quando as linhas em branco e os comentários saem do denominador. O outlier (Guilherme kata-03 com IA, 0,857) está rotulado e foi mantido.*

**Outliers (Tukey, por tratamento):** LOC de Marcos no kata-04 com IA (25 linhas; cerca superior 20) e CC/LOC de Guilherme no kata-03 com IA (0,857; cerca superior 0,673). Os dois foram sinalizados e mantidos (ver [`outliers.csv`](../results/rq3/outliers.csv)).

**Multiplicidade.** A RQ3 fez 14 testes. Os 4 de duplicação e duplicação/LOC são degenerados (sem p-valor), e os outros 10 produziram p-valor. Cada **família** de correção é uma unidade de pareamento, com 5 testes cada (LOC, CC, MI como coletado, MI harmonizado e CC/LOC):

- **Participante** (análise primária): todos os p brutos = 0,25; Bonferroni = 1; BH = 0,25.
- **Kata** (sensibilidade): p brutos de 0,03125 a 0,84375; ver abaixo.

Seguindo a orientação do material da disciplina ("Muitos testes? Corrija (Bonferroni / FDR)"), os p-valores brutos foram mantidos e reportados ao lado dos p ajustados por Bonferroni (erro por família) e Benjamini–Hochberg (taxa de falsas descobertas). **Nenhum teste permanece significativo após a correção.** Nenhum p bruto atingiria o limiar de Bonferroni mesmo com os 10 testes numa única família (α = 0,005). Valores completos em [`statistical_tests.csv`](../results/rq3/statistical_tests.csv). Os p do Mann-Whitney (Seção 2.5) são exploratórios, não entram nessas famílias e não são usados em nenhuma decisão.

**Análise de sensibilidade: pareamento por kata (N = 6).** Parear por kata bloqueia a dificuldade da tarefa e baixa o piso de p para 0,031, mas os dois lados de cada par vêm de participantes diferentes. Resultados (p bruto): LOC 0,0625; CC 0,375; MI como coletado 0,844; CC/LOC 0,3125; MI harmonizado 0,03125. O MI harmonizado é o **único p bruto abaixo de α**. O caminho completo desse resultado:

1. **Resultado bruto:** p = 0,03125, com os 6 katas na mesma direção.
2. **Contexto:** 0,03125 = 2/2⁶ é o **menor p bilateral exato possível** com 6 pares. O valor observado é o piso do teste, não um valor que se destaque dentro do intervalo possível.
3. **Correção de multiplicidade:** na família de 5 testes do pareamento por kata, p ajustado = 0,156 por Bonferroni e 0,156 por Benjamini–Hochberg, acima de α. Como o p bruto já está no piso, nenhuma correção com mais de um teste poderia mantê-lo abaixo de 0,05.
4. **Interpretação final:** não significativo. O resultado ainda vem de uma análise secundária, que não é within-subject, e usa o MI harmonizado, não a série como coletada. Ele é mantido visível, mas não altera a conclusão.

**Confundimento entre tratamento e dificuldade do kata.** Como cada lado do par contém katas diferentes, a dificuldade das tarefas entra junto na diferença medida, e a distribuição dos katas entre os tratamentos não ficou equilibrada. A dificuldade de cada kata foi estimada pela sua CC média entre os três participantes ([`task_allocation_balance.csv`](../results/rq3/task_allocation_balance.csv)):

| Participante | Katas com IA | Katas sem IA | Diferença de CC média dos katas (com IA − sem IA) |
|---|---|---|---:|
| Arthur | kata-01, kata-03, kata-05 | kata-02, kata-04, kata-06 | −3,56 |
| Guilherme | kata-01, kata-02, kata-03 | kata-04, kata-05, kata-06 | −0,89 |
| Marcos | kata-04, kata-05, kata-06 | kata-01, kata-02, kata-03 | +0,89 |

- Em **2 dos 3 participantes** (Arthur e Guilherme), os katas do lado com IA eram, em média, menos complexos segundo a CC. Para Marcos, o desequilíbrio vai no sentido oposto.
- Em LOC, Guilherme e Marcos ficam praticamente equilibrados (±0,11).
- O kata-04, o de maior CC média, ficou no lado sem IA para Arthur e Guilherme.

Esse indicador é derivado das próprias medições e absorve parte de um eventual efeito do tratamento. Ele serve para descrever a alocação, não para estimar um efeito de tarefa. Há, portanto, **confundimento entre tarefa (kata) e tratamento**, uma limitação do desenho executado (Seção 2.1) que a análise não corrige. Parte das diferenças observadas pode estar associada à composição dos katas de cada lado. Em particular, o fato de os três pares apontarem na mesma direção em LOC e em CC **não pode ser interpretado isoladamente como evidência do efeito do tratamento**, porque os dois lados de cada par contêm katas diferentes e desequilibrados em dificuldade.

**Discussão estatística.**

- **Evidência descritiva:** o código produzido com IA foi **menor** (mediana de 14 contra 21 linhas), teve **CC absoluta menor** (5 contra 8) e teve **MI maior** nas duas séries de MI. As três direções se repetem nos três participantes. Nesta amostra, o código com IA não foi mais verboso. Com 3 pares e o confundimento com os katas, porém, isso não basta para descartar a preocupação do enunciado de que o código gerado por IA seja mais verboso.
- **CC, LOC e CC/LOC:** não são três evidências independentes. Como o LOC caiu proporcionalmente mais que a CC, a razão CC/LOC ficou maior com IA (0,444 contra 0,282). A diferença cai para menos da metade (0,071) quando as linhas em branco não são contadas. A CC absoluta menor acompanha, em boa parte, o tamanho menor, e não indica um código com lógica mais simples por linha.
- **Inferência:** nenhuma dessas diferenças é estatisticamente significativa. Com 3 pares o p bilateral mínimo é 0,25, nenhum teste sobrevive à correção de multiplicidade, e o confundimento com a dificuldade dos katas impede atribuir a direção observada só ao tratamento.
- **Duplicação:** nenhum bloco duplicado foi detectado em nenhum dos 18 trials. Isso é um valor observado, não prova de que o código não tenha duplicação. Cada trial tem uma única função num único arquivo, e o jscpd exige 5 linhas / 20 tokens repetidos dentro do próprio trial. Nesse arranjo, a métrica não teve oportunidade de variar. A duplicação **não pôde ser avaliada adequadamente** com a estrutura da coleta. Por isso não há figura de duplicação: um gráfico de valor constante sugeriria uma evidência que a coleta não produziu.

**Conclusão da RQ3: H0 não rejeitada.** Os dados não permitem afirmar que o uso de IA alterou a complexidade ciclomática, e a duplicação não foi avaliável com a métrica coletada.

### 3.5 Síntese frente às hipóteses

| RQ | Métrica principal | Com IA × sem IA (medianas) | Teste (pareado por participante, n = 3) | Decisão (α = 0,05) | O que os dados respondem |
|---|---|---|---|---|---|
| RQ1 | Tempo até *green* | 37,6 s × 721,6 s | W = 0,0; p unilateral = 0,125 (piso) | H0 não rejeitada | Descritivamente, tempos muito menores com IA nos três participantes, com separação completa; o teste não tem resolução para confirmar a diferença |
| RQ2 | Taxa de sucesso / testes falhando | 100% × 100% / 0 × 0 | Não aplicável (diferenças nulas) | Teste não aplicável; H0 não rejeitada | **Não respondida:** sem variação por efeito de teto do protocolo de encerramento |
| RQ3 | CC (LOC como controle; CC/LOC derivada; MI como aprofundamento) | CC 5 × 8; LOC 14 × 21; CC/LOC 0,444 × 0,282; MI maior com IA nas duas séries | W = 0,0; p bilateral = 0,25 (piso); nenhum teste significativo após correção | H0 não rejeitada | Descritivamente, código com IA menor, com CC absoluta menor e mais denso por linha; sem significância e com confundimento de kata |
| RQ3 | Duplicação | 0% × 0% | Não aplicável (diferenças nulas) | Teste não aplicável; H0 não rejeitada | **Não avaliável** com a métrica coletada: nenhuma duplicação detectada, e a métrica não teve como variar |

Em nenhuma RQ foi possível rejeitar H0. Nas três, porém, isso reflete limitações do desenho executado, e não evidência de equivalência entre os tratamentos: 3 pares, com piso de p acima de α; efeito de teto na RQ2; ausência de variância na duplicação; e confundimento entre tratamento e kata. A discussão integrada dessas limitações e de suas consequências para a validade do estudo será feita na Seção 4.

### 3.6 Análise exploratória: MI em profundidade e nº de prompts (bônus, Issue #18)

Esta análise é **exploratória e descritiva**. Ela não acrescenta testes de hipótese, porque os testes de MI entre tratamentos já estão na Seção 3.4, com correção de multiplicidade. Foi gerada por `python -m experiment.analysis.mi_prompts`, com saída completa em [`results/mi_prompts/mi_prompts_summary.md`](../results/mi_prompts/mi_prompts_summary.md).

**MI em profundidade.** O Radon calcula o MI a partir de quatro componentes: volume de Halstead (V), complexidade ciclomática (G), linhas lógicas (LLOC, L) e % de linhas de comentário (C). Os componentes foram recalculados do `solution.py` de cada trial, na convenção do MI harmonizado. O MI reconstruído a partir deles confere com essa série nos 18 trials.

| Componente | Sem IA — mediana (IQR) | Com IA — mediana (IQR) | ρ de Spearman com o MI (18 trials) |
|---|---:|---:|---:|
| LLOC (L) | 17 (6) | 12 (5) | −0,91 |
| CC (G) | 8 (4) | 5 (2) | −0,85 |
| Volume de Halstead (V) | 82,04 (42,12) | 62,91 (33,79) | −0,63 |
| Comentários (C) | 0% (0) | 0% (0) | — (constante) |

- Nenhum trial tem comentários, então o termo C da fórmula é constante e não explica nenhuma diferença de MI.
- Nesta amostra, o MI acompanha sobretudo o tamanho lógico e a CC, e parte dessa associação é mecânica, porque esses componentes estão na própria fórmula.
- O MI maior com IA observado na Seção 3.4 corresponde, portanto, ao código com IA ter menos linhas lógicas e menor CC. Como métrica composta, o MI **não acrescenta aqui evidência independente** de LOC e CC, e herda deles o confundimento com os katas.

**Nº de prompts × qualidade do código.** O nº de prompts vem de `data/prompts/prompt_records.csv`, que cobre os 9 trials com IA. O MI usado é o harmonizado, porque a comparação é entre participantes e o MI como coletado não é comparável entre participantes.

| Participante | Nº de prompts | CC (mediana) | MI harmonizado (mediana) | LOC (mediana) |
|---|---:|---:|---:|---:|
| Arthur | 1 | 5 | 63,75 | 13 |
| Guilherme | 1 | 6 | 64,80 | 14 |
| Marcos | 2 | 5 | 61,43 | 15 |

Nos 9 trials com IA, o ρ de Spearman entre o nº de prompts e cada métrica foi −0,05 (CC), −0,18 (MI harmonizado) e 0,37 (LOC). São valores apenas descritivos, sem p-valor, por três motivos:

- O nº de prompts teve só dois valores: 1 para Arthur e Guilherme, 2 para Marcos.
- Ele é **constante dentro de cada participante**, então qualquer associação se confunde com o participante e, como cada um resolveu katas diferentes com IA, também com o kata.
- Os 9 trials não são independentes, porque são 3 por participante.

**Os dados coletados não permitem avaliar se o nº de prompts está associado à qualidade do código.**

![Figura 9 — Bônus: MI harmonizado contra os componentes da fórmula](figures/bonus_mi_componentes.png)

*Figura 9 — MI harmonizado contra LLOC, CC e volume de Halstead, nos 18 trials, com o ρ de Spearman descritivo em cada painel. Os pontos com IA ficam na região de menos linhas e menor CC, e por isso com MI mais alto.*

![Figura 10 — Bônus: nº de prompts × CC e MI](figures/bonus_prompts_qualidade.png)

*Figura 10 — CC e MI harmonizado dos 9 trials com IA, agrupados pelo nº de prompts. O rótulo de cada ponto é a inicial do participante mais o kata. O eixo mostra quem está em cada coluna: a comparação entre colunas também é entre participantes e katas diferentes, e não mede o efeito dos prompts.*

---

## 4. Discussão

### 4.1 Interpretação integrada dos resultados

Os resultados das três RQs apontam na mesma direção: o uso de assistente de IA esteve associado a tempos de resolução muito menores, a código mais compacto e com menor complexidade ciclomática absoluta, e a taxas de sucesso idênticas. Em nenhuma RQ foi possível rejeitar H0 estatisticamente. Essa combinação — efeito descritivo grande, inferência não significativa — não é contraditória: decorre de limitações do desenho executado, que são discutidas a seguir.

**RQ1 — Tempo.** A separação completa entre os tratamentos (o trial com IA mais lento foi mais rápido que o trial sem IA mais rápido) é o resultado descritivo mais robusto do estudo. A diferença de medianas foi de −684 s, e a mesma direção se repetiu nos três participantes. O p unilateral de 0,125 é o menor valor que o Wilcoxon pareado pode produzir com 3 pares, o que significa que o teste simplesmente não tem resolução para confirmar a diferença nesta amostra — não que a diferença seja pequena. A magnitude observada é coerente com a literatura: Copilot e assistentes similares têm sido associados a reduções de tempo da ordem de 50–56% em tarefas de programação controladas (Peng et al., 2023; GitHub, 2022). No presente estudo, a redução foi muito maior (medianas 95% menores com IA), mas katas curtos com solução única são mais suscetíveis a esse efeito do que tarefas de produção.

**RQ2 — Defeitos.** A ausência de variação na taxa de sucesso não é resultado do experimento: é uma consequência direta do protocolo de encerramento. O cronômetro encerra o trial no *green*, isto é, quando todos os testes passam — e, como nenhum trial foi censurado, todos os 18 terminaram com 100% de sucesso. A RQ2 não foi respondida. Para respondê-la seria necessário registrar o estado do código no momento do encerramento pelo time-box, o que exigiria uma modificação no protocolo.

**RQ3 — Estrutura do código.** Os três indicadores descritivos (LOC menor, CC absoluta menor, MI maior com IA) repetiram-se nos três participantes. O resultado mais delicado é a CC/LOC: embora o código com IA tenha sido menor e menos complexo em termos absolutos, a razão CC por linha foi maior (0,444 contra 0,282 com LOC bruto; 0,500 contra 0,429 com SLOC). Isso sugere que o assistente produziu código mais denso — mais lógica por linha — e não necessariamente mais simples. A interpretação é inconclusiva, contudo, porque o confundimento entre tratamento e kata (cada participante resolveu katas diferentes em cada tratamento) impede isolar o efeito do assistente do efeito da dificuldade da tarefa. A duplicação zero em todos os trials decorre da estrutura da coleta (uma função por arquivo, limiares de 5 linhas e 20 tokens), e não de uma característica do código produzido.

### 4.2 Ameaças à validade observadas na execução

As ameaças previstas no desenho (Seção 2.6) se concretizaram em graus distintos durante a execução:

**Efeito de aprendizado** *(validade interna).* O contrabalanceamento entre participantes foi executado, mas de forma diferente do planejado na S01. Guilherme seguiu o bloco original (katas 1–3 com IA, 4–6 sem IA); Arthur passou para alternância (katas 1, 3, 5 com IA; 2, 4, 6 sem IA); Marcos teve o bloco invertido (katas 1–3 sem IA, 4–6 com IA). Esse desvio não invalida a execução, mas enfraquece a garantia de que os efeitos de aprendizado foram distribuídos igualmente, pois a ordem cronológica real de execução não ficou registrada nos dados.

**Memorização pelo assistente de IA** *(validade interna).* Os katas foram elaborados de forma autoral, sem publicação prévia. O risco de memorização foi reduzido, mas não eliminado: o assistente pode ter generalizado padrões de katas similares vistos no treinamento. Essa ameaça não pode ser avaliada com os dados disponíveis.

**Vazamento de solução entre participantes** *(validade interna).* As soluções foram isoladas em diretórios individuais (`katas/participants/`), o que reduziu o risco. Contudo, o commit de Arthur (issue #4) incluiu soluções para todos os 6 katas antes que Guilherme e Marcos tivessem executado seus trials. Os participantes operaram sob orientação de não consultar o código de colegas, mas não há registro de que isso foi verificado.

**Tamanho amostral reduzido** *(conclusão estatística).* Com 3 participantes, o piso de p do Wilcoxon pareado é 0,125 unilateral — acima do α convencional de 0,05. Isso significa que nenhuma diferença, por maior que seja, pode produzir um resultado significativo neste experimento. O tamanho amostral não é uma limitação contornável por escolha de teste: é uma restrição estrutural do desenho.

**Qualidade e proveniência dos dados** *(ameaça não prevista no desenho).* Duas situações comprometeram a confiança em parte dos dados: os tempos com IA de Guilherme (katas 1–3) foram inseridos manualmente durante uma resolução de conflito de merge, sem origem no CLI do cronômetro; e os tempos com IA de Marcos são confirmados apenas por autorrelato. Apenas os 6 tempos de Arthur foram registrados pelo cronômetro sem ressalva de proveniência. Essa ameaça afeta 9 dos 18 trials e é a mais relevante do estudo, pois compromete a variável dependente principal (RQ1).

**Confundimento tratamento–kata** *(ameaça não prevista no desenho).* Como o protocolo executado não atribuiu o mesmo kata aos dois tratamentos para nenhum participante, a dificuldade da tarefa entra como variável de confusão em todas as comparações. Em 2 dos 3 participantes (Arthur e Guilherme), os katas do lado com IA tinham, em média, CC menor — o que pode explicar parte da diferença observada em CC e LOC.

### 4.3 Relação com a literatura e limitações de generalização

Os resultados descritivos de RQ1 são coerentes com estudos que reportam ganhos de produtividade com assistentes de IA em tarefas de programação controladas. Peng et al. (2023) reportaram 55,8% de redução no tempo de conclusão de uma tarefa de implementação de servidor HTTP com GitHub Copilot. O efeito observado neste estudo foi proporcionalmente maior, o que pode refletir a natureza dos katas — tarefas curtas, com solução única e testes de aceitação claros, onde o assistente pode gerar a solução quase diretamente a partir do enunciado.

A generalização é limitada por três fatores: (1) os participantes são estudantes de graduação em ambiente acadêmico controlado, não profissionais em contexto de produção; (2) os katas são tarefas de complexidade reduzida, com domínio bem delimitado, diferentemente de tarefas de manutenção ou de desenvolvimento de novas funcionalidades em bases de código existentes; (3) o assistente utilizado (Claude Sonnet, via Claude Code) pode ter comportamento diferente de outros assistentes, e os resultados não devem ser generalizados para ferramentas distintas.

---

## 5. Conclusão

Este laboratório investigou o impacto do uso de um assistente de IA generativa (Claude Sonnet via Claude Code) na resolução de katas de programação em Python, por meio de um experimento controlado *crossover within-subject* com três participantes e seis katas autorais.

**Em nenhuma das três RQs foi possível rejeitar H0** com α = 0,05. Esse resultado deve ser lido com cautela: ele não é evidência de que o assistente de IA não tem efeito. Ele reflete, sobretudo, as limitações do desenho executado — em especial o tamanho amostral de 3 participantes, que impede qualquer teste pareado de atingir significância estatística, e o confundimento entre tratamento e kata decorrente do desvio de protocolo.

**Descritivamente**, os dados são expressivos:

- Com IA, o tempo mediano de resolução foi de 37,6 s, contra 721,6 s sem IA — uma diferença de mais de 10 vezes, com separação completa entre os tratamentos.
- Com IA, o código produzido foi mais compacto (mediana de 14 contra 21 linhas) e com menor complexidade ciclomática absoluta (5 contra 8), embora mais denso por linha (CC/LOC 0,444 contra 0,282).
- A taxa de sucesso foi de 100% nos dois tratamentos, o que impediu a avaliação de RQ2 por efeito de teto do protocolo.
- Nenhuma duplicação foi detectada em nenhum dos 18 trials, o que também impediu a avaliação desse aspecto de RQ3 com a métrica coletada.

**Para estudos futuros**, as principais recomendações são: (1) aumentar o número de participantes para pelo menos 8–10, de modo a dar ao teste estatístico resolução suficiente; (2) registrar o estado do código no encerramento pelo time-box, separando *green* de censura, para viabilizar a RQ2; (3) garantir que o mesmo participante resolva o mesmo kata nos dois tratamentos (crossover puro), eliminando o confundimento com a dificuldade da tarefa; (4) registrar todos os tempos com o cronômetro padronizado, sem inserção manual.

Apesar das limitações, o experimento cumpriu seu propósito formativo: exercitou a definição de hipóteses, o planejamento experimental, a coleta de dados com instrumentação automática, a análise estatística não-paramétrica e a discussão crítica de ameaças à validade em um contexto real de experimentação em engenharia de software.

---

## Referências

- PENG, S. et al. **The Impact of AI on Developer Productivity: Evidence from GitHub Copilot**. arXiv preprint arXiv:2302.06590, 2023.
- GITHUB. **Research: quantifying GitHub Copilot's impact on developer productivity and happiness**. GitHub Blog, 2022. Disponível em: https://github.blog/2022-09-07-research-quantifying-github-copilots-impact-on-developer-productivity-and-happiness/
- WOHLIN, C. et al. **Experimentation in Software Engineering**. Springer, 2012.
- CONOVER, W. J. **Practical Nonparametric Statistics**. 3. ed. Wiley, 1999.
