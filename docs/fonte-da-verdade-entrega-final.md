# LAB02 — Fonte da Verdade da Entrega Final

> Auditoria realizada em **2026-09-24** sobre `main` @ `fab7915` (igual a `origin/main`).
>
> **Etapa de correção técnica/documental concluída em 2026-09-24 (não commitada).** As Seções 4–20 registram o estado encontrado na auditoria; o que foi corrigido depois, e o que ainda depende de ação posterior, está na **Seção 24**. O checklist da Seção 21 já reflete o estado atual.
> Nenhum código, dado ou relatório foi alterado durante esta auditoria. As reexecuções foram feitas numa cópia descartável do repositório.

---

## 1. Objetivo deste documento

Este documento é a referência interna do grupo para responder:

> **"O que precisa existir no projeto final para que o LAB02 esteja completo, coerente com o enunciado e sem furos?"**

Cada item abaixo tem evidência verificável: arquivo, commit, Issue ou comando reexecutado. Quando não há evidência, o item aparece como ⚠️ ou ❌. Uma afirmação feita na documentação não conta como evidência.

**Legenda de status**

| Status | Significado |
|---|---|
| ✅ OK | Evidência suficiente e coerente |
| ⚠️ PARCIAL | Existe, mas falta completar ou comprovar |
| ❌ AUSENTE | Não foi encontrada evidência |
| 🔴 INCONSISTENTE | Existe, mas contradiz outra evidência |

**Legenda de exigência**

| Sigla | Significado |
|---|---|
| **EXIG** | Exigido pelo enunciado (`docs/enunciado/lab02.md`) |
| **REC** | Recomendado pelo enunciado |
| **CONS** | Necessário para a consistência do próprio experimento (o grupo prometeu ou depende disso) |
| **OPC** | Opcional ou melhoria |

---

## 2. Escopo da entrega final

| Entregável | Pontos | Fonte |
|---|---:|---|
| Lab02S01: desenho e preparação (Passos 1–2) + cartões no Kanban | 5 | enunciado, "Sprints e Pontuação" |
| Lab02S02: execução e coleta (Passo 3) | 5 | idem |
| Lab02S03: análise (Passo 4, RQ1–RQ3) + dashboard (Passo 6) | 5 | idem |
| Relatório Final (Passo 5) | 5 | idem |
| Transversal: GitHub Projects, Issues com Assignee e commits referenciando Issues | desconto até 10% por sprint; parcela individual zerada se faltar commit | enunciado, "Processo" e "Observações" |

---

## 3. Enunciado e requisitos oficiais

| ID | Requisito | Origem no enunciado | Exigência |
|---|---|---|---|
| E1 | Hipóteses nula e alternativa | Passo 1 (A) | EXIG |
| E2 | Variáveis dependentes e independente | Passo 1 (B)(C) | EXIG |
| E3 | Tratamentos | Passo 1 (D) | EXIG |
| E4 | 4 ou 6 katas de dificuldade equivalente, com testes automatizados | Passo 1 (E), Passo 2 | EXIG |
| E5 | Desenho crossover within-subject contrabalanceado | Passo 1 (F) | REC |
| E6 | Quantidade de medições | Passo 1 (G) | EXIG |
| E7 | Ameaças: aprendizado, familiaridade com IA, vazamento, memorização | Passo 1 (H) | EXIG |
| E8 | Katas pouco indexados ou autorais | Passo 1 (H), Passo 2 | REC |
| E9 | Ambiente fixado: linguagem, IDE, assistente, cronômetro, scripts de métricas | Passo 2 | EXIG |
| E10 | O mesmo assistente de IA em todos os trials | Passo 2 | EXIG |
| E11 | Métricas escolhidas e justificadas no desenho **e** no relatório | GQM | EXIG |
| E12 | Metade dos katas com IA e metade sem, em ordem contrabalanceada | Passo 3 | EXIG |
| E13 | Time-box de 35 min (pode ser reduzido, nunca aumentado) | Passo 3 | EXIG |
| E14 | Registrar tempo, testes passando e métricas estáticas por trial | Passo 3 | EXIG |
| E15 | Trial censurado registrado em 35 min, não descartado | RQ1 | REC (tratado como EXIG pelo próprio desenho) |
| E16 | Mediana e IQR em vez de média e desvio-padrão | GQM, "Robustez" | REC |
| E17 | Outliers identificados e Wilcoxon pareado | Passo 4 | EXIG |
| E18 | LOC sempre que reportar complexidade ou duplicação | RQ3 | EXIG |
| E19 | MI | RQ3 | OPC |
| E20 | Nº de prompts | RQ1 | OPC |
| E21 | Relatório (i): introdução **com as hipóteses** | Passo 5 | EXIG |
| E22 | Relatório (ii): metodologia reprodutível com ambiente, katas, **assistente e versão** | Passo 5 | EXIG |
| E23 | Relatório (iii): resultados por RQ com as respostas estatísticas | Passo 5 | EXIG |
| E24 | Relatório (iv): discussão final | Passo 5 | EXIG |
| E25 | Relatório (v): link do repositório e do GitHub Projects | Passo 5 | EXIG |
| E26 | Dashboard: gráficos Pandas + Matplotlib/Seaborn de tempo, taxa de sucesso e métricas estáticas | Passo 6 | EXIG |
| E27 | Em S01, S02 e S03, cada integrante é Assignee de ≥ 1 Issue com artefato de código commitado | Processo | EXIG (a falta zera a parcela individual) |
| E28 | Trials como Issues individuais, **uma por kata/tratamento**, com Assignee | Observações | EXIG |
| E29 | Commits referenciam o número da Issue | Observações | EXIG |
| E30 | Kanban: WIP, Assignee, cartões atualizados, evolução semanal | Observações | EXIG (desconto de até 10%) |
| E31 | Cartões do desenho e da preparação no Kanban | S01 | EXIG |

---

## 4. Estado atual geral

**O núcleo técnico está sólido.** Os 18 trials existem e estão consistentes. As três análises (RQ1/RQ2, RQ3 e bônus) e as figuras **se reproduzem byte a byte**: reexecutei tudo numa cópia limpa e o `git diff` saiu vazio. Os **336 testes passam**. O relatório tem todas as seções, e os números dele batem com os CSVs de resultado.

**Os problemas estão na periferia, e alguns podem custar nota diretamente:**

