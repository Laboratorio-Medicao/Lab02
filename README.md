# Lab02 — Assistentes de IA vs. Codificação Manual

Experimento controlado comparando o uso de assistente de IA generativa contra
codificação manual na resolução de katas, avaliando tempo de resolução
(RQ1), defeitos (RQ2) e estrutura do código produzido (RQ3). Enunciado
completo em [`docs/enunciado/lab02.md`](docs/enunciado/lab02.md); desenho do
experimento em [`docs/experiment_design.md`](docs/experiment_design.md); seleção
e validação dos exercícios em [`docs/katas.md`](docs/katas.md).

## Ambiente de execução

Fixado para **todos os trials**, para que os tratamentos sejam comparáveis
dentro do experimento:

| Item | Escolha |
|---|---|
| Linguagem | Python 3.10+ (compatível com Radon, a ferramenta de métricas estáticas escolhida) |
| IDE | Visual Studio Code |
| Assistente de IA | Claude Code — modelo Claude Sonnet 5 (`claude-sonnet-5`) |
| Ferramenta de métricas estáticas | [Radon](https://radon.readthedocs.io/) 6.x (`cc`, `mi`, LOC) |
| Testes | pytest 9.1.1 (pinado em `requirements.txt`) |

## Instalação e reprodução local

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd Lab02

# 2. Criar e ativar um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Instalar o jscpd usado na métrica de duplicação
npm ci
```

O comando `npm ci` requer Node.js e npm instalados.

## Rodando os testes

```bash
source .venv/bin/activate
python -m pytest
```

Os seis katas e seus testes de aceitação estão em [`katas/`](katas/). Para
executar apenas essa validação:

```bash
python -m pytest katas -q
```

## Scripts de preparação (S01)

**Cronômetro de trial** (time-to-green, time-box de 35 min — [Issue #5](../../issues/5)):

```bash
python -m experiment.collection.timer <participante> <kata_id> <with_ai|without_ai> [--output data/trials.csv]
```

Por padrão, o "green" depende do participante pressionar ENTER quando achar
que os testes passam (autodeclaração). Para confirmar programaticamente que
os testes de aceitação realmente passam — em vez de confiar apenas no
participante —, informe `--kata-path`: o cronômetro roda `pytest` de verdade
sobre esse diretório a cada `--poll-seconds` (padrão: 5s) até obter sucesso ou
o time-box acabar.

```bash
python -m experiment.collection.timer <participante> <kata_id> <with_ai|without_ai> \
  --kata-path katas/kata_01 --poll-seconds 5 --output data/trials.csv
```

**Métricas estáticas via Radon + jscpd** (complexidade ciclomática, índice de
manutenibilidade, LOC e duplicação — [Issue #5](../../issues/5)):

```bash
python -m experiment.collection.static_metrics <caminho-do-trial> --json
python -m experiment.collection.static_metrics <caminho-do-trial> --participant Arthur --kata-id kata-01 --treatment with_ai --output data/static_metrics.csv
```

Por padrão, testes de aceitação não entram nas métricas. O CSV de métricas por
trial pode ser unido a `data/trials.csv` pelas colunas `participant`, `kata_id`
e `treatment`.

**Relatório do desenho do experimento** ([Issue #3](../../issues/3)):

```bash
python generate_design_report.py
```

## Análise de resultados (S03)

**RQ1 e RQ2 — mediana/IQR e Wilcoxon pareado** ([Issue #15](../../issues/15)):

```bash
python analyze_rq1_rq2.py
```

Lê e valida `data/trials.csv` contra o desenho (`experiment/config/lab02_design.py`),
aplica o teste de Wilcoxon pareado por participante e gera
[`docs/analysis_rq1_rq2.md`](docs/analysis_rq1_rq2.md) com p-valores, conclusão
sobre H0, outliers, trials censurados e ressalvas.

**RQ3 — métricas estáticas** ([Issue #16](../../issues/16)): consolida
`data/trials.csv` e `data/static_metrics.csv`, valida os dados, calcula
mediana/IQR por tratamento, aplica Wilcoxon signed-rank pareado com tamanho de
efeito e correção de multiplicidade, normaliza as métricas por LOC e gera as
figuras.

```bash
python -m experiment.analysis.rq3
```

Os artefatos são escritos em `results/rq3/` (use `--output-dir` para mudar o
destino). Os CSVs de `data/` são abertos somente para leitura — a análise nunca
altera os dados brutos.

| Artefato | Conteúdo |
|---|---|
| `rq3_summary.md` | Resposta à RQ3, tabelas principais e interpretação |
| `data_quality_report.md` | Verificações de qualidade, conferência contra o código-fonte e outliers |
| `consolidated_trials.csv` | Os 18 trials com todas as métricas, uma linha por trial |
| `descriptive_statistics.csv` | n, mediana, Q1, Q3, IQR, mínimo e máximo por métrica × tratamento |
| `statistical_tests.csv` | Wilcoxon por métrica e por unidade de pareamento, com p-valor bruto, p ajustado (Bonferroni e Benjamini–Hochberg) e tamanho de efeito |
| `normalized_metrics.csv` | Descritiva das razões por LOC (CC/LOC e duplicação/LOC) |
| `task_allocation_balance.csv` | Dificuldade aparente dos katas de cada lado do par, por participante (confundimento tratamento × tarefa) |
| `source_integrity_check.csv` | CSV coletado na S02 × recomputação via Radon, trial a trial |
| `outliers.csv` | Observações fora de 1,5 × IQR (sinalizadas, não removidas) |
| `figures/*.png` | As cinco figuras de RQ3 (distribuição, comparação pareada, por kata, CC × LOC e complexidade normalizada) |

## Reprodutibilidade

- As dependências e versões exatas estão fixadas em [`requirements.txt`](requirements.txt).
- A versão do jscpd está fixada em [`package-lock.json`](package-lock.json); use
  `npm ci` para reproduzir a instalação.
- O assistente de IA e sua versão (Claude Sonnet 5) são registrados aqui para
  permitir reprodução/replicação do experimento, conforme exigido na
  metodologia do Relatório Final.
- `.venv/` não é versionado (ver `.gitignore`); recrie o ambiente com os
  passos acima antes de rodar qualquer script do experimento.
