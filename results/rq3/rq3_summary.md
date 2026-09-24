# RQ3 — Análise de métricas estáticas

> **RQ3 (texto oficial, `docs/enunciado/lab02.md` linha 25):** O uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?

- **H0 (`docs/experiment_design.md`):** O uso de assistente de IA não altera a complexidade ciclomática nem a duplicação do código produzido.
- **H1:** O uso de assistente de IA altera a complexidade ciclomática e/ou a duplicação do código produzido.
- **Nível de significância adotado nesta análise:** α = 0.05. Nenhum artefato anterior do projeto fixou um α; este valor é uma decisão declarada da S03.

Gerado automaticamente por `python -m experiment.analysis.rq3` a partir de `trials.csv` e `static_metrics.csv`. Todos os números abaixo são calculados a partir dos dados reais — nenhum é fixo no código.

---

## 1. Dados analisados

- 18 trials (3 participantes × 6 katas), nenhum excluído, nenhum censurado.
- Ferramentas da coleta (S02): Radon 6.0.1 para CC, MI e LOC; jscpd 4.0.5 para duplicação.
- Qualidade dos dados, conferência contra o código-fonte e observações extremas: `data_quality_report.md`.

## 2. Unidade de análise e unidade de pareamento

**Unidade de observação: o trial.** Cada uma das 18 linhas é a combinação participante × kata × tratamento, que é o nível em que o tratamento (`with_ai`/`without_ai`) está definido. Os dados não são agregados antes das verificações de qualidade nem da descritiva.

**Níveis de cálculo de cada métrica, verificados no código-fonte:**

- **CC** é calculada pelo Radon por *bloco* (função/método) e o coletor grava a média dos blocos do trial. A conferência linha a linha mostra que todos os 18 trials têm exatamente 1 bloco (uma única função por `solution.py`), logo, **neste conjunto de dados, a média por trial é numericamente igual à CC daquela função** — não há mistura de níveis de agregação entre trials.
- **LOC** é o `loc` bruto do Radon (linhas físicas totais do arquivo, incluindo linhas em branco e comentários), somado sobre os arquivos não-teste do trial. É, portanto, uma medida de *volume de texto*, não de instruções — relevante para interpretar a comparação de verbosidade.
- **MI** é calculado por arquivo e o coletor grava a média por arquivo do trial; ver a ressalva de convenção no relatório de qualidade.
- **Duplicação** é calculada pelo jscpd sobre os arquivos do trial, isoladamente — detecta repetição *dentro* do trial, não entre trials.

**Agregação usada para chegar a uma observação comparável por trial:** nenhuma além da que o próprio coletor já aplica (soma para LOC, média por bloco para CC, média por arquivo para MI). As quatro métricas são, portanto, uma observação por trial cada.

**Unidade de pareamento do Wilcoxon.** O desenho é crossover within-subject, mas nenhum participante resolveu o mesmo kata nos dois tratamentos (verificado: 0 pares participante×kata com os dois tratamentos). Não existe, portanto, par direto linha a linha. Foram usados dois blocos, ambos reportados:

| Pareamento | Papel | N de pares | Justificativa |
| --- | --- | ---: | --- |
| participante (within-subject) | primário | 3 | Cada participante contribui com 3 trials por tratamento; o par é a mediana de cada metade. É o único bloco within-subject disponível e neutraliza diferenças individuais de estilo. |
| kata (bloco de dificuldade) | secundário (sensibilidade) | 6 | Bloqueia pela dificuldade da tarefa — principal determinante de LOC e CC — e oferece 6 blocos. Não é within-subject: os dois lados de cada par vêm de participantes diferentes e as células são desbalanceadas (1 ou 2 trials). |

## 3. Tabela principal

| Métrica | Sem IA — Mediana (IQR) | Com IA — Mediana (IQR) | Diferença | Wilcoxon p | Tamanho de efeito |
| --- | ---: | ---: | ---: | ---: | ---: |
| LOC (linhas) | 21.0 (14.0) | 14.0 (4.0) | -7.0 | 0.25 | r_rb = -1.00 |
| CC (adimensional) | 8.00 (4.00) | 5.00 (2.00) | -3.00 | 0.25 | r_rb = -1.00 |
| MI (0–100) | 77.93 (14.70) | 80.71 (13.95) | +2.78 | 0.25 | r_rb = +1.00 |
| Duplicação (% de linhas) | 0.00 (0.00) | 0.00 (0.00) | +0.00 | n/a (degenerado) | n/a |

