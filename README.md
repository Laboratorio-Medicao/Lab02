# Lab02 — Assistentes de IA vs. Codificação Manual

Experimento controlado comparando o uso de assistente de IA generativa contra
codificação manual na resolução de katas, avaliando tempo de resolução
(RQ1), defeitos (RQ2) e estrutura do código produzido (RQ3). Enunciado
completo em [`docs/enunciado/lab02.md`](docs/enunciado/lab02.md); desenho do
experimento em [`docs/experiment_design.md`](docs/experiment_design.md).

## Ambiente de execução

Fixado para **todos os trials**, para que os tratamentos sejam comparáveis
dentro do experimento:

| Item | Escolha |
|---|---|
| Linguagem | Python 3.10+ (compatível com Radon, a ferramenta de métricas estáticas escolhida) |
| IDE | Visual Studio Code |
| Assistente de IA | Claude Code — modelo Claude Sonnet 5 (`claude-sonnet-5`) |
| Ferramenta de métricas estáticas | [Radon](https://radon.readthedocs.io/) 6.x (`cc`, `mi`, LOC) |
| Testes | pytest 8.x |

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
```

## Rodando os testes

```bash
source .venv/bin/activate
python -m pytest
```

## Scripts de preparação (S01)

**Cronômetro de trial** (time-to-green, time-box de 35 min — [Issue #5](../../issues/5)):

```bash
python -m experiment.collection.timer <participante> <kata_id> <with_ai|without_ai> [--output data/trials.csv]
```

**Métricas estáticas via Radon** (complexidade ciclomática, índice de
manutenibilidade e LOC — [Issue #5](../../issues/5)):

```bash
python -m experiment.collection.static_metrics <caminho-do-kata> [--json] [--include-tests]
```

**Relatório do desenho do experimento** ([Issue #3](../../issues/3)):

```bash
python generate_design_report.py
```

## Reprodutibilidade

- As dependências e versões exatas estão fixadas em [`requirements.txt`](requirements.txt).
- O assistente de IA e sua versão (Claude Sonnet 5) são registrados aqui para
  permitir reprodução/replicação do experimento, conforme exigido na
  metodologia do Relatório Final.
- `.venv/` não é versionado (ver `.gitignore`); recrie o ambiente com os
  passos acima antes de rodar qualquer script do experimento.