1. **Guilherme não tem commit em nenhuma Issue da S03.** Pela regra do enunciado, isso zera a parcela individual dele nessa sprint (§12).
2. **O board está desatualizado.** #15, #17, #18 e #21 continuam abertas com o trabalho já mergeado; #10 foi fechada antes de os dados existirem; o snapshot da S03 (#27) não foi feito (§11).
3. **A história do `main` foi reescrita.** Todos os hashes citados no relatório e no desenho (`e9478c3`, `0aff185`, `c826baa`, `805bb72` …) **não existem no `main`** (§9.3).
4. **Soluções de referência dos 6 katas** foram commitadas por Arthur em 07/09 (Issue #4), antes de qualquer trial. O relatório afirma que os participantes não tinham experiência prévia com os katas (§7.4).
5. **Itens do relatório exigidos pelo enunciado estão faltando:** hipóteses na introdução, a ameaça "familiaridade com IA", a divergência do modelo de Issues e a data de entrega (§13).
6. **Armadilha de reprodutibilidade:** `python generate_design_report.py`, comando documentado no README, **apaga 120 linhas** de `docs/experiment_design.md`, inclusive o registro do desvio de protocolo (§10).

---

## 5. Inventário de artefatos

Estrutura real (214 arquivos versionados; `node_modules/`, `.venv/` e `.pytest_cache/` são ignorados):

| Artefato | Existe? | Conteúdo válido? | Usado? | Evidência |
|---|---|---|---|---|
| `docs/enunciado/lab02.md` | ✅ | ✅ | Referência | commit `19fd9b5` |
| `docs/experiment_design.md` | ✅ | ⚠️ tem seções manuais que o gerador apaga | Sim | §10 |
| `docs/katas.md` | ✅ | 🔴 contagens de testes erradas | Sim | §6.4 |
| `docs/relatorio.md` | ✅ | ⚠️ ver §13 | Entrega | 402 linhas |
| `docs/analysis_rq1_rq2.md` | ✅ | ✅ reprodutível | Sim | `python analyze_rq1_rq2.py` sem diff |
| `docs/figures/*.png\|pdf` (10 figuras) | ✅ | ✅ reprodutíveis | Sim (Figuras 1–10 do relatório) | `python generate_figures.py` sem diff |
| `results/rq3/*` (CSVs, 2 `.md`, 5 figuras) | ✅ | ✅ reprodutíveis | CSVs e `.md` sim; **as 5 figuras não são usadas no relatório** | `python -m experiment.analysis.rq3` sem diff |
| `results/mi_prompts/*` | ✅ | ✅ reprodutíveis | Sim (Seção 3.6) | `python -m experiment.analysis.mi_prompts` sem diff |
| `data/trials.csv` | ✅ 18 linhas | ✅ (proveniência ⚠️) | Sim | §7 |
| `data/static_metrics.csv` | ✅ 18 linhas | ⚠️ MI com duas convenções | Sim | §8.3 |
| `data/prompts/prompt_records.csv` | ✅ 12 linhas (9 com IA + 3 sem IA de Arthur) | ⚠️ parte é autorrelato retroativo | Sim (bônus) | §7.4 |
| `data/participant_ai_familiarity.csv` | ✅ 3 linhas | ⚠️ 2 de 3 relatadas por terceiro | **Não** (ausente do relatório) | §13 |
| `data/kanban-snapshots/` (09-10, 09-17) | ✅ | ✅ | Evidência de Kanban | falta a da S03 |
| `katas/kata_0N/` (enunciado, testes e **solução de referência**) | ✅ | ✅ 36 testes | Oráculo | commit `6f79179` (#4) |
| `katas/participants/<p>/kata_0N/` (18 soluções) | ✅ | ✅ todas passam; `test_solution.py` idêntico ao oráculo (18/18) | Sim | `cmp` com as referências |
| `experiment/collection/` (timer, static_metrics, duplication, prompts) | ✅ | ✅ testado | Sim (S02) | `tests/` |
| `experiment/config/` + `generate_design_report.py` | ✅ | 🔴 o gerador sobrescreve o desenho | Parcial | §10 |
| `experiment/analysis/` | ✅ | ✅ | Sim | §10 |
| `experiment/visualization/report_figures.py` | ✅ | ✅ | Sim (figuras do relatório) | `generate_figures.py` |
| `experiment/visualization/boxplots.py` | ✅ | — | **Só nos testes** (código morto no pipeline) | grep: importado só por `tests/test_figures.py` |
| `experiment/visualization/rq3_figures.py` | ✅ | ✅ | Gera `results/rq3/figures` (redundante) | `rq3.py:55` |
| `kanban/` + `generate_kanban_snapshot.py` | ✅ | ✅ | Snapshots | #25 |
| `tests/` (13 arquivos) | ✅ | ✅ 336 passed | Sim | `pytest` |
| `requirements.txt`, `package.json`, `package-lock.json` | ✅ | ⚠️ versão de Python não fixada | Sim | §10.2 |
| `GRAFICOS_CONCEITOS.md` (não versionado) | local | — | Não | material de apoio |
| `trab-final-pdf (1).pdf` (não versionado) | local | — | Não | **slides de outro grupo; não versionar** |
| Branch local `backup/main-antes-rewrite` | local | — | — | prova da reescrita da história (§9.3) |

---

## 6. S01 — Desenho e Preparação

### 6.1 Requisitos
E1–E11 e E31 (ver §3).

### 6.2 Evidências

| Elemento | Evidência |
|---|---|
| H0/H1 para RQ1–RQ3 | `docs/experiment_design.md` §Hipóteses; `experiment/domain/hypothesis.py`; commit `906bafc` (#3) |
| VI, VDs e controle (LOC) | `docs/experiment_design.md` §Variáveis; MI justificado como opcional |
| Tratamentos `with_ai` / `without_ai` | `experiment/domain/enums.py`; CSVs |
| 6 katas autorais com 5/6/7/6/7/5 testes (36 no total) | `katas/kata_0N/test_solution.py`; `pytest --collect-only` reexecutado |
| Desenho crossover contrabalanceado (plano) | commit `906bafc` (antigo `e9478c3`): Guilherme 1–3 com IA; Arthur 1–3 sem IA; Marcos 1–3 com IA |
| Medições: 3 × 6 = 18 | `docs/experiment_design.md` §Protocolo |
| Ameaças (aprendizado, familiaridade, memorização, vazamento, amostra, generalização) | `docs/experiment_design.md` §Ameaças |
| Ambiente | README: Python "3.10+", VS Code, Claude Code / Claude Sonnet 5, Radon 6.0.1, jscpd 4.0.5, pytest 9.1.1 |
| Cronômetro e métricas | `experiment/collection/timer.py`, `static_metrics.py`, `duplication_metrics.py` (#5, #6, #35) |
| Cartões no Kanban | snapshot `kanban-snapshot-2026-09-10.csv`: #1–#6, #24, #25 e #35 em Done |

### 6.3 Status

| Item | Status |
|---|---|
| Hipóteses, variáveis, tratamentos, medições | ✅ |
| 6 katas com testes | ✅ |
| Dificuldade equivalente | ⚠️ só estimada; o piloto prometido em `docs/katas.md` não foi feito; a CC das referências vai de 4 a 10 |
| Baixa indexação comprovada | ❌ `docs/katas.md` promete "registrar a data e anexar os resultados [da busca] ao relatório final", e isso não existe |
| Ameaças do enunciado (H) | ✅ no desenho |
| Versões do ambiente | ⚠️ Python "3.10+" (o `.venv` atual é 3.14.5; a versão usada na S02 não está registrada); versão do Claude Code não registrada |
| Scripts de medição | ✅ |

### 6.4 Problemas

- 🔴 **`docs/katas.md` contradiz os testes reais.** O texto diz que os katas têm "entre 5 e 6 testes", mas kata-03 e kata-05 têm 7. A tabela "(a)" registra kata-05 = 5 e kata-06 = 6, quando o real é **7 e 5**. O relatório (Seção 2.3) traz os valores corretos.
- ⚠️ `docs/katas.md` afirma que Marcos fez "kata-01 → kata-02 → kata-03 … segundo `data/trials.csv`", mas o CSV **não tem timestamp**, então a ordem não pode ser derivada dele.
- ⚠️ O registro de desvio em `docs/experiment_design.md` data `e9478c3` em 2026-09-04 (o commit é de **2026-09-06**) e `805bb72` em 2026-09-17 (o commit é de **2026-09-16 23:24**).

---

## 7. S02 — Execução e Coleta

### 7.1 Requisitos
E10, E12–E15, E28, E29.

### 7.2 Evidências: experimento reconstruído

| Participante | Com IA | Sem IA | Tempos com IA (s) | Tempos sem IA (s) | Commits de dados |
|---|---|---|---|---|---|
| Guilherme | 01, 02, 03 | 04, 05, 06 | 44,3 / 71,8 / 37,6 | 537,4 / 263,7 / 574,3 | `27fcebf` (código 1–3), `3d6cae6`, `66ae97f`, `05574dd` (4–6), `8684477` (tempos 1–3) — #9 |
| Arthur | 01, 03, 05 | 02, 04, 06 | 54,656 / 38,422 / 27,640 | 794,421 / 721,641 / 246,891 | `07398a7` — #10 |
| Marcos | 04, 05, 06 | 01, 02, 03 | 36,781 / 36,824 / 36,757 | 1815,102 / 848,698 / 982,066 | `c30be82` — #11 |

Verificações cruzadas executadas:
- 18/18 trials: `tests_total` bate com o nº real de testes de cada kata, `tests_passing = tests_total`, `success_rate = 100`, `censored = False`, e todos os tempos são < 2100 s. ✅
- 18/18 soluções em `katas/participants/` passam nos testes, e os `test_solution.py` são idênticos aos do oráculo (os testes não foram alterados). ✅
- 18/18 LOC e CC recalculados a partir do código conferem com `static_metrics.csv` (`results/rq3/source_integrity_check.csv`). ✅
- Cada participante fez 3 com IA e 3 sem IA; nenhum kata foi repetido pelo mesmo participante. ✅
- Os horários dos commits de Guilherme (sem IA) são compatíveis com os tempos: kata-04 às 22:49, kata-05 às 22:55 (+6 min, trial de 4,4 min) e kata-06 às 23:05 (+10 min, trial de 9,6 min).

### 7.3 Status

| Item | Status |
|---|---|
| 18 trials registrados, nenhum descartado | ✅ |
| Time-box de 35 min respeitado; regra de censura implementada (0 casos) | ✅ |
| Execução conforme o contrabalanceamento planejado | 🔴 Arthur e Marcos divergem do plano da S01 (documentado) |
| Tempos com proveniência de instrumento | ⚠️ 9 de 18 têm ressalva (6 de Guilherme, 3 de Marcos) |
| Mesmo assistente em todos os trials | ⚠️ só Marcos confirmou por escrito |
| Ordem cronológica / timestamps | ❌ não registrados |
| Uma Issue por kata/tratamento (E28) | 🔴 modelo de uma Issue por participante (#9/#10/#11) |
| Commits dos trials referenciam Issue | ✅ |

### 7.4 Problemas

- 🔴 **Vazamento: as soluções de referência estavam no repositório durante os trials.** O commit `6f79179` (#4, Arthur, **2026-09-07**) adicionou `katas/kata_0N/solution.py` com a solução completa dos 6 katas. Os trials só aconteceram entre 16 e 17/09. Consequências:
  - **Arthur** commitou as 6 soluções antes dos próprios trials, inclusive os "sem IA". A leitura mais provável é que ele as conhecia, mas o repositório não comprova quem as escreveu.
  - O relatório, Seção 2.2, diz "sem experiência prévia formalizada com os katas utilizados", e a Seção 2.6 diz "vazamento mitigado pelo isolamento em pastas individuais". **Isso contradiz a evidência.** A Seção 4.2 reconhece o vazamento só para Guilherme e Marcos.
  - Similaridade textual (difflib) entre a solução do participante e a de referência: Guilherme kata-03 com IA **0,97**, kata-01 com IA 0,81; Marcos kata-05 com IA 0,87. Isso é **indício**, não prova.
  - `docs/katas.md` diz que "os participantes devem iniciar o trial com a implementação removida", mas não há evidência de como isso foi feito.
- 🔴 **Modelo de Issues.** O enunciado pede "Issues individuais (uma por kata/tratamento)". O grupo usou uma Issue por participante e descartou #28–#33. A justificativa está em `docs/experiment_design.md`, mas **não aparece no relatório**, embora o próprio desenho recomende isso.
- 🔴 **#10 (Arthur) foi fechada em 2026-09-09**, mas os dados dele só foram commitados em 2026-09-17. #9, #10 e #11 também têm o comentário "Substituída por issues individuais por kata" (06/09), que depois foi revertido sem novo comentário.
- ⚠️ **Proveniência dos tempos de Guilherme.** As 6 linhas têm 1 casa decimal. O relatório diz corretamente que `TrialRecord.to_row()` grava 3 casas. Mas o CLI **imprime** `elapsed=…:.1f` no terminal (`timer.py`, final de `_cli`), então os valores podem ter sido **transcritos da saída do cronômetro**. O relatório deveria apresentar isso como hipótese, não só dizer que o formato "não corresponde ao que o script produz". Os tempos 1–3 entraram em `8684477` (antigo `0aff185`), cuja mensagem registra conflitos de merge.
- ⚠️ **Modo do cronômetro não registrado.** Não há evidência de se cada trial usou `--kata-path` (green automático) ou ENTER (autodeclaração).
- ⚠️ **Registro de prompts.** O relatório (2.4) diz "registrados interativamente via `register_prompts.py` ao final de cada trial com IA", mas as notas de Marcos no CSV dizem "autorrelato de Marcos, 2026-09-17" (os trials foram no dia 16). → 🔴 inconsistência de redação.
- ⚠️ Familiaridade com IA: `participant_ai_familiarity.csv` foi preenchido por Marcos em nome de Guilherme e Arthur, e isso está registrado no campo `notes`.

---

## 8. S03 — Análise e Dashboard

### 8.1 RQ1: tempo

| Elo | Evidência | Status |
|---|---|---|
| Dado | `data/trials.csv` (`elapsed_seconds`, `censored`) | ✅ |
| Métrica | time-to-green (s), censura em 2100 s | ✅ |
| Descritiva | mediana 37,6 s × 721,6 s; IQR 7,5 × 311,3 | ✅ reproduzido |
| Inferência | Wilcoxon pareado por participante (N = 3), exato, unilateral: W = 0, p = 0,125 (piso) | ✅ reproduzido |
| Censura | implementada (`rq1_rq2.py`); 0 casos | ✅ |
| Outliers | Tukey: Guilherme k02 com IA; Marcos k01 sem IA; mantidos | ✅ |
| Gráficos | Fig. 1 (distribuição, escala log) e Fig. 2 (pareada por participante) | ✅ |
| Resposta | "H0 não rejeitada; descritivamente favorece H1; teste sem poder" | ✅ |

### 8.2 RQ2: defeitos

| Elo | Evidência | Status |
|---|---|---|
| Dados e métricas | taxa de sucesso e nº de testes falhando | ✅ |
| Estatística | Wilcoxon não aplicável (todas as diferenças são zero), corretamente declarado | ✅ |
| Gráfico | Fig. 3 (desfecho dos trials) | ✅ |
| Resposta | "**Não respondida**: efeito de teto do protocolo (o trial termina no green)" | ⚠️ honesta, mas a RQ fica efetivamente sem resposta, por falha de desenho |

### 8.3 RQ3: estrutura

| Elo | Evidência | Status |
|---|---|---|
| CC | Radon 6.0.1 `cc`; 1 função por trial; 18/18 recalculados | ✅ |
| Duplicação | jscpd 4.0.5, mínimo de 5 linhas / 20 tokens; **0 em 18/18** | ⚠️ não avaliável; declarado |
| LOC | Radon `raw` (`loc` bruto); SLOC como sensibilidade | ✅ |
| MI (OPC) | duas séries: "como coletado" mistura convenções (12 trials com média incluindo `__init__.py` vazio = 100; os 6 de Guilherme sem ele) e "harmonizado" | 🔴 dado bruto inconsistente, **documentado e mitigado** |
| Inferência | Wilcoxon bilateral por participante (p = 0,25, piso), por kata (sensibilidade), Bonferroni/BH, r_rb | ✅ reproduzido |
| Gráficos | Fig. 4–8 (+ bônus 9–10) | ✅ |
| Resposta | "H0 não rejeitada; confundimento kata × tratamento" | ✅ |

### 8.4 Dashboard

O enunciado pede gráficos Pandas + Matplotlib/Seaborn comparando **tempo, taxa de sucesso e métricas estáticas**. Isso é atendido por `generate_figures.py` → `experiment/visualization/report_figures.py` (pandas + matplotlib). Não existe um "dashboard" único (notebook ou página): as figuras são estáticas e ficam em `docs/figures/`. Isso atende ao texto do enunciado.

| Gráfico | RQ | Dados corretos? | Legenda / eixos / unidade | Comparação clara? |
|---|---|---|---|---|
| `rq1_tempo_por_tratamento` | 1 | ✅ reproduzido | ✅ log, s/min, time-box marcado | ✅ |
| `rq1_tempo_por_participante` | 1 | ✅ | ✅ nº do kata nos pontos, ressalvas no rodapé | ✅ pareada |
| `rq2_desfecho_trials` | 2 | ✅ | ✅ | ✅ (mostra o mecanismo; não é boxplot da taxa, o que foi justificado) |
| `rq3_loc_cc_por_tratamento` | 3 | ✅ | ✅ | ✅ |
| `rq3_loc_cc_por_participante` | 3 | ✅ | ✅ | ✅ pareada |
| `rq3_mi_duas_series` | 3 | ✅ | ✅ aviso de escalas diferentes | ✅ |
| `rq3_cc_vs_loc` | 3 | ✅ | ✅ | ✅ |
| `rq3_cc_normalizada` | 3 | ✅ | ✅ | ✅ |
| `bonus_mi_componentes`, `bonus_prompts_qualidade` | bônus | ✅ | ✅ | ✅ |
| `results/rq3/figures/fig1…fig5` | 3 | ✅ | — | 🟡 **redundantes**: não usadas no relatório |
| Duplicação | 3 | — | — | sem figura, de propósito (valor constante); justificado no relatório |

Observação: a Issue #17 pedia "anotações com mediana e p-valor em cada gráfico". As figuras finais **omitem p-valores de propósito** (estão nas tabelas). Isso é uma divergência da Issue, não do enunciado.

### 8.5 Status
Análise S03: ✅ técnica e reprodutível. Pendências: RQ2 sem resposta (desenho), duplicação não avaliável (desenho), MI bruto com duas convenções (mitigado).

### 8.6 Problemas
- 🟡 `experiment/visualization/boxplots.py` (entregável original de Arthur na #17) foi substituído por `report_figures.py` (Marcos, #21). Hoje só os testes o usam.
- 🟡 `generate_figures.py` e `report_figures.py` citam o plano `AUDITORIA_VISUALIZACAO.md`, que **não existe** no repositório.
- 🟡 `seaborn` está fixado em `requirements.txt`, mas não é usado.

---

## 9. Dados e rastreabilidade

### 9.1 Datasets

| Dataset | Tipo | Origem | Colunas | Linhas | Usado? | Problemas |
|---|---|---|---:|---:|---|---|
| `data/trials.csv` | bruto | cronômetro / manual (Guilherme) | 9 | 18 | RQ1, RQ2, RQ3 | sem timestamp nem modo do cronômetro; proveniência ⚠️ em 9 linhas |
| `data/static_metrics.csv` | bruto | `static_metrics.py` | 15 | 18 | RQ3 | MI com duas convenções |
| `data/prompts/prompt_records.csv` | bruto | autorrelato (sem evidência de uso do `register_prompts.py`) | 7 | 12 | bônus | parte retroativa |
| `data/participant_ai_familiarity.csv` | bruto | autorrelato via Marcos | 4 | 3 | **não** | ausente do relatório |
| `results/rq3/consolidated_trials.csv` | derivado | `rq3.py` | — | 18 | RQ3 | — |
| `results/rq3/source_integrity_check.csv` | derivado | recálculo via Radon | — | 18 | MI harmonizado e SLOC | — |
| `results/rq3/{descriptive_statistics,statistical_tests,normalized_metrics,outliers,task_allocation_balance}.csv` | final | `rq3.py` | — | — | Tabela 4 e Seção 3.4 | — |
| `results/mi_prompts/*.csv` | final | `mi_prompts.py` | — | — | Seção 3.6 | — |
| `data/kanban-snapshots/*.csv` | evidência de processo | `generate_kanban_snapshot.py` | 5 | 34 cada | Kanban | #41 não aparece (não tem o label `lab02`) |

### 9.2 Cadeia resultado → dado
Para cada número do relatório conferido (Tabelas 1–4, Seções 3.4 e 3.6), a cadeia **relatório → `.md`/CSV de resultado → script → `data/*.csv` → commit do trial** fecha. A reexecução completa não produziu nenhum diff. ✅

### 9.3 Hashes de commit quebrados (🔴)
O `main` foi **reescrito** (existe a branch local `backup/main-antes-rewrite`; todos os hashes mudaram desde o "Initial commit"; `origin/main` recebeu force-push). Os hashes citados nos documentos são **da história antiga**. Eles não existem em `main` e só são alcançáveis pelas branches remotas `feature/*` ou `pr/*`:

| Citado em | Hash citado | Equivalente em `main` | Commit |
|---|---|---|---|
| `relatorio.md` 2.1; `experiment_design.md` | `e9478c3` | `906bafc` | #3 desenho |
| `relatorio.md` 2.4 ("`git show 0aff185 -- data/trials.csv`") | `0aff185` | `8684477` | #9 tempos 1–3 |
| `experiment_design.md` | `c826baa` | `07398a7` | #10 Arthur |
| `experiment_design.md` | `805bb72` | `c30be82` | #11 Marcos |
| `experiment_design.md` | `485bc09`, `faff5d4`, `f79eb52`, `991cf83` | `3d6cae6`, `66ae97f`, `05574dd`, `27fcebf` | #9 |

Risco: se `origin/feature/participants-kata-solutions` ou `origin/feature/issue-20-relatorio` forem apagadas, as referências do relatório deixam de funcionar no GitHub.

---

## 10. Scripts e reprodutibilidade

### 10.1 Scripts

| Script | Finalidade | Entrada | Saída | Executável? | No resultado final? |
|---|---|---|---|---|---|
| `experiment/collection/timer.py` | cronômetro | CLI | `data/trials.csv` | ✅ | ✅ (S02) |
| `experiment/collection/static_metrics.py` | Radon + jscpd | diretório do trial | `data/static_metrics.csv` | ✅ | ✅ (S02) |
| `register_prompts.py` / `consolidate_prompts.py` | prompts | interativo | `data/prompts/` | ✅ | ✅ bônus |
| `analyze_rq1_rq2.py` | RQ1/RQ2 | `data/trials.csv` | `docs/analysis_rq1_rq2.md` | ✅ sem diff | ✅ |
| `python -m experiment.analysis.rq3` | RQ3 | os 2 CSVs + código | `results/rq3/` | ✅ sem diff | ✅ |
| `python -m experiment.analysis.mi_prompts` | bônus | CSVs + código | `results/mi_prompts/` | ✅ sem diff | ✅ |
| `generate_figures.py` | figuras | análises | `docs/figures/` | ✅ sem diff | ✅ |
| `generate_design_report.py` | desenho | `lab02_design.py` | `docs/experiment_design.md` | 🔴 **destrutivo** | — |
| `generate_kanban_snapshot.py` | Kanban | API GitHub (`GITHUB_TOKEN`) | `data/kanban-snapshots/` | não testado (precisa de token) | ✅ |
| `experiment/visualization/boxplots.py` | figuras antigas | — | — | só testes | ❌ morto |

**🔴 `generate_design_report.py`:** executado na cópia descartável, ele sobrescreve `docs/experiment_design.md`. O resultado tem −120 linhas: some o "Registro de desvio de protocolo", a "Confirmação de execução", a "Justificativa do modelo de Issues", o status das mitigações e a ameaça "Desvio de protocolo". Também muda `tool_version` → `duplication_tool_version`. Essas seções foram editadas à mão e não estão em `lab02_design.py`. O README manda rodar esse comando.

### 10.2 Versões

| Item | Documentado | Verificado no ambiente | Status |
|---|---|---|---|
| Python | "3.10+" (README) | 3.14.5 no `.venv` | ⚠️ versão usada na S02 não comprovada |
| pytest / radon / numpy / pandas / scipy / matplotlib / seaborn | fixados em `requirements.txt` | idênticos no `.venv` | ✅ |
| jscpd | 4.0.5 (`package-lock.json`) | 4.0.5 | ✅ (bate com a coluna do CSV) |
| Radon | 6.0.1 | 6.0.1 | ✅ (bate com a coluna do CSV) |
| Assistente | Claude Code / Claude Sonnet 5 | — | ⚠️ versão do Claude Code não registrada; uso confirmado por escrito só por Marcos |
| IDE | VS Code | — | ⚠️ versão não registrada (baixo impacto) |
| Testes | 336 passed | reexecutado | ✅ |

---

## 11. GitHub Projects e Issues

> Não consegui ler o board diretamente: o token do `gh` não tem o escopo `read:project`. O estado abaixo vem das Issues (`gh issue list`) e dos snapshots CSV.

| Issue | Estado atual | Problema |
|---|---|---|
| #10 (trials Arthur) | CLOSED em **09-09** | fechada 8 dias antes dos dados (commit de 09-17) 🔴 |
| #13 (FEAT S03) | OPEN | trabalho da S03 já mergeado |
| #15 (RQ1/RQ2) | **OPEN** | entregue por Arthur (`488084a`, `8798413`); Guilherme também é Assignee, sem commit. No snapshot de 09-17 o único Assignee era Guilherme 🔴 |
| #17 (dashboard) | **OPEN** | as figuras de Arthur foram substituídas na #21 |
| #18 (bônus MI/prompts) | **OPEN** | entregue (`f145d4b`) |
| #21 (relatório: resultados) | **OPEN** | entregue (`c410d0d`) |
| #19, #23 (relatório final, revisão/PDF) | OPEN | legítimo: revisão cruzada e PDF ainda não feitos |
| #27 (snapshot Kanban S03) | OPEN | ❌ snapshot da S03 inexistente |
| #20 | milestone **S02** | tarefa do relatório no milestone errado |
| #41 | sem label `lab02` | não aparece nos snapshots (o filtro é por label) |
| #9/#10/#11 | comentário "Substituída…" | reversão não comentada |
| Evolução semanal | snapshot de 09-17 com toda a S03 em Backlog; **nenhum commit entre 09-18 e 09-22**; toda a S03 em 09-23 | ⚠️ pode ser lido como "ausência de evolução semanal" |

Todas as Issues têm Assignee. ✅

---

## 12. Commits e participação individual

Regra (E27): em cada sprint, cada integrante precisa ser Assignee de ≥ 1 Issue **da sprint** com artefato de código commitado, e o commit precisa referenciar a Issue.

| Sprint | Integrante | Issue | Assignee? | Artefato | Commit(s) em `main` | Issue ↔ commit |
|---|---|---|---|---|---|---|
| S01 | Guilherme | #3, #25 | ✅ | `experiment/config`, `domain`, `kanban/` | `906bafc`, `d7254d8`, `046c4d1` | ✅ |
| S01 | Arthur | #4, #6 | ✅ | `katas/`, `duplication_metrics.py` | `6f79179`, `e563cba` | ✅ |
| S01 | Marcos | #5, #24, #35 | ✅ | `timer.py`, `static_metrics.py`, README | `b03e305`, `e89848a`, `3305aad` | ✅ |
| S02 | Guilherme | #9, #12 | ✅ | soluções + CSV; registro de prompts | `27fcebf`, `3d6cae6`, `66ae97f`, `05574dd`, `8684477`, `d55c26a` | ✅ |
| S02 | Arthur | #10, #26 | ✅ | soluções + CSV; snapshot | `07398a7`, `7b9e0e5` | ✅ |
| S02 | Marcos | #11, #41 | ✅ | soluções + CSV; sincronização do schema | `c30be82`, `078f511` | ✅ |
| S03 | Arthur | #15, #17 | ✅ | `rq1_rq2.py` (usado no final), `boxplots.py` (substituído) | `488084a`, `8798413`, `af694e5`, `2722f6f` | ✅ |
| S03 | Marcos | #16, #18 | ✅ | `rq3.py`, `mi_prompts.py` | `0d28068`, `f145d4b` | ✅ |
| S03 | **Guilherme** | #13 (feat), #14 (refinamento), #15 (co-assignee) | ✅ | **nenhum** | **nenhum commit referenciando Issue da S03** | 🔴 |
| Relatório | Guilherme / Marcos | #20, #22 / #21 | ✅ | `relatorio.md` | `adad98a`, `b6daa49` / `c410d0d` | ✅ (fora das sprints) |

**Commits sem referência a Issue** (fora os merges): `5eb4153` "Initial commit", `19fd9b5` "Add initial documentation…" (enunciado) e **`5b917f9` "Fix REDME.md" (Arthur, 09-23, +27 linhas no README, durante a S03)**. Pela regra do enunciado, esses commits "não serão considerados". O impacto é baixo, porque nenhum integrante depende deles.

Commits não merge em `main`: Guilherme 12, Marcos 9, Arthur 8.

---

## 13. Relatório Final

| Item | Status | Evidência / lacuna |
|---|---|---|
| (i) Introdução | ✅ | Seção 1 |
| (i) **Hipóteses na introdução** | ⚠️ | H0/H1 só aparecem nas Seções 3.2–3.4 (resultados); a introdução só lista as RQs |
| GQM / Goal explícito | ⚠️ | o Goal do GQM não aparece; as métricas são listadas junto às RQs |
| Justificativa das métricas (E11) | ⚠️ | só em `experiment_design.md` e de forma parcial no relatório (MI, LOC) |
| (ii) Metodologia: desenho, desvio, participantes, katas, coleta, estatística | ✅ | Seções 2.1–2.5 |
| (ii) Assistente e versão | ✅/⚠️ | "Claude Code — Claude Sonnet 5"; sem a versão do Claude Code |
| (ii) Versão de Python e ambiente | ⚠️ | não aparece no relatório (só "3.10+" no README) |
| (ii) Como a solução de referência foi escondida | ❌ | não aparece |
| Divergência do modelo de Issues (E28) | ❌ | não aparece, embora `experiment_design.md` diga que deve constar |
| Evidência de baixa indexação | ❌ | prometida em `katas.md`, não anexada |
| (iii) Resultados por RQ com estatística | ✅ | números conferidos com os CSVs e reproduzidos |
| Descritiva × inferência separadas | ✅ | "Evidência descritiva" / "Inferência" em cada RQ |
| (iv) Discussão final | ✅ | Seção 4 (#22) |
| Ameaça **familiaridade prévia com IA** (E7) | ❌ | fora das Seções 2.6 e 4.2; o CSV existe, mas não é usado |
| Ameaça de vazamento descrita corretamente | 🔴 | 2.2 ("sem experiência prévia") e 2.6 ("mitigado") contradizem 4.2 e o commit `6f79179` |
| Registro de prompts | 🔴 | 2.4 diz "interativamente ao final de cada trial"; o CSV registra autorrelato retroativo |
| Conclusão sem extrapolar | ✅ | "H0 não rejeitada … não é evidência de ausência de efeito" |
| Frases a revisar | 🟡 | Conclusão: "coleta de dados com instrumentação automática" (9 de 18 tempos com ressalva). Recomendação (3): "o mesmo participante resolva o mesmo kata nos dois tratamentos (crossover puro)" — isso cria efeito de memória do kata; reformular (ex.: mais participantes, alocação de katas balanceada por dificuldade) |
| (v) Link do repositório e do Projects | ✅ | cabeçalho |
| Data de entrega | ❌ | "*(a preencher)*" |
| Hashes citados | 🔴 | `e9478c3` e `0aff185` não existem em `main` (§9.3) |
| Revisão cruzada + PDF (#23, plano do grupo) | ❌ | #23 aberta |

---

## 14. Matriz de rastreabilidade

| # | Requisito | Exig. | Evidência | Status | Ação necessária |
|---|---|---|---|---|---|
| R01 | Hipóteses H0/H1 | EXIG | `experiment_design.md` | ✅ | — |
| R02 | Variáveis dependentes | EXIG | idem | ✅ | — |
| R03 | Variável independente | EXIG | idem | ✅ | — |
| R04 | Tratamentos | EXIG | `enums.py`, CSVs | ✅ | — |
| R05 | 6 katas com testes automatizados | EXIG | `katas/`, 36 testes | ✅ | — |
| R06 | Dificuldade equivalente | EXIG | `katas.md` (estimativa) | ⚠️ | declarar como limitação (já em parte na Seção 2.3) |
| R07 | Baixa indexação comprovada | REC/CONS | promessa em `katas.md` | ❌ | fazer a busca, registrar a data e anexar, ou retirar a promessa e declarar |
| R08 | Crossover contrabalanceado planejado | REC | `906bafc` | ✅ | — |
| R09 | Quantidade de medições | EXIG | 18 | ✅ | — |
| R10 | Ameaças no desenho | EXIG | `experiment_design.md` | ✅ | — |
| R11 | Versões do ambiente | EXIG | README | ⚠️ | registrar a versão de Python e do Claude Code usadas |
| R12 | Scripts de tempo e métricas | EXIG | `experiment/collection`, testes | ✅ | — |
| R13 | Justificativa das métricas no desenho | EXIG | `experiment_design.md` | ✅ | — |
| R14 | Cartões da S01 no Kanban | EXIG | snapshot 09-10 | ✅ | — |
| R15 | 18 trials registrados | EXIG | `trials.csv` | ✅ | — |
| R16 | Time-box de 35 min e censura | EXIG | `trials.csv`, `rq1_rq2.py` | ✅ | — |
| R17 | Proveniência dos tempos | CONS | 9 de 18 com ressalva | ⚠️ | ajustar o texto sobre Guilherme (transcrição do print `.1f`) |
| R18 | Testes passando ao final | EXIG | `trials.csv` | ✅ | — |
| R19 | Métricas estáticas por trial (CC/LOC/dup) | EXIG | `static_metrics.csv`, 18/18 recalculados | ✅ | — |
| R20 | MI homogêneo | OPC | duas convenções | 🔴 | já mitigado (série harmonizada); manter declarado |
| R21 | Execução = contrabalanceamento planejado | EXIG | desvio de Arthur e Marcos | 🔴 | já declarado; falta o motivo na voz de Arthur |
| R22 | Mesmo assistente em todos os trials | EXIG | só Marcos por escrito | ⚠️ | confirmação escrita de Arthur e Guilherme |
| R23 | Timestamps / ordem dos trials | CONS | inexistente | ❌ | não dá para recuperar; declarar (já declarado) |
| R24 | Isolamento de soluções | EXIG (ameaça H) | `6f79179` com referências | 🔴 | corrigir as Seções 2.2 e 2.6 do relatório; incluir Arthur como autor das referências |
| R25 | Uma Issue por kata/tratamento | EXIG | #9/#10/#11 | 🔴 | declarar a divergência e a justificativa no relatório |
| R26 | Commits dos trials referenciam Issue | EXIG | §12 | ✅ | — |
| R27 | RQ1 descritiva (mediana/IQR) | REC | Tabela 1 | ✅ | — |
| R28 | RQ1 Wilcoxon | EXIG | p = 0,125 | ✅ | — |
| R29 | RQ1 censura na análise | REC | `rq1_rq2.py` | ✅ | — |
| R30 | RQ1 gráfico | EXIG | Fig. 1–2 | ✅ | — |
| R31 | RQ2 respondida | EXIG | "não respondida" (teto) | ⚠️ | declarado; nada a corrigir sem nova coleta |
| R32 | RQ2 estatística | EXIG | não aplicável, declarado | ✅ | — |
| R33 | RQ2 gráfico (taxa de sucesso) | EXIG | Fig. 3 | ✅ | — |
| R34 | RQ3 CC | EXIG | Radon | ✅ | — |
| R35 | RQ3 duplicação | EXIG | 0 em 18/18 | ⚠️ | declarado como não avaliável |
| R36 | RQ3 LOC | EXIG | Radon `raw` | ✅ | — |
| R37 | RQ3 Wilcoxon + multiplicidade | EXIG | `statistical_tests.csv` | ✅ | — |
| R38 | RQ3 gráficos | EXIG | Fig. 4–8 | ✅ | — |
| R39 | Outliers identificados e mantidos | EXIG | Tukey, `outliers.csv` | ✅ | — |
| R40 | Dashboard (pandas + matplotlib) | EXIG | `docs/figures/` | ✅ | — |
| R41 | Análises reproduzíveis | CONS | reexecução sem diff | ✅ | — |
| R42 | Gerador do desenho preserva o documento | CONS | −120 linhas | 🔴 | mover as seções manuais para outro arquivo ou para o gerador, ou tirar o comando do README |
| R43 | Versões documentadas (reprodução) | EXIG (ii) | §10.2 | ⚠️ | fixar a versão de Python |
| R44 | Hipóteses na introdução do relatório | EXIG (i) | só na Seção 3 | ⚠️ | adicionar H0/H1 na Seção 1 |
| R45 | GQM / justificativa das métricas no relatório | EXIG | parcial | ⚠️ | incluir o Goal e a justificativa de cada métrica |
| R46 | Metodologia reprodutível | EXIG (ii) | Seção 2 | ⚠️ | Python, versão do Claude Code, modo do cronômetro, ocultação da referência |
| R47 | Resultados por RQ com estatística | EXIG (iii) | Seção 3 | ✅ | — |
| R48 | Discussão | EXIG (iv) | Seção 4 | ✅ | — |
| R49 | Ameaça "familiaridade com IA" no relatório | EXIG (H) | ausente | ❌ | incluir, usando `participant_ai_familiarity.csv` |
| R50 | Conclusão suportada pelos dados | EXIG | Seção 5 | ✅ | ajustes 🟡 de redação |
| R51 | Link do repositório/Projects | EXIG (v) | cabeçalho | ✅ | — |
| R52 | Data de entrega | CONS | "a preencher" | ❌ | preencher |
| R53 | Hashes citados existem em `main` | CONS | §9.3 | 🔴 | trocar pelos hashes de `main` |
| R54 | Registro de prompts descrito corretamente | CONS | 2.4 × CSV | 🔴 | corrigir o texto (autorrelato retroativo) |
| R55 | Revisão cruzada + PDF (#23) | OPC (plano do grupo) | #23 aberta | ❌ | executar ou fechar com justificativa |
| R56 | S01: 3/3 com Issue + commit | EXIG | §12 | ✅ | — |
| R57 | S02: 3/3 com Issue + commit | EXIG | §12 | ✅ | — |
| R58 | S03: 3/3 com Issue + commit | EXIG | Guilherme sem commit | 🔴 | ver Plano B1 |
| R59 | Todos os commits referenciam Issue | EXIG | 3 sem `#` | ⚠️ | não reescrever; seguir a regra daqui em diante |
| R60 | Status das Issues coerente | EXIG | #10, #15, #17, #18, #21 | 🔴 | atualizar o board |
| R61 | Snapshot do Kanban da S03 | CONS (#27) | ausente | ❌ | gerar |
| R62 | Issues com Assignee | EXIG | todas | ✅ | — |
| R63 | Evolução semanal | EXIG | lacuna 09-18 a 09-22 | ⚠️ | não corrigível; não piorar |
| R64 | Board verificável | EXIG | sem `read:project` | ⚠️ | conferir manualmente no navegador |
| R65 | `katas.md` coerente com os testes | CONS | 5–6 × 5–7; tabela (a) errada | 🔴 | corrigir as contagens |
| R66 | Sem scripts mortos ou duplicados | OPC | `boxplots.py`, `results/rq3/figures`, `AUDITORIA_VISUALIZACAO.md` | ⚠️ | limpar ou documentar |

**Totais: ✅ 36 · ⚠️ 14 · ❌ 6 · 🔴 10 (66 requisitos).**

---

## 15. Falsos OK encontrados

| Parece OK | Mas… |
|---|---|
| ✅ "Vazamento mitigado pelo isolamento em pastas individuais" (relatório 2.6) | ❌ as soluções de referência completas estavam em `katas/kata_0N/solution.py` desde 07/09, commitadas por um dos participantes |
| ✅ "Participantes sem experiência prévia com os katas" (2.2) | ❌ Arthur commitou as soluções de referência antes dos próprios trials |
| ✅ Issue #10 fechada / Done | ❌ fechada em 09-09; os trials de Arthur só entraram em 09-17 |
| ✅ S03 entregue pelos três | ❌ Guilherme não tem commit em Issue da S03 |
| ✅ Dashboard da #17 (Arthur) | ⚠️ substituído pelo `report_figures.py` de Marcos (#21); o código de Arthur ficou morto, e a #17 continua aberta |
| ✅ "Relatório do desenho: `python generate_design_report.py`" (README) | 🔴 o comando apaga o registro de desvio de protocolo |
| ✅ "Verificável com `git show 0aff185`" (relatório 2.4) | 🔴 o hash não existe em `main` |
| ✅ Ameaças à validade completas | ❌ "familiaridade prévia com IA", exigida no enunciado, não está no relatório |
| ✅ "Prompts registrados interativamente ao final de cada trial" | 🔴 as notas do CSV dizem "autorrelato … 2026-09-17", depois dos trials |
| ✅ Tabela de testes por kata em `katas.md` | 🔴 kata-05 = 7 (não 5), kata-06 = 5 (não 6) |
| ✅ Baixa indexação | ❌ nenhuma busca registrada |
| ✅ RQ2 "respondida" com estatística | ⚠️ o próprio relatório admite que não foi respondida (efeito de teto) — correto e honesto, mas não é um OK |
| ✅ Duplicação medida | ⚠️ constante zero; não avaliável |
| ✅ Mesmo assistente em todos os trials | ⚠️ só Marcos confirmou por escrito |

---

## 16. Inconsistências encontradas

| # | Fonte A | Fonte B | Divergência |
|---|---|---|---|
| I1 | Plano da S01 (`906bafc`): Arthur 1–3 sem IA, Marcos 1–3 com IA | `trials.csv`: Arthur alternado, Marcos invertido | desvio de protocolo (documentado) |
| I2 | Enunciado: uma Issue por kata/tratamento | #9/#10/#11 por participante | divergência documentada só no desenho |
| I3 | Relatório 2.2 / 2.6 | commit `6f79179` e relatório 4.2 | vazamento negado × vazamento existente |
| I4 | `katas.md`: "5 e 6 testes"; tabela (a) | `pytest --collect-only`: 5, 6, 7, 6, 7, 5 | contagens erradas |
| I5 | `experiment_design.md`: `e9478c3` de 09-04; `805bb72` de 09-17 | git: 09-06; 09-16 23:24 | datas |
| I6 | Relatório e desenho citam hashes antigos | `main` reescrito | hashes inexistentes |
| I7 | Relatório 2.4 (prompts "interativamente") | notas do CSV (autorrelato de 09-17) | forma de coleta |
| I8 | README: Python "3.10+" | `.venv` 3.14.5 | versão de execução não comprovada |
| I9 | Issue #10 CLOSED em 09-09 | dados de Arthur em 09-17 | status |
| I10 | Snapshot 09-17: #15 com Assignee Guilherme | hoje: Arthur + Guilherme; commits só de Arthur | Assignee alterado depois |
| I11 | Issue #17: "anotar p-valor em cada gráfico" | figuras finais sem p-valor (decisão consciente) | escopo da Issue |
| I12 | `generate_figures.py`: "plano em AUDITORIA_VISUALIZACAO.md" | arquivo inexistente | referência quebrada |
| I13 | `static_metrics.csv`: MI de Guilherme ≈ 54–68, dos demais ≈ 76–84 | convenções diferentes (`__init__.py`) | documentada; série harmonizada |
| I14 | Relatório: tempos de Guilherme "não correspondem ao que o script produz" | `timer.py` imprime `elapsed=%.1f` | afirmação incompleta (podem ter sido transcritos do terminal) |
| I15 | #20 (tarefa do relatório) | milestone S02 | classificação |

Conferidas e **sem** divergência: 18 trials em todos os artefatos; 3 participantes; 6 katas; time-box de 35 min; Radon 6.0.1 e jscpd 4.0.5 nos CSVs = `requirements`/`package-lock`; todos os números das Tabelas 1–4 e da Seção 3.6.

---

## 17. Itens obrigatórios (EXIG) ainda não atendidos

1. Guilherme: artefato de código commitado em Issue da S03 (R58).
2. Relatório: hipóteses na introdução (R44).
3. Relatório: ameaça "familiaridade prévia com IA" (R49).
4. Relatório: vazamento descrito corretamente (R24).
5. Relatório: declarar a divergência do modelo de Issues (R25).
6. Relatório: justificativa das métricas por RQ e metodologia com versões (R45, R46, R43).
7. Board: status coerentes (R60).
8. Confirmação de uso do mesmo assistente por Arthur e Guilherme (R22).

## 18. Itens recomendados (REC)

1. Evidência de baixa indexação (R07).
2. Motivo do desvio de protocolo na voz de Arthur (R21).
3. Confirmação de familiaridade com IA por escrito, por Guilherme e Arthur.

## 19. Itens opcionais (OPC)

MI (feito), nº de prompts (feito), PDF e revisão cruzada (#23), limpeza de `boxplots.py`, `results/rq3/figures` e `seaborn`, e remover a referência a `AUDITORIA_VISUALIZACAO.md`.

---

## 20. Plano de Correção

### 🔴 BLOQUEADORES DA ENTREGA

| # | Problema | Por que é bloqueador | Ação |
|---|---|---|---|
| B1 | Guilherme sem commit em Issue da S03 | o enunciado zera a parcela individual | Guilherme assume uma tarefa **real** da S03 com código: por exemplo, a #27 (gerar o snapshot da S03 com `generate_kanban_snapshot.py` e commitar com `#27`) e/ou a consolidação da #17. O commit precisa referenciar a Issue. **Não retroagir datas nem reatribuir autoria.** |
| B2 | Relatório afirma "sem experiência prévia" e "vazamento mitigado" | contradiz o commit `6f79179`; ameaça exigida (H) descrita de forma errada | Reescrever 2.2, 2.6 e 4.2: soluções de referência no repositório desde 07/09, commit de Arthur; declarar o impacto potencial nos trials de Arthur e nos demais |
| B3 | Ameaça "familiaridade com IA" ausente do relatório | exigida em Passo 1 (H) | Incluir em 2.6/4.2 com os níveis de `participant_ai_familiarity.csv` e a ressalva de coleta |
| B4 | Hipóteses fora da introdução | Passo 5 (i) | Adicionar H0/H1 das três RQs na Seção 1 |
| B5 | Modelo de Issues diverge do enunciado sem declaração no relatório | Observações do enunciado; o desenho promete declarar | Incluir a justificativa (texto já pronto em `experiment_design.md`) |
| B6 | Hashes inexistentes em `main` | a correção é feita pelo GitHub; a referência "verificável com `git show 0aff185`" falha no `main` | Trocar `e9478c3`→`906bafc`, `0aff185`→`8684477` (relatório) e os demais da tabela do §9.3 (desenho). Não apagar as branches `feature/*` antigas |
| B7 | Board desatualizado | desconto de até 10% por sprint | Fechar #15, #16 (já fechada), #17, #18 e #21 com comentário apontando os commits; corrigir o histórico da #10 com um comentário; mover o que falta; gerar o snapshot da S03 (#27) |

### 🟠 IMPORTANTES

| # | Ação |
|---|---|
| I-1 | `generate_design_report.py` destrutivo: tirar as seções manuais de `experiment_design.md` (ex.: `docs/experiment_design_desvios.md`) ou avisar no README que o comando sobrescreve o arquivo |
| I-2 | Corrigir as contagens de testes em `docs/katas.md` e as datas dos commits em `experiment_design.md` |
| I-3 | Relatório 2.4: descrever os prompts como "autorrelato registrado após o trial" onde for o caso |
| I-4 | Relatório: versão de Python e do Claude Code, modo do cronômetro usado e como a solução de referência foi ocultada (ou declarar que não foi) |
| I-5 | Relatório: Goal do GQM e justificativa de cada métrica (reaproveitar `experiment_design.md`) |
| I-6 | Confirmação escrita (comentário na Issue #10/#9) de Arthur e Guilherme: assistente usado, familiaridade e motivo do desvio (Arthur) |
| I-7 | Evidência de baixa indexação, ou retirar a promessa de `katas.md` e declarar como limitação |
| I-8 | Relatório: ajustar a ressalva de Guilherme (os valores com 1 casa decimal podem ter sido transcritos do terminal, que imprime `%.1f`) |
| I-9 | Preencher a data de entrega; executar a #23 (revisão cruzada + PDF) |

### 🟡 MELHORIAS

- Remover ou documentar `boxplots.py`, `results/rq3/figures/` (redundantes), a referência a `AUDITORIA_VISUALIZACAO.md` e o `seaborn` sem uso.
- Rever a recomendação (3) da conclusão ("mesmo kata nos dois tratamentos" gera efeito de memória) e a frase "instrumentação automática".
- Colocar o label `lab02` na #41 e mover a #20 para o milestone "Relatório Final".
- **Não versionar** `trab-final-pdf (1).pdf` (material de outro grupo) nem `GRAFICOS_CONCEITOS.md`, a menos que o grupo decida o contrário.

> **O que NÃO fazer:** alterar `data/*.csv`, remover os trials de Marcos ou de Guilherme, trocar a série principal de MI, reescrever o histórico de novo ou criar agora as 18 Issues por trial como se fossem da S02.

---

## 21. Checklist final

> Estado em 2026-09-24, após a etapa de correção. `[x]` resolvido · `[ ]` pendente · **⚠️ AÇÃO POSTERIOR** = depende de commit, GitHub/Kanban ou de terceiros.

### Experimento
- [x] S01 documentada (desenho, katas, scripts)
- [x] S02 executada (18 trials)
- [x] S03 analisada (RQ1–RQ3 + bônus)
- [x] Desvio desenho × execução documentado
- [x] Soluções de referência descritas corretamente (disponível ≠ acessado ≠ usado) no relatório, no desenho e em `katas.md`

### Dados
- [x] 18 trials registrados, 0 descartados
- [x] Censura tratada (0 casos)
- [x] LOC e CC reproduzidos a partir do código (18/18)
- [x] `data/` preservado (sem diff)
- [ ] ⚠️ AÇÃO POSTERIOR — confirmações escritas de Arthur e Guilherme (assistente usado, familiaridade, motivo do desvio de Arthur)

### RQ1
- [x] métrica · [x] estatística · [x] gráfico · [x] resposta

### RQ2
- [x] métrica · [x] estatística (n/a declarado) · [x] gráfico · [x] resposta ("não respondida", justificada)

### RQ3
- [x] métricas (CC, LOC, dup, MI) · [x] ferramentas e versões · [x] análise · [x] gráficos · [x] resposta

### Dashboard
- [x] RQ1 · [x] RQ2 · [x] RQ3 · [x] reprodutível sem diff

### Relatório
- [x] introdução · [x] hipóteses **na introdução** (1.2) · [x] Goal do GQM + justificativa das métricas (1.1)
- [x] metodologia com versões (o que foi fixado × o que foi comprovado) e modos do cronômetro
- [x] resultados · [x] discussão · [x] ameaça de familiaridade (2.6, 4.2) · [x] vazamento corrigido (2.2, 2.3, 2.6, 4.2)
- [x] modelo de Issues declarado (2.4) · [x] hashes corrigidos · [x] redação sobre prompts corrigida (2.4)
- [x] conclusão (recomendação 3 e "instrumentação automática" revistas) · [x] link do repositório/Projects
- [x] data de entrega — 24/09/2026 (Seção 25)
- [ ] ⚠️ AÇÃO POSTERIOR — revisão cruzada/PDF (#23)

### GitHub
- [x] S01: 3/3 com Issue + artefato + commit
- [x] S02: 3/3 com Issue + artefato + commit
- [ ] ⚠️ AÇÃO POSTERIOR — S03: **Guilherme** com Issue da S03 + artefato de código + commit
- [ ] ⚠️ AÇÃO POSTERIOR — #15, #17, #18, #21 fechadas com referência aos commits; #10 com comentário
- [ ] ⚠️ AÇÃO POSTERIOR — snapshot do Kanban da S03 (#27)
- [ ] ⚠️ AÇÃO POSTERIOR — board conferido manualmente no navegador
- [ ] ⚠️ AÇÃO POSTERIOR — commitar as correções desta etapa com referência a Issue

### Reprodutibilidade
- [x] `pytest` → 341 passed
- [x] análises e figuras reproduzíveis (`results/` e `docs/figures/` sem diff)
- [x] `generate_design_report.py` preserva o conteúdo manual (idempotente; para sem gravar se fosse perder texto)
- [x] versão de Python documentada (mínimo 3.10; análise validada em 3.14.5; versão dos trials não registrada)

---

## 22. Definition of Done — LAB02

O LAB02 está pronto para entrega quando **todas** as condições abaixo forem verdadeiras:

1. `python -m pytest` passa e `analyze_rq1_rq2.py`, `python -m experiment.analysis.rq3`, `python -m experiment.analysis.mi_prompts` e `generate_figures.py` rodam sem gerar diff no repositório.
2. Nenhum comando documentado no README apaga ou reescreve conteúdo manual (`generate_design_report.py` resolvido).
3. `data/*.csv` estão idênticos aos de `fab7915`, ou qualquer mudança está justificada em commit com Issue.
4. O relatório tem hipóteses na introdução, Goal e justificativa das métricas, versões (Python, Radon, jscpd, Claude Code/Sonnet 5), as ameaças do enunciado (aprendizado, **familiaridade**, **vazamento descrito corretamente**, memorização), a divergência do modelo de Issues e a data de entrega.
5. Todo hash citado em `docs/` existe em `main` (`git merge-base --is-ancestor <hash> main`).
6. Cada número do relatório vem de um arquivo em `results/` ou `docs/analysis_rq1_rq2.md` (já verdadeiro hoje; manter).
7. Em S01, S02 e S03, cada um dos três tem ≥ 1 Issue da sprint como Assignee com commit de código que referencia essa Issue.
8. Nenhuma Issue com trabalho entregue fica aberta, e nenhuma Issue fica fechada antes do respectivo artefato sem comentário explicando.
9. Existe o snapshot do Kanban da S03.
10. Toda inconsistência dos §15 e §16 está corrigida ou declarada explicitamente no relatório.

---

## 23. Conclusão da auditoria

**Tecnicamente, o experimento está completo e é reproduzível.** Os dados são coerentes entre si e com o código. As análises estatísticas seguem o enunciado (mediana/IQR, Wilcoxon pareado, censura, outliers mantidos, LOC como controle). O relatório separa descrição e inferência e não extrapola: "H0 não rejeitada" nas três RQs, com o piso de p explicado.

**O que falta é de processo e de coerência documental, e parte disso afeta a nota diretamente:** a parcela individual de Guilherme na S03 está em risco, o board está desatualizado, o relatório omite ou descreve de forma errada duas ameaças exigidas (familiaridade e vazamento), não declara a divergência do modelo de Issues e cita hashes que não existem em `main`. Nenhuma dessas correções exige mexer nos dados ou nos resultados. São ajustes de texto, de board e um commit legítimo de Guilherme na S03.

**Limites desta auditoria:** não tive acesso ao board do GitHub Projects (o token não tem `read:project`), não li logs de sessão do assistente (não existem) e não verifiquei a autoria real além do que o git registra.

---

## 24. Registro da etapa de correção técnica/documental (2026-09-24)

> Nenhum commit, push, merge ou alteração no GitHub/Kanban foi feito nesta etapa. `data/trials.csv`, `data/static_metrics.csv` e `data/prompts/` estão sem diff.

### 24.1 O que foi corrigido

| Req. | Problema | Arquivo(s) | Correção | Status |
|---|---|---|---|---|
| R42 | `generate_design_report.py` apagava 120 linhas manuais | `experiment/config/design_report.py`, `generate_design_report.py`, `docs/experiment_design.md`, `tests/test_experiment_design.py` | Texto manual passou para blocos `<!-- manual:start/end -->`, que o gerador reinsere; um bloco sem âncora é anexado, não descartado; se a regeneração fosse perder qualquer outra linha, o script para sem gravar (`--force` para forçar). Tabela de atribuição agrupada ("kata-01, kata-03 e kata-05"). Validado: 2 execuções seguidas sem diff; linha solta fora de bloco → exit 1 sem gravar. 5 testes novos | [x] resolvido |
| R53 | Hashes da história antiga | `docs/relatorio.md`, `docs/experiment_design.md`, `experiment/config/lab02_design.py` | `e9478c3`→`906bafc`, `0aff185`→`8684477`, `c826baa`→`07398a7`, `805bb72`→`c30be82`, `485bc09/faff5d4/f79eb52/991cf83`→`3d6cae6/66ae97f/05574dd/27fcebf`; nota explicando a reescrita. Todo hash citado agora existe em `main` (exceto os da nota explicativa, de propósito) | [x] resolvido |
| I5 | Datas de commits erradas no desenho | `docs/experiment_design.md` | `906bafc` = 2026-09-06; `c30be82` = 2026-09-16 | [x] resolvido |
| R44 | Hipóteses fora da introdução | `docs/relatorio.md` §1.2 | Tabela H0/H1/teste das 3 RQs, idêntica ao desenho | [x] resolvido |
| R45 | GQM e justificativa das métricas | `docs/relatorio.md` §1.1 | Goal com objeto, propósito, foco, ponto de vista e contexto; tabela RQ → métrica → o que mede → por que responde | [x] resolvido |
| R49 | Familiaridade com IA ausente | `docs/relatorio.md` §2.2, §2.6, §4.2 | Tabela dos níveis declarados com a origem de cada registro; tratado como **autorrelato**, não medição | [x] resolvido |
| R24 | Vazamento descrito como mitigado | `docs/relatorio.md` §2.2, §2.3, §2.6, §4.2; `docs/experiment_design.md` (bloco de status); `docs/katas.md` | Removido "sem experiência prévia"; separado **disponível** (comprovado) × **acessado** × **usado** (não comprovados); ameaça declarada como não mitigada e não mensurável | [x] resolvido (documentação) |
| R25 | Modelo de Issues não declarado | `docs/relatorio.md` §2.4 | Divergência do enunciado declarada como tal, com a justificativa do grupo; nada foi reconstruído retroativamente | [x] resolvido (documentação) |
| R11/R43/R46 | Versões e ambiente | `docs/relatorio.md` §2.4, `README.md` | Tabela "fixado × comprovado": Radon 6.0.1 e jscpd 4.0.5 comprovados por trial; Python mínimo 3.10, análise em 3.14.5, versão dos trials não registrada (só indício local para Marcos: `.pyc` cpython-314 de 2026-09-16); versão do Claude Code e do VS Code **não registradas** | [x] resolvido (limitação declarada) |
| R17 / I14 | Descrição do cronômetro | `docs/relatorio.md` §2.4, §3.2, §4.2; `experiment/analysis/rq1_rq2_report.py` → `docs/analysis_rq1_rq2.md` | Descritos os dois modos (ENTER / `--kata-path`); modo por trial não registrado; tempos de Guilherme descritos como **registrados manualmente**, formato igual ao impresso no terminal, sem evidência de transcrição. Estatísticas regeneradas sem mudança numérica | [x] resolvido |
| R54 | Prompts descritos como coleta interativa | `docs/relatorio.md` §2.4 | Descritos como autorrelato em parte retrospectivo, com commit e data de cada participante; o tipo "correção de erros de teste" (Marcos) não é opção do `register_prompts.py` → não saiu do script | [x] resolvido |
| R65 | Contagens erradas em `katas.md` | `docs/katas.md` | "5 e 6" → "5 a 7" (5/6/7/6/7/5, 36, conferido com `pytest --collect-only`); tabela (a): kata-05 = 7, kata-06 = 5; corrigida também a frase "segundo menor LOC" (kata-01 é o 4º menor, e a CC 4 é a menor, empatada com kata-05); ordem de Marcos marcada como presumida. **Testes não alterados** | [x] resolvido |
| R07 | Busca de baixa indexação prometida | `docs/katas.md`, `docs/relatorio.md` §2.3 | Declarado que a busca **não foi registrada** (nada foi inventado) | [x] resolvido (limitação declarada) |
| I12 | Referência a `AUDITORIA_VISUALIZACAO.md` inexistente | `generate_figures.py`, `experiment/visualization/report_figures.py` | Referência removida das docstrings; nenhum arquivo foi criado para satisfazê-la | [x] resolvido |
| R50 | Redação da conclusão | `docs/relatorio.md` §5 | "instrumentação automática" → "parcialmente manual"; recomendação (3) reescrita (quadrado latino + piloto, em vez de repetir o kata); recomendações (5) e (6) adicionadas | [x] resolvido |
| — | Erro da própria auditoria | este documento §5, §9.1 | `prompt_records.csv` tem **12** linhas, não 18 | [x] corrigido |

### 24.2 Verificações sem correção necessária

| Item | Resultado |
|---|---|
| MI | O relatório usa a série "como coletado" como principal e a "harmonizada" (só `solution.py`, recalculada do código em `source_integrity_check.csv`) como sensibilidade; as duas convenções estão documentadas em §2.4 e §3.4; `python -m experiment.analysis.rq3` reproduz as duas séries sem diff. Nenhum valor foi alterado |
| `experiment/visualization/boxplots.py` | **redundante**: só `tests/test_figures.py` o importa; mantido (registro do entregável da #17) |
| `results/rq3/figures/` | **redundante**: geradas por `rq3.py`, não usadas no relatório; o README agora diz que são auxiliares |
| `seaborn` | **não utilizado** (fixado em `requirements.txt`); mantido — o enunciado cita "Matplotlib/Seaborn" |
| `GRAFICOS_CONCEITOS.md` | material de apoio não versionado, derivado do PDF abaixo; não é artefato do LAB02 |
| `trab-final-pdf (1).pdf` | **material externo de outro grupo** (slides "Trabalho Final — Grupo 1"); não versionar |
| Participação de Guilherme na S03 | Verificado o histórico: após 2026-09-17, o único commit de Guilherme é `b6daa49` (#22, Relatório Final). **Não existe artefato de código da S03 de autoria dele** que possa ser apenas documentado; a pendência exige trabalho real novo na etapa posterior |

### 24.3 Pendências para as próximas etapas

**Git / commits (⚠️ AÇÃO POSTERIOR)**
- Commitar, com referência a Issue: código do gerador + testes (`experiment/config/*`, `generate_design_report.py`, `tests/test_experiment_design.py`), relatório (`docs/relatorio.md`, #21/#22/#23), documentação (`docs/experiment_design.md`, `docs/katas.md`, `README.md`), `docs/analysis_rq1_rq2.md` + `rq1_rq2_report.py` (#15), docstrings de figuras (#17) e este documento.
- Não versionar `trab-final-pdf (1).pdf` nem `GRAFICOS_CONCEITOS.md`.
- Não apagar as branches remotas `feature/*` (guardam os hashes antigos).

**GitHub / Kanban (⚠️ AÇÃO POSTERIOR)**
- Guilherme: tarefa real da S03, com artefato de código e commit referenciando a Issue (ex.: #27).
- Fechar #15, #17, #18, #21 com comentário apontando os commits; comentar o histórico da #10 (fechada em 09-09, dados em 09-17).
- Label `lab02` na #41; mover #20 para o milestone "Relatório Final".
- Comentários de Arthur e Guilherme confirmando assistente usado e familiaridade; Arthur explicando o motivo do desvio de ordem.
- Conferir o board no navegador (o token local não tem `read:project`).

**Snapshot (⚠️ AÇÃO POSTERIOR)**
- Gerar o snapshot da S03 (#27) com `generate_kanban_snapshot.py` **depois** de atualizar o board.

**Outras**
- Preencher a data de entrega no relatório.
- Revisão cruzada e exportação em PDF (#23).
- Nova auditoria final após os commits (conferir de novo os hashes citados, porque os commits novos não mudam os antigos).

---

## 25. Pendências finais do relatório (2026-09-24)

> Referência: `docs/auditoria-relatorio-final.md` (veredito `APTO COM PENDÊNCIAS`). Sem commit, sem alteração no GitHub/Kanban, `data/` sem diff.

| ID | Pendência | Situação | O que foi feito |
|---|---|---|---|
| P1 | Data de entrega | [x] resolvido | Cabeçalho do relatório: **24/09/2026** |
| P2 | Limite de WIP | [x] resolvido | "Configuração do processo — GitHub Projects": **WIP = 6 itens na coluna In progress**. Justificativa registrada de forma mínima: "valor definido pelo grupo para a configuração do quadro". Nenhuma justificativa metodológica foi acrescentada. Observação: o template de referência (`exemplo_relatorio_lab-1.md`, Lab01) **também usa WIP = 6** e justifica o valor como "2 por integrante"; por isso não foi usada a frase de que o template "não estabelecia um limite de WIP" |
| P6 | Procedência de Batella et al. (2026) | [x] resolvido — **referência mantida** | Há evidência de uso anterior à auditoria: a frase "Muitos testes? Corrija (Bonferroni / FDR)" já era citada entre aspas no código versionado `experiment/analysis/rq3_report.py` e em `results/rq3/rq3_summary.md` (commit `0d28068`, #16, 2026-09-23) e no relatório (commit `c410d0d`, #21); `GRAFICOS_CONCEITOS.md` (local, 2026-09-17) foi extraído do mesmo PDF. Referência completada com os dados que constam no PDF (título, "Trabalho Final — Grupo 1", PUC Minas, Engenharia de Software, jun. 2026, 98 slides); as duas citações no texto (§3.2) são trechos literais dos slides |
| P3 | Print do Kanban | ⚠️ AÇÃO POSTERIOR | Marcador explícito mantido no relatório: **[PRINT DO KANBAN A INSERIR APÓS A FINALIZAÇÃO DAS TAREFAS PENDENTES E ATUALIZAÇÃO DO QUADRO]** |

**Ainda pendente (⚠️ AÇÃO POSTERIOR):**
- print final do Kanban (P3), só depois que as tarefas em andamento forem de fato concluídas e movidas para Done;
- atualização do board e snapshot da S03 (#27);
- tarefas de processo da Seção 24.3 (commit das correções, participação de Guilherme na S03, status das Issues, confirmações escritas, revisão cruzada e PDF — #23);
- o PDF `trab-final-pdf (1).pdf` citado como Batella et al. (2026) não está versionado: se a banca pedir a fonte, o grupo precisa apresentá-la (versionar ou não um material de outro grupo é decisão do grupo);
- `results/rq3/rq3_summary.md` (saída gerada, já validada) ainda chama esse material de "material da disciplina"; não foi alterado nesta etapa.