Mediana (IQR) calculadas sobre os 9 trials de cada tratamento. A diferença é `mediana com IA − mediana sem IA`. O p-valor e o tamanho de efeito vêm do Wilcoxon pareado por participante (within-subject). Tabela completa (incluindo o pareamento secundário por kata) em `statistical_tests.csv`; descritiva completa com Q1, Q3, mínimo e máximo em `descriptive_statistics.csv`.

## 4. Normalização por LOC

O enunciado (linha 54) exige LOC como controle sempre que complexidade ou duplicação forem reportadas, porque *"código gerado por IA pode ser mais verboso, e complexidade/duplicação sem normalizar por LOC pode enganar"*. A normalização não foi aplicada automaticamente a todas as métricas — cada razão abaixo tem uma justificativa própria, e duas métricas foram deliberadamente **não** normalizadas:

- **CC/LOC — normalizada.** *Por que é necessária:* CC cresce com o número de caminhos de decisão, e um código maior tende a ter mais decisões; observou-se de fato uma correlação de Spearman ρ = 0.63 entre LOC e CC nos 18 trials. *Qual problema controla:* separa "o código é mais complexo porque é maior" de "o código é mais complexo por linha escrita". *Como interpretar:* densidade de decisões por linha física; quanto maior, mais lógica condensada por linha.
- **Duplicação/LOC — calculada, mas não usada para concluir.** O numerador (`duplicated_lines`) é identicamente zero nos 18 trials, então a razão é zero por construção e não acrescenta informação à duplicação bruta. É reportada apenas para deixar registrado que foi verificada.
- **MI — deliberadamente não normalizada.** O Maintainability Index já incorpora LOC na própria fórmula (junto de CC e do volume de Halstead); dividi-lo por LOC contaria o tamanho duas vezes e produziria um número sem interpretação definida.
- **LOC — não normalizada**, por ser ela própria a métrica de controle de tamanho.

| Métrica | Sem IA (mediana) | Com IA (mediana) | Wilcoxon p | Tamanho de efeito | Motivo da normalização |
| --- | ---: | ---: | ---: | ---: | --- |
| CC/LOC (complexidade por linha) | 0.282 | 0.444 | 0.25 | r_rb = +1.00 | Separa verbosidade de densidade de complexidade (exigência de controle por LOC, enunciado linha 54) |
| Linhas duplicadas/LOC (fração de linhas) | 0.000 | 0.000 | n/a (degenerado) | n/a | Numerador identicamente zero — razão degenerada, reportada apenas por completude |

**Os três conceitos, mantidos separados:**

| Conceito | Métrica | Pergunta | Resultado observado |
| --- | --- | --- | --- |
| Tamanho | LOC | O código produzido possui maior volume? | mediana 21.0 → 14.0 (menor com IA); p = 0.25, não rejeita H0 (α = 0.05) |
| Complexidade absoluta | CC | O código produzido possui maior complexidade total? | mediana 8.00 → 5.00 (menor com IA); p = 0.25, não rejeita H0 (α = 0.05) |
| Complexidade relativa | CC/LOC | Considerando o tamanho do código, há maior densidade de complexidade? | mediana 0.282 → 0.444 (maior com IA); p = 0.25, não rejeita H0 (α = 0.05) |

## 5. Gráficos

