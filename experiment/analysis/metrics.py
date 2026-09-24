"""Métricas de RQ3 e razões normalizadas por LOC.

As chaves correspondem às colunas de `data/static_metrics.csv` produzidas na
S02 por `experiment/collection/static_metrics.py`.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Metric:
    """Variável dependente de RQ3. MI é a única em que maior é melhor."""

    key: str
    label: str
    unit: str
    higher_is_better: bool
    question: str
    #: Unidade escrita no meio de uma frase; vazia quando a métrica é adimensional.
    inline_unit: str = ""


LOC = Metric(
    key="loc",
    label="LOC",
    unit="linhas",
    higher_is_better=False,
    question="O código produzido possui maior volume?",
    inline_unit="linhas",
)

CYCLOMATIC_COMPLEXITY = Metric(
    key="cyclomatic_complexity_avg",
    label="CC",
    unit="adimensional",
    higher_is_better=False,
    question="O código produzido possui maior complexidade total?",
    inline_unit="",
)

MAINTAINABILITY_INDEX = Metric(
    key="maintainability_index",
    label="MI",
    unit="0–100",
    higher_is_better=True,
    question="O código produzido é mais manutenível?",
    inline_unit="pontos de MI",
)

DUPLICATION = Metric(
    key="duplicated_lines_percent",
    label="Duplicação",
    unit="% de linhas",
    higher_is_better=False,
    question="O código produzido possui mais linhas duplicadas?",
    inline_unit="pontos percentuais",
)

PRIMARY_METRICS = (LOC, CYCLOMATIC_COMPLEXITY, MAINTAINABILITY_INDEX, DUPLICATION)

CC_PER_LOC = Metric(
    key="cc_per_loc",
    label="CC/LOC",
    unit="complexidade por linha",
    higher_is_better=False,
    question="Considerando o tamanho do código, há maior densidade de complexidade?",
    inline_unit="ponto(s) de complexidade por linha",
)

DUPLICATION_PER_LOC = Metric(
    key="duplicated_lines_per_loc",
    label="Linhas duplicadas/LOC",
    unit="fração de linhas",
    higher_is_better=False,
    question="Considerando o tamanho do código, há maior densidade de duplicação?",
    inline_unit="",
)

NORMALIZED_METRICS = (CC_PER_LOC, DUPLICATION_PER_LOC)

NORMALIZATION_NUMERATORS = {
    CC_PER_LOC.key: CYCLOMATIC_COMPLEXITY.key,
    DUPLICATION_PER_LOC.key: "duplicated_lines",
}

ALL_METRICS = PRIMARY_METRICS + NORMALIZED_METRICS


def metric_by_key(key: str) -> Metric:
    for metric in ALL_METRICS:
        if metric.key == key:
            return metric
    raise KeyError(f"métrica desconhecida: {key}")
