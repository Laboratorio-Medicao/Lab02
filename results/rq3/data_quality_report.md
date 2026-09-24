# RQ3 — Relatório de qualidade dos dados

Gerado por `python -m experiment.analysis.rq3`. Nenhum dado bruto foi alterado: os CSVs de `data/` são abertos somente para leitura e nenhuma observação foi removida da análise.

## Contagem de trials

```text
Trials esperados (desenho S01): 18
Trials encontrados:             18
Trials completos (as duas fontes, sem valores ausentes): 18
Trials excluídos:               0
```

Nenhum trial foi excluído: os 18 trials de `data/trials.csv` casam 1-para-1 com as 18 linhas de `data/static_metrics.csv` pela chave (participante, kata, tratamento).

## Verificações executadas

| Verificação | Resultado | Detalhe |
| --- | --- | --- |
| Chaves únicas em trials.csv | ✅ OK | 18 linhas, 0 chave(s) duplicada(s) |
| Chaves únicas em static_metrics.csv | ✅ OK | 18 linhas, 0 chave(s) duplicada(s) |
| Junção trials.csv × static_metrics.csv | ✅ OK | 18 trial(is) com as duas fontes; 0 sem correspondência |
| Total de trials | ✅ OK | esperados 18, encontrados 18 |
| Tratamentos válidos | ✅ OK | valores fora de ('without_ai', 'with_ai'): nenhum |
| Balanceamento within-subject | ✅ OK | Arthur: 3 sem IA / 3 com IA; Guilherme: 3 sem IA / 3 com IA; Marcos: 3 sem IA / 3 com IA |
| Repetição do mesmo kata sob os dois tratamentos | ✅ OK | 0 par(es) participante×kata com os dois tratamentos — 0 é o esperado neste desenho e determina a unidade de pareamento |
| Valores ausentes nas métricas de RQ3 | ✅ OK | loc: 0; cyclomatic_complexity_avg: 0; maintainability_index: 0; duplicated_lines_percent: 0 |
| Valores dentro das faixas possíveis | ✅ OK | nenhum valor impossível ou negativo |
| Métricas com variância | ⚠️ ATENÇÃO | sem variância (valor único nos 18 trials): Duplicação |
| LOC reproduzido a partir do código-fonte | ✅ OK | 18/18 trials reproduzidos |
| CC reproduzida a partir do código-fonte | ✅ OK | 18/18 trials reproduzidos |
| MI reproduzível pelo coletor no estado atual do repositório | ⚠️ ATENÇÃO | 12/18 trials reproduzem o valor gravado; 6 são valores históricos que o coletor não reproduz hoje (os diretórios de trial contêm hoje 18 arquivo(s) .py vazio(s) de pacote, que entram na média por arquivo do MI) |
| Unidade de cálculo da CC uniforme entre os trials | ✅ OK | blocos (funções/métodos) por trial: [1] |

## Achados que exigem interpretação

### Métricas com variância

sem variância (valor único nos 18 trials): Duplicação

`duplicated_lines_percent` vale 0,0 em todos os 18 trials. Não é dado ausente nem erro de coleta: o jscpd 4.0.5 foi executado de fato em cada trial (reproduzido nesta análise) e não encontrou nenhum bloco duplicado. A causa é estrutural — cada trial contém um único arquivo com uma única função, e o limiar configurado na S01 exige ≥ 5 linhas e ≥ 20 tokens repetidos **dentro do próprio trial**. Nesse arranjo, a métrica não tinha como variar. Consequência: qualquer teste sobre duplicação é degenerado, e a parte da RQ3 referente a duplicação não pode ser respondida com poder estatístico — apenas constatada.

### MI reproduzível pelo coletor no estado atual do repositório

12/18 trials reproduzem o valor gravado; 6 são valores históricos que o coletor não reproduz hoje (os diretórios de trial contêm hoje 18 arquivo(s) .py vazio(s) de pacote, que entram na média por arquivo do MI)