| Figura | Tipo | Pergunta que responde |
| --- | --- | --- |
| [`fig1_distribuicao_por_tratamento.png`](figures/fig1_distribuicao_por_tratamento.png) | Pontos dos 18 trials + mediana por tratamento | Os dois tratamentos produzem distribuições diferentes em LOC, CC e MI — e onde estão os 18 trials dentro dessas distribuições? |
| [`fig2_comparacao_pareada.png`](figures/fig2_comparacao_pareada.png) | Pares por participante + trials individuais | Dentro de cada participante, em que direção a métrica muda de sem IA para com IA, e sobre quantas observações cada ponto do par se apoia? |
| [`fig3_resultados_por_kata.png`](figures/fig3_resultados_por_kata.png) | Categórico × numérico × grupo (pontos) | Como os valores observados se distribuíram por kata, e quais katas caíram em cada tratamento? |
| [`fig4_cc_vs_loc.png`](figures/fig4_cc_vs_loc.png) | Dispersão | A complexidade acompanha o tamanho do código, e os tratamentos ocupam regiões diferentes desse plano? |
| [`fig5_complexidade_normalizada.png`](figures/fig5_complexidade_normalizada.png) | Pontos dos 18 trials + mediana por tratamento | Controlando o tamanho, a densidade de complexidade difere — e quanto dessa diferença depende de como as linhas são contadas? |

Cada figura responde a uma pergunta que nenhuma outra responde. Formas do catálogo da disciplina que foram deliberadamente **não** usadas:

- **Histograma** — o catálogo indica *"grande volume de dados"* como melhor uso; com 9 trials por tratamento, o boxplot com os pontos individuais mostra mais do que um histograma de poucos bins.
- **Violino** — com 9 observações por grupo a densidade estimada é instável (ver `FONTE_DA_VERDADE_SPRINT_3.md`, Seção 8).
- **Gráfico de duplicação** — a métrica é constante em 0,0% por limitação de escopo da coleta; um gráfico sugeriria uma evidência que a análise não tem. A limitação está descrita na Seção 10.

---

## 6. RQ3 — O uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?

**LOC** — O código produzido possui maior volume?

- *Descritivo:* sem IA mediana 21.0 (14.0), faixa [9.0, 39.0], n = 9; com IA mediana 14.0 (4.0), faixa [7.0, 25.0], n = 9.
- *Diferença entre tratamentos:* menor com IA (diferença de mediana: -7.0 linhas).
- *Teste estatístico:* Wilcoxon signed-rank (bicaudal), pareado por participante (within-subject); N = 3 pares (3 não-nulos).
  - H0: a mediana de LOC é igual nos dois tratamentos
  - H1: a mediana de LOC difere entre os tratamentos
- *p-valor:* W = 0.0, p = 0.25 (método exact); não rejeita H0 (α = 0.05).
- *Tamanho de efeito:* r_rb = -1.00 (os 3 pares apresentaram a mesma direção observada — ver a ressalva de confundimento na Seção 9; com 3 pares não-nulos o coeficiente só pode assumir -1,000, -0,667, -0,333, 0,000, 0,333, 0,667, 1,000, o que limita a resolução dessa medida); Hodges–Lehmann = -7.5 linhas (mediana das diferenças pareadas: -5.0).
- *Interpretação:* Nos trials analisados, a mediana de LOC com IA é 7.0 linhas abaixo da mediana sem IA, o que nesta métrica é o sentido melhor; o teste pareado não rejeita H0 (p = 0.25). Com 3 pares, o menor p bicaudal alcançável pelo teste exato é 0.2500 — acima de α = 0.05, de modo que rejeitar H0 é impossível por construção, independentemente da magnitude da diferença.

**CC** — O código produzido possui maior complexidade total?

- *Descritivo:* sem IA mediana 8.00 (4.00), faixa [4.00, 14.00], n = 9; com IA mediana 5.00 (2.00), faixa [4.00, 10.00], n = 9.
- *Diferença entre tratamentos:* menor com IA (diferença de mediana: -3.00).
- *Teste estatístico:* Wilcoxon signed-rank (bicaudal), pareado por participante (within-subject); N = 3 pares (3 não-nulos).
  - H0: a mediana de CC é igual nos dois tratamentos
  - H1: a mediana de CC difere entre os tratamentos
