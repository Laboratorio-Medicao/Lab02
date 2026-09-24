# Bônus S03 — MI em profundidade e nº de prompts (Issue #18)

Gerado por `python -m experiment.analysis.mi_prompts`. Análise **exploratória e descritiva**: nenhum teste de hipótese novo é feito — os testes de MI entre tratamentos estão na RQ3 (`results/rq3/`), com correção de multiplicidade. Os CSVs de `data/` não são alterados.

## Verificações

| Verificação | Resultado | Detalhe |
|---|---|---|
| MI reconstruído dos componentes = MI harmonizado (#16) | ✅ | 18/18 trials; maior diferença 0,0041 |
| Nº de prompts registrado para os trials com IA | ✅ | 9/9 trials com IA têm `n_prompts` |
| Nº de prompts varia dentro de algum participante | ⚠️ | nº de valores distintos de `n_prompts` por participante: Arthur 1, Guilherme 1, Marcos 1 — sem variação interna, o nº de prompts se confunde com o participante |

## 1. MI em profundidade

O Radon calcula o MI como `max(0, (171 − 5,2·ln V − 0,23·G − 16,2·ln L + 50·sen(√(2,4·C))) · 100/171)`, com V = volume de Halstead, G = complexidade ciclomática, L = linhas lógicas (LLOC) e C = % de linhas de comentário. Os componentes foram recalculados do `solution.py` versionado de cada trial — a convenção do **MI harmonizado** da RQ3 — e o MI reconstruído a partir deles confere com essa série (ver verificações).

### 1.1 Componentes por tratamento

| Componente | Unidade | Sem IA — mediana (IQR) | Com IA — mediana (IQR) |
|---|---|---:|---:|
| MI (harmonizado) | 0–100 | 58,85 (5,57) | 63,75 (3,68) |
| Volume de Halstead (V) | bits | 82,04 (42,12) | 62,91 (33,79) |
| LLOC (L) | linhas lógicas | 17,00 (6,00) | 12,00 (5,00) |
| CC (G) | adimensional | 8,00 (4,00) | 5,00 (2,00) |
| Comentários (C) | % de linhas | 0,00 (0,00) | 0,00 (0,00) |

### 1.2 O que move o MI nestes dados

Correlação de Spearman entre o MI harmonizado e cada componente, nos 18 trials (descritiva):

| Componente | ρ com o MI |
|---|---:|
| Volume de Halstead (V) | -0,63 |
| LLOC (L) | -0,91 |
| CC (G) | -0,85 |
| Comentários (C) | — |

- **Comentários:** 0,0% em todos os 18 trials. O termo de comentários da fórmula é constante e não contribui para nenhuma diferença de MI.
- **LLOC:** ρ = -0,91 (associação forte). **CC:** ρ = -0,85 (forte). **Volume de Halstead:** ρ = -0,63 (moderada).
- Parte dessas associações é **mecânica**: V, G e L entram na própria fórmula do MI. A correlação mostra quanto o MI desta amostra é explicado por eles, não uma relação independente.

**Leitura.** Nestes 18 trials, o MI acompanha sobretudo o tamanho lógico e a complexidade ciclomática do código. O MI maior com IA observado na RQ3 corresponde, portanto, ao código com IA ter menos linhas lógicas e menor CC, e não a um aspecto de manutenibilidade que LOC e CC não capturem. Como métrica composta, o MI não acrescenta aqui evidência independente de LOC e CC — e herda deles o confundimento com os katas descrito na RQ3.

## 2. Nº de prompts × qualidade do código (trials com IA)

`n_prompts` vem de `data/prompts/prompt_records.csv` (9 trials com IA). O MI usado é o **harmonizado**: a comparação aqui é entre participantes, e o MI como coletado não é comparável entre participantes.

| Participante | Katas com IA | Nº de prompts | CC (mediana) | MI harmonizado (mediana) | LOC (mediana) |
|---|---|---:|---:|---:|---:|
| Arthur | kata-01, kata-03, kata-05 | 1 | 5,0 | 63,75 | 13 |
| Guilherme | kata-01, kata-02, kata-03 | 1 | 6,0 | 64,80 | 14 |
| Marcos | kata-04, kata-05, kata-06 | 2 | 5,0 | 61,43 | 15 |

Correlação de Spearman entre o nº de prompts e cada métrica, nos 9 trials com IA (descritiva, sem p-valor — ver abaixo):

| Métrica | ρ com o nº de prompts |
|---|---:|
| CC | -0,05 |
| MI (harmonizado) | -0,18 |
| LOC | 0,37 |

**Por que não há teste nem conclusão:**

- O nº de prompts assumiu apenas 2 valores: 1 (Arthur, Guilherme); 2 (Marcos).
- O nº de prompts é **constante dentro de cada participante**. Qualquer associação com CC ou MI é, portanto, indistinguível da diferença entre participantes — estilo, experiência e forma de usar o assistente — e, como cada participante resolveu katas diferentes com IA, também da diferença entre katas.
- Os 9 trials não são independentes: são 3 por participante, com o mesmo nº de prompts.
- O nº de prompts é autorrelatado ao final do trial.

**Leitura.** Os dados coletados **não permitem avaliar** se o nº de prompts está associado à qualidade do código. Os coeficientes acima descrevem a amostra, mas não separam o efeito dos prompts do efeito do participante e do kata.

## Artefatos

| Arquivo | Conteúdo |
|---|---|
| `mi_components.csv` | V, G, L, C e MI reconstruído por trial |
| `mi_components_descriptive.csv` | Mediana, quartis e IQR de cada componente por tratamento |
| `mi_component_correlations.csv` | ρ de Spearman entre o MI harmonizado e cada componente |
| `prompts_quality.csv` | Trials com IA: nº de prompts, percepção de produtividade, CC, MI harmonizado e LOC |
| `prompt_correlations.csv` | ρ de Spearman entre o nº de prompts e CC, MI harmonizado e LOC |

Figuras: `docs/figures/bonus_mi_componentes.png` e `docs/figures/bonus_prompts_qualidade.png` (`python generate_figures.py`).