**Os seis valores históricos de MI de Guilherme não são reproduzíveis pelo coletor no estado atual do repositório.** Todos os 18 diretórios de trial contêm hoje um `__init__.py` vazio; como o coletor da S02 grava a *média do MI por arquivo* e um arquivo vazio pontua MI = 100, executar o coletor agora sobre os katas de Guilherme produziria valores 18 a 22 pontos acima dos gravados (coluna `mi_collector_today` em `source_integrity_check.csv`). Os valores gravados coincidem com o MI do `solution.py` isolado, o que indica que foram medidos antes de o arquivo de pacote existir no diretório. Caracterizam-se, portanto, como **dados históricos não reproduzíveis no estado atual** — não como uma segunda convenção de coleta em uso. LOC e CC não são afetados (um arquivo vazio não acrescenta linhas nem blocos) e reproduzem 18/18. **Impacto na análise:** o MI *como coletado* não é comparável entre participantes, o que contamina a mediana de MI agregada por tratamento. No pareamento por participante, o **sinal** de cada diferença é preservado (a transformação é monótona e se aplica aos dois lados do mesmo par), mas os postos das diferenças *entre* pares poderiam ser distorcidos — neste conjunto de dados não são, o que é uma coincidência favorável e não uma garantia do método. Os valores históricos **não foram alterados**; o MI harmonizado, recomputado sob convenção única a partir do código-fonte, é reportado como análise de sensibilidade (Seção 8.2 de `rq3_summary.md`).

## Conferência linha a linha contra o código-fonte

Cada linha de `data/static_metrics.csv` foi recalculada a partir do código do próprio trial (mesmos arquivos, mesmo Radon), para confirmar que os números publicados correspondem ao código versionado. Detalhe completo em `source_integrity_check.csv`.

| Participante | Kata | Tratamento | LOC csv/rec. | CC csv/rec. | Blocos | MI csv | MI hoje | Situação do MI |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Arthur | kata-01 | with_ai | 13/13 | 5.0/5.0 | 1 | 81.64 | 81.64 | reproduzível pelo coletor atual |
| Arthur | kata-02 | without_ai | 18/18 | 8.0/8.0 | 1 | 79.42 | 79.42 | reproduzível pelo coletor atual |
| Arthur | kata-03 | with_ai | 14/14 | 7.0/7.0 | 1 | 81.87 | 81.87 | reproduzível pelo coletor atual |
| Arthur | kata-04 | without_ai | 39/39 | 11.0/11.0 | 1 | 76.45 | 76.45 | reproduzível pelo coletor atual |
| Arthur | kata-05 | with_ai | 10/10 | 5.0/5.0 | 1 | 82.55 | 82.55 | reproduzível pelo coletor atual |
| Arthur | kata-06 | without_ai | 18/18 | 5.0/5.0 | 1 | 80.71 | 80.71 | reproduzível pelo coletor atual |
| Guilherme | kata-01 | with_ai | 14/14 | 4.0/4.0 | 1 | 64.80 | 82.40 | histórico — não reproduzível no estado atual |
| Guilherme | kata-02 | with_ai | 14/14 | 8.0/8.0 | 1 | 59.13 | 79.56 | histórico — não reproduzível no estado atual |
| Guilherme | kata-03 | with_ai | 7/7 | 6.0/6.0 | 1 | 67.92 | 83.96 | histórico — não reproduzível no estado atual |
| Guilherme | kata-04 | without_ai | 24/24 | 14.0/14.0 | 1 | 54.19 | 77.10 | histórico — não reproduzível no estado atual |
| Guilherme | kata-05 | without_ai | 9/9 | 4.0/4.0 | 1 | 64.74 | 82.37 | histórico — não reproduzível no estado atual |
| Guilherme | kata-06 | without_ai | 17/17 | 8.0/8.0 | 1 | 56.99 | 78.49 | histórico — não reproduzível no estado atual |
| Marcos | kata-01 | without_ai | 21/21 | 4.0/4.0 | 1 | 81.77 | 81.77 | reproduzível pelo coletor atual |
| Marcos | kata-02 | without_ai | 32/32 | 9.0/9.0 | 1 | 77.93 | 77.93 | reproduzível pelo coletor atual |
| Marcos | kata-03 | without_ai | 34/34 | 7.0/7.0 | 1 | 79.44 | 79.44 | reproduzível pelo coletor atual |
| Marcos | kata-04 | with_ai | 25/25 | 10.0/10.0 | 1 | 77.88 | 77.88 | reproduzível pelo coletor atual |
| Marcos | kata-05 | with_ai | 9/9 | 4.0/4.0 | 1 | 84.45 | 84.45 | reproduzível pelo coletor atual |
| Marcos | kata-06 | with_ai | 15/15 | 5.0/5.0 | 1 | 80.71 | 80.71 | reproduzível pelo coletor atual |

## Observações extremas (critério de Tukey, 1,5 × IQR)

Sinalizadas, **não removidas** — a regra do experimento é não descartar observações (ver `docs/enunciado/lab02.md`, linha 40).

| Métrica | Tratamento | Participante | Kata | Valor | Cerca inferior | Cerca superior | Decisão |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| LOC | with_ai | Marcos | kata-04 | 25 | 4 | 20 | mantido na análise |
| CC/LOC | with_ai | Guilherme | kata-03 | 0.857143 | 0.2115 | 0.6731 | mantido na análise |