- *p-valor:* W = 0.0, p = 0.25 (método exact); não rejeita H0 (α = 0.05).
- *Tamanho de efeito:* r_rb = -1.00 (os 3 pares apresentaram a mesma direção observada — ver a ressalva de confundimento na Seção 9; com 3 pares não-nulos o coeficiente só pode assumir -1,000, -0,667, -0,333, 0,000, 0,333, 0,667, 1,000, o que limita a resolução dessa medida); Hodges–Lehmann = -2.25 (mediana das diferenças pareadas: -2.00).
- *Interpretação:* Nos trials analisados, a mediana de CC com IA é 3.00 abaixo da mediana sem IA, o que nesta métrica é o sentido melhor; o teste pareado não rejeita H0 (p = 0.25). Com 3 pares, o menor p bicaudal alcançável pelo teste exato é 0.2500 — acima de α = 0.05, de modo que rejeitar H0 é impossível por construção, independentemente da magnitude da diferença.

**MI** — O código produzido é mais manutenível?

- *Descritivo:* sem IA mediana 77.93 (14.70), faixa [54.19, 81.77], n = 9; com IA mediana 80.71 (13.95), faixa [59.13, 84.45], n = 9.
- *Diferença entre tratamentos:* maior com IA (diferença de mediana: +2.78 pontos de MI).
- *Teste estatístico:* Wilcoxon signed-rank (bicaudal), pareado por participante (within-subject); N = 3 pares (3 não-nulos).
  - H0: a mediana de MI é igual nos dois tratamentos
  - H1: a mediana de MI difere entre os tratamentos
- *p-valor:* W = 0.0, p = 0.25 (método exact); não rejeita H0 (α = 0.05).
- *Tamanho de efeito:* r_rb = +1.00 (os 3 pares apresentaram a mesma direção observada — ver a ressalva de confundimento na Seção 9; com 3 pares não-nulos o coeficiente só pode assumir -1,000, -0,667, -0,333, 0,000, 0,333, 0,667, 1,000, o que limita a resolução dessa medida); Hodges–Lehmann = +3.49 pontos de MI (mediana das diferenças pareadas: 2.45).
- *Interpretação:* Nos trials analisados, a mediana de MI com IA é 2.78 pontos de MI acima da mediana sem IA, o que nesta métrica é o sentido melhor; o teste pareado não rejeita H0 (p = 0.25). Com 3 pares, o menor p bicaudal alcançável pelo teste exato é 0.2500 — acima de α = 0.05, de modo que rejeitar H0 é impossível por construção, independentemente da magnitude da diferença.

**Duplicação** — O código produzido possui mais linhas duplicadas?

- *Descritivo:* sem IA mediana 0.00 (0.00), faixa [0.00, 0.00], n = 9; com IA mediana 0.00 (0.00), faixa [0.00, 0.00], n = 9.
- *Diferença entre tratamentos:* mediana idêntica nos dois tratamentos.
- *Teste estatístico:* Wilcoxon signed-rank (bicaudal), pareado por participante (within-subject); N = 3 pares (0 não-nulos).
  - H0: a mediana de Duplicação é igual nos dois tratamentos
  - H1: a mediana de Duplicação difere entre os tratamentos
- *p-valor:* não aplicável — todas as diferenças pareadas são exatamente zero — a métrica é constante entre os tratamentos e o teste não tem o que ordenar.
- *Tamanho de efeito:* não definido (métrica constante).
- *Interpretação:* Duplicação é constante nos 18 trials, então não há diferença a detectar e o teste não tem o que ordenar. O resultado é uma constatação ('nenhuma duplicação foi detectada sob nenhum dos dois tratamentos'), não uma evidência de equivalência entre os tratamentos — a métrica não teve oportunidade de variar neste arranjo de coleta.

**Métricas normalizadas**

**CC/LOC** — Considerando o tamanho do código, há maior densidade de complexidade?

- *Descritivo:* sem IA mediana 0.282 (0.167), faixa [0.190, 0.583], n = 9; com IA mediana 0.444 (0.115), faixa [0.286, 0.857], n = 9.
- *Diferença entre tratamentos:* maior com IA (diferença de mediana: +0.162 ponto(s) de complexidade por linha).
- *Teste estatístico:* Wilcoxon signed-rank (bicaudal), pareado por participante (within-subject); N = 3 pares (3 não-nulos).
  - H0: a mediana de CC/LOC é igual nos dois tratamentos
  - H1: a mediana de CC/LOC difere entre os tratamentos
- *p-valor:* W = 0.0, p = 0.25 (método exact); não rejeita H0 (α = 0.05).
- *Tamanho de efeito:* r_rb = +1.00 (os 3 pares apresentaram a mesma direção observada — ver a ressalva de confundimento na Seção 9; com 3 pares não-nulos o coeficiente só pode assumir -1,000, -0,667, -0,333, 0,000, 0,333, 0,667, 1,000, o que limita a resolução dessa medida); Hodges–Lehmann = +0.177 ponto(s) de complexidade por linha (mediana das diferenças pareadas: 0.194).
- *Interpretação:* Nos trials analisados, a mediana de CC/LOC com IA é 0.162 ponto(s) de complexidade por linha acima da mediana sem IA, o que nesta métrica é o sentido pior; o teste pareado não rejeita H0 (p = 0.25). Com 3 pares, o menor p bicaudal alcançável pelo teste exato é 0.2500 — acima de α = 0.05, de modo que rejeitar H0 é impossível por construção, independentemente da magnitude da diferença.

## 7. Multiplicidade

Foram realizados **14 testes inferenciais**, dos quais **10 produziram p-valor** (os demais são degenerados: duplicação e duplicação/LOC, constantes nos 18 trials, não têm o que ordenar). Reportar vários p-valores sem correção infla a chance de um falso positivo, e o material da disciplina é explícito quanto a isso (*"Muitos testes? Corrija (Bonferroni / FDR)"*).

**Famílias de inferência.** A família é a **unidade de pareamento**: dentro dela, cada teste responde a uma pergunta diferente (uma métrica) sob o mesmo bloqueio. Corrigir também entre as unidades de pareamento penalizaria duas vezes a mesma pergunta analisada sob bloqueios alternativos.

- **participante (within-subject)** — 5 testes: LOC, CC, MI, MI (harmonizado), CC/LOC.
- **kata (bloco de dificuldade)** — 5 testes: LOC, CC, MI, MI (harmonizado), CC/LOC.

**Métodos aplicados:** Bonferroni (controla o erro por família, FWER) e Benjamini–Hochberg (controla a taxa de falsas descobertas, FDR). Os p-valores brutos **não foram substituídos**: `p_value`, `p_bonferroni` e `p_fdr_bh` convivem em `statistical_tests.csv`.

| Métrica | Família | p bruto | p Bonferroni | p FDR (BH) | Decisão após Bonferroni |
| --- | --- | ---: | ---: | ---: | --- |
| LOC | participante (within-subject) | 0.25 | 1 | 0.25 | não rejeita H0 (α = 0.05, corrigido) |
| CC | participante (within-subject) | 0.25 | 1 | 0.25 | não rejeita H0 (α = 0.05, corrigido) |
| MI | participante (within-subject) | 0.25 | 1 | 0.25 | não rejeita H0 (α = 0.05, corrigido) |
| MI (harmonizado) | participante (within-subject) | 0.25 | 1 | 0.25 | não rejeita H0 (α = 0.05, corrigido) |
| CC/LOC | participante (within-subject) | 0.25 | 1 | 0.25 | não rejeita H0 (α = 0.05, corrigido) |
| LOC | kata (bloco de dificuldade) | 0.0625 | 0.3125 | 0.1562 | não rejeita H0 (α = 0.05, corrigido) |
| CC | kata (bloco de dificuldade) | 0.375 | 1 | 0.4688 | não rejeita H0 (α = 0.05, corrigido) |
| MI | kata (bloco de dificuldade) | 0.8438 | 1 | 0.8438 | não rejeita H0 (α = 0.05, corrigido) |
| MI (harmonizado) | kata (bloco de dificuldade) | 0.03125 | 0.1562 | 0.1562 | não rejeita H0 (α = 0.05, corrigido) |
| CC/LOC | kata (bloco de dificuldade) | 0.3125 | 1 | 0.4688 | não rejeita H0 (α = 0.05, corrigido) |

**Nenhum teste permanece significativo a α = 0.05 após correção**, por nenhum dos dois métodos. Na leitura mais conservadora possível — tratar todos os 10 testes como uma única família — o limiar de Bonferroni seria α = 0.0050, que nenhum p bruto observado atinge. A escolha da definição de família, portanto, não muda nenhuma conclusão.

## 8. Análises secundárias e de sensibilidade

### 8.1 Pareamento secundário por kata (N = 6 blocos)

Bloqueia pela dificuldade da tarefa e tem piso de p de 0,0313, contra 0,2500 do pareamento primário — ou seja, é o único dos dois em que rejeitar H0 a α = 0.05 é aritmeticamente possível. Em troca, **não é within-subject**: os dois lados de cada par vêm de participantes diferentes, e as células são desbalanceadas (1 ou 2 trials por lado).

| Métrica | W | Wilcoxon p | r_rb | Decisão |
| --- | ---: | ---: | ---: | --- |
| LOC (linhas) | 1.0 | 0.0625 | -0.90 | não rejeita H0 (α = 0.05) |
| CC (adimensional) | 5.0 | 0.375 | -0.52 | não rejeita H0 (α = 0.05) |
| MI (0–100) | 9.0 | 0.8438 | +0.14 | não rejeita H0 (α = 0.05) |
| Duplicação (% de linhas) | n/a | n/a (degenerado) | n/a | teste não aplicável |
| CC/LOC (complexidade por linha) | 5.0 | 0.3125 | +0.52 | não rejeita H0 (α = 0.05) |

### 8.2 Sensibilidade do MI: valores históricos × recomputação

Os seis valores de MI de Guilherme em `data/static_metrics.csv` são históricos e **não são reproduzíveis pelo coletor no estado atual do repositório** (ver `data_quality_report.md`). A linha `MI (harmonizado)` recomputa o MI dos 18 trials sob uma convenção única, a partir do código-fonte versionado; **`data/static_metrics.csv` não foi alterado**.

| Pareamento | p — MI como coletado | p — MI harmonizado | r_rb (harmonizado) | Decisão (harmonizado) |
| --- | ---: | ---: | ---: | --- |
| participante (within-subject) | 0.25 | 0.25 | +1.00 | não rejeita H0 (α = 0.05) |
| kata (bloco de dificuldade) | 0.8438 | 0.03125 | +1.00 | rejeita H0 (α = 0.05) |

**Resultado com p bruto abaixo de α apenas na análise secundária:** **MI (harmonizado)** (p = 0.03125, r_rb = +1.00), pareado por kata (bloco de dificuldade) — nos 6 katas, o código produzido com IA teve MI harmonizado maior que o produzido sem IA, sem exceção. O resultado é mantido visível e não foi removido.

**O p = 0,03125 observado na análise secundária não permanece significativo após correção de multiplicidade** (Bonferroni: 0.1562; Benjamini–Hochberg: 0.1562; ver Seção 7).

Registre-se ainda que, **com seis pares, 0,03125 é o menor p bicaudal que o teste exato pode produzir** nessa configuração: é o piso, e não um valor que se destaque dentro do intervalo possível. Como o piso coincide com o próprio p observado, nenhuma correção de multiplicidade poderia ser satisfeita com esse número de pares.

**Como este resultado deve (e não deve) ser lido.** Ele (a) é análise **secundária**; (b) usa **MI harmonizado**, recomputado, e não a métrica gravada na S02; (c) usa **pareamento por kata**, que não é within-subject — cada par compara participantes diferentes, confundindo tratamento com habilidade e estilo individual; (d) **não é a análise primária**, que foi fixada antes de os p-valores serem calculados — trocar a unidade de pareamento depois de ver o resultado seria escolher o teste pelo desfecho; (e) **não deve substituir a conclusão principal**; e (f) **não sobrevive à correção de multiplicidade**. Nada disso indica ausência de efeito: indica que este resultado não sustenta, sozinho, nenhuma afirmação sobre o tratamento. A conclusão da RQ3 permanece a da Seção 10.

## 9. Confundimento entre tratamento e dificuldade dos katas

Três fatos do desenho executado, verificados nos dados e não corrigíveis nesta etapa:

1. **Não existe pareamento participante × kata.** Nenhum participante resolveu o mesmo kata sob os dois tratamentos (verificado: 0 combinações participante × kata com os dois tratamentos).
2. **O pareamento primário é por participante**, por ser o único bloco within-subject disponível.
3. **Logo, cada lado do par contém um conjunto diferente de katas** — e a diferença medida entre os tratamentos carrega, junto, a diferença entre as tarefas resolvidas em cada lado.

Para dimensionar esse desequilíbrio, a dificuldade aparente de um kata foi estimada pela média dos seus valores entre os três participantes, e comparada entre os dois lados de cada par:

| Participante | Katas com IA | Katas sem IA | CC média dos katas — com IA | CC média dos katas — sem IA | Diferença (CC) | Diferença (LOC) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Arthur | kata-01, kata-03, kata-05 | kata-02, kata-04, kata-06 | 5.11 | 8.67 | -3.56 | -7.89 |
| Guilherme | kata-01, kata-02, kata-03 | kata-04, kata-05, kata-06 | 6.44 | 7.33 | -0.89 | +0.11 |
| Marcos | kata-04, kata-05, kata-06 | kata-01, kata-02, kata-03 | 7.33 | 6.44 | +0.89 | -0.11 |

Em **2 dos 3 pares** (Arthur, Guilherme), os katas alocados ao tratamento com IA são, por esse indicador, os menos complexos. O kata-04 — o de maior CC média entre os seis — ficou no lado sem IA de dois dos três participantes.

**Limite do indicador, declarado junto do número:** ele é derivado das próprias medições desta análise, não de uma avaliação independente de dificuldade. Como cada kata aparece sob os dois tratamentos (em participantes diferentes), a média por kata absorve parte de um eventual efeito do tratamento. Serve para **descrever a alocação**, não para estimar um efeito de tarefa isolado. Valores completos em `task_allocation_balance.csv`.

**Consequência para a leitura dos resultados.** A alocação dos katas constitui um possível confundimento entre tratamento e dificuldade da tarefa. A alocação observada não permite separar completamente o efeito do tratamento do efeito da tarefa. Em particular, os três pares apresentaram a mesma direção observada em LOC e em CC — e esse fato permanece verdadeiro —, mas **essa unanimidade não pode ser interpretada isoladamente como consistência do efeito do tratamento**, porque os lados do pareamento contêm katas diferentes e a dificuldade dos katas não está perfeitamente balanceada entre eles.

Este é um traço do experimento tal como foi executado — registrado em `docs/experiment_design.md` como desvio da atribuição fechada na S01 — e **não** um defeito da análise. Corrigi-lo exigiria nova coleta, fora do escopo da S03.

## 10. Conclusão da RQ3

Nos 18 trials analisados: **LOC**: mediana 21.0 sem IA contra 14.0 com IA (-7.0), p = 0.25; **CC**: mediana 8.00 sem IA contra 5.00 com IA (-3.00), p = 0.25; **CC/LOC**: mediana 0.282 sem IA contra 0.444 com IA (+0.162), p = 0.25; **MI**: mediana 77.93 sem IA contra 80.71 com IA (+2.78), p = 0.25.

Nenhum dos testes pareados por participante (within-subject) atingiu significância a α = 0.05, e nenhum teste desta análise permanece significativo após correção de multiplicidade (Seção 7). Com N = 3 pares, o menor p bicaudal que o teste exato pode produzir é 0,2500, acima de α; a não-rejeição de H0 é, portanto, uma **limitação de poder estatístico estrutural do desenho**, e não evidência de que os tratamentos sejam equivalentes.

Soma-se a isso que, em 2 dos 3 pares, os katas alocados ao tratamento com IA são os menos complexos pelo indicador da Seção 9. A alocação dos katas constitui um possível confundimento entre tratamento e dificuldade da tarefa, e a alocação observada não permite separar completamente um efeito do outro.

Sobre a duplicação, que a RQ3 nomeia explicitamente: nenhum bloco duplicado foi detectado sob nenhum dos dois tratamentos, de modo que todas as diferenças pareadas são exatamente zero e o teste não é aplicável (3 pares, 0 não-nulos). O arranjo da coleta — um arquivo com uma única função por trial, e limiar de 5 linhas / 20 tokens repetidos dentro do próprio trial — não dava à métrica oportunidade de variar. Essa metade da RQ3 não pode ser respondida com os dados disponíveis: só é possível constatar a ausência de duplicação detectada.

**Resposta à RQ3, em duas partes:**

- **Complexidade ciclomática.** Os dados disponíveis **não permitem estabelecer que o tratamento com IA alterou a complexidade ciclomática** do código produzido. A análise primária possui apenas três pares — com piso de p de 0,2500, acima de α = 0.05 — e apresenta confundimento entre tratamento e dificuldade dos katas. As diferenças descritivas observadas estão reportadas acima e continuam válidas como descrição da amostra, mas não sustentam uma afirmação sobre o efeito do tratamento.
- **Duplicação.** A duplicação **não pôde ser avaliada adequadamente** devido ao escopo estrutural da coleta. Essa metade da RQ3 permanece sem resposta.

Esta é uma afirmação sobre o que os dados permitem concluir, **não** sobre a ausência de efeito: `p > α` aqui não significa que os tratamentos sejam equivalentes. Os dados **não** autorizam afirmar que a IA produz código melhor ou pior, nem que deixa de alterar a complexidade.

## 11. Limitações desta análise

1. **Poder estatístico.** Com N = 3 pares — pareamento por participante (within-subject) — o menor p bicaudal alcançável é 0,2500. Rejeitar H0 a α = 0.05 é impossível por construção, qualquer que seja a magnitude do efeito. O pareamento secundário por kata (N = 6, piso de p = 0,0313) tem mais poder e está na Seção 7.1, mas não é within-subject e mistura participantes dentro de cada par.
2. **Confundimento entre tratamento e dificuldade dos katas.** Não existe pareamento participante × kata, de modo que cada lado do par contém katas diferentes; o indicador da Seção 9 mostra que a alocação não está balanceada. É um traço do experimento executado, não um defeito da análise.
3. **Duplicação sem variância.** A métrica é 0,0% nos 18 trials por uma razão estrutural da coleta, não por um resultado do tratamento. Ver `data_quality_report.md`.
4. **Multiplicidade.** Vários p-valores são reportados juntos; as correções de Bonferroni e Benjamini–Hochberg estão na Seção 7 e em `statistical_tests.csv`. Nenhum resultado permanece significativo após correção.
5. **Valores históricos de MI não reproduzíveis.** Os seis valores de MI de Guilherme em `data/static_metrics.csv` não são reproduzíveis pelo coletor no estado atual do repositório. A mediana de MI por tratamento está contaminada por isso; no pareamento por participante o sinal de cada diferença é preservado. A análise de sensibilidade está na Seção 8.2 e nas linhas `MI (harmonizado)` de `statistical_tests.csv`.
6. **Ausência de par participante × kata.** O contrabalanceamento executado não repetiu nenhum kata sob os dois tratamentos para o mesmo participante, o que impede o pareamento mais forte possível neste desenho.
7. **α = 0.05 foi definido durante a S03**, não antes da coleta: nenhum artefato de S01/S02 fixava um nível de significância. É, portanto, uma decisão pós-hoc, ainda que declarada.
8. **Pressuposto de simetria não verificado.** A leitura do Wilcoxon signed-rank como diferença de medianas supõe simetria da distribuição das diferenças pareadas; com 3 pares esse pressuposto é inverificável.
9. **LOC inclui linhas em branco e comentários** (métrica `loc` bruta do Radon), e CC/LOC herda essa sensibilidade. A coluna `sloc_recomputed` em `source_integrity_check.csv` permite verificar o efeito dessa escolha sobre a comparação de verbosidade e de densidade.
10. **Tamanho de efeito fora da lista do material da disciplina.** O material nomeia Cohen's d, Cliff's δ e A12; esta análise usa a correlação bisserial de postos para amostras pareadas, por ser a medida definida diretamente a partir dos postos com sinal do próprio signed-rank e por não depender da aproximação normal com N pequeno.
11. **Herdadas da S02** (registradas em `AUDITORIA_SPRINTS_1_2.md`): divergência entre o contrabalanceamento fechado na S01 e o executado — que é a origem do confundimento da Seção 9 — e ressalva de proveniência dos tempos de Guilherme. A segunda não afeta RQ3, que não usa `elapsed_seconds`.
