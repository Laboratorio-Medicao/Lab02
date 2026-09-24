"""Estatística descritiva e inferencial pareada para as métricas do LAB02.

Mediana e IQR em vez de média e desvio-padrão (enunciado, linha 57) e Wilcoxon
signed-rank, o teste fechado no desenho da S01. O módulo é genérico — não
conhece RQ3 — para servir também às análises de RQ1/RQ2 (Issue #15).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import pandas as pd
from scipy.stats import rankdata, wilcoxon

#: Decisão pós-hoc da S03: nenhum artefato anterior do projeto fixou um α.
ALPHA = 0.05

Q1_QUANTILE = 0.25
Q3_QUANTILE = 0.75

#: Limite em que o SciPy troca a distribuição exata pela aproximação normal.
EXACT_METHOD_MAX_PAIRS = 50

BONFERRONI = "bonferroni"
BENJAMINI_HOCHBERG = "benjamini-hochberg"
MAX_P_VALUE = 1.0


def describe(values: pd.Series) -> dict[str, float]:
    """Resumo por mediana/IQR, com mínimo e máximo."""
    q1 = values.quantile(Q1_QUANTILE)
    q3 = values.quantile(Q3_QUANTILE)
    return {
        "n": int(values.count()),
        "median": values.median(),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "min": values.min(),
        "max": values.max(),
    }


def describe_by_group(
    observations: pd.DataFrame, value_column: str, group_column: str, groups: tuple[str, ...]
) -> pd.DataFrame:
    rows = []
    for group in groups:
        summary = describe(observations.loc[observations[group_column] == group, value_column])
        rows.append({group_column: group, **summary})
    return pd.DataFrame(rows)


def build_pairs(
    observations: pd.DataFrame,
    value_column: str,
    pairing_column: str,
    treatment_column: str,
    treatments: tuple[str, str],
) -> pd.DataFrame:
    """Monta os pares do Wilcoxon agregando cada célula pela mediana.

    Unidades sem os dois tratamentos são descartadas: não formam par.
    """
    baseline, comparison = treatments
    cells = (
        observations.groupby([pairing_column, treatment_column])[value_column]
        .median()
        .unstack(treatment_column)
    )
    missing = [column for column in treatments if column not in cells.columns]
    if missing:
        raise ValueError(f"tratamento ausente nos dados: {', '.join(missing)}")

    pairs = cells[[baseline, comparison]].dropna().reset_index()
    pairs["difference"] = pairs[comparison] - pairs[baseline]
    return pairs


@dataclass(frozen=True)
class WilcoxonResult:
    """Resultado de um Wilcoxon signed-rank, com tamanho de efeito.

    `rank_biserial` = (W⁺ − W⁻)/(W⁺ + W⁻), preferível a r = Z/√N com poucos
    pares por não depender da aproximação normal. `hodges_lehmann` é a
    pseudomediana das diferenças, na unidade original da métrica.
    """

    metric: str
    pairing_unit: str
    n_pairs: int
    n_nonzero_pairs: int
    statistic: float | None
    p_value: float | None
    method: str
    rank_biserial: float | None
    median_difference: float | None
    hodges_lehmann: float | None
    min_achievable_p: float | None
    degenerate: bool
    note: str

    def to_row(self) -> dict:
        return asdict(self)


def rank_biserial_levels(n_nonzero: int) -> tuple[float, ...]:
    """Valores que r_rb pode assumir com `n_nonzero` pares e sem empates.

    As somas de subconjuntos dos postos 1…n são enumeradas em vez de assumidas,
    para que a lista continue correta se a construção dos postos mudar. Com
    poucos pares o conjunto é pequeno, o que limita a resolução da medida.
    """
    if n_nonzero <= 0:
        return ()
    total = n_nonzero * (n_nonzero + 1) // 2
    reachable_sums = {0}
    for rank in range(1, n_nonzero + 1):
        reachable_sums |= {partial + rank for partial in reachable_sums}
    return tuple(sorted((2 * w - total) / total for w in reachable_sums))


def adjust_p_values(p_values: pd.Series, method: str) -> pd.Series:
    """p-valores corrigidos para multiplicidade dentro de uma família de testes.

    Bonferroni controla o erro por família (FWER); Benjamini–Hochberg controla
    a taxa de falsas descobertas (FDR). Testes degenerados, sem p-valor, não
    contam para o tamanho da família.
    """
    observed = p_values.dropna()
    family_size = len(observed)
    adjusted = pd.Series(float("nan"), index=p_values.index, dtype=float)
    if family_size == 0:
        return adjusted

    if method == BONFERRONI:
        adjusted.loc[observed.index] = (observed * family_size).clip(upper=MAX_P_VALUE)
        return adjusted

    if method == BENJAMINI_HOCHBERG:
        ordered = observed.sort_values()
        ranks = range(1, family_size + 1)
        raw = [p * family_size / rank for p, rank in zip(ordered, ranks)]
        monotone = list(pd.Series(raw)[::-1].cummin()[::-1])
        adjusted.loc[ordered.index] = [min(value, MAX_P_VALUE) for value in monotone]
        return adjusted

    raise ValueError(f"método de correção desconhecido: {method}")


def _rank_biserial(differences: pd.Series) -> float:
    """(W⁺ − W⁻) / (W⁺ + W⁻) sobre os pares não-nulos."""
    nonzero = differences[differences != 0]
    ranks = rankdata(nonzero.abs())
    positive = ranks[(nonzero > 0).to_numpy()].sum()
    negative = ranks[(nonzero < 0).to_numpy()].sum()
    total = positive + negative
    return float((positive - negative) / total) if total else 0.0


def _hodges_lehmann(differences: pd.Series) -> float:
    """Pseudomediana: mediana das médias de Walsh das diferenças pareadas."""
    values = differences.to_numpy()
    walsh = [
        (values[i] + values[j]) / 2
        for i in range(len(values))
        for j in range(i, len(values))
    ]
    return float(pd.Series(walsh).median())


def _minimum_two_sided_p(n_nonzero: int) -> float | None:
    """Piso de p do teste exato: 2/2**n, mesmo com todas as diferenças na
    mesma direção. É o que torna a rejeição de H0 impossível com N = 3.
    """
    return 2 ** (1 - n_nonzero) if n_nonzero else None


def paired_wilcoxon(
    pairs: pd.DataFrame,
    metric: str,
    pairing_unit: str,
    treatments: tuple[str, str],
) -> WilcoxonResult:
    """Aplica o Wilcoxon signed-rank bicaudal sobre pares já montados.

    Casos degenerados — nenhum par, ou todas as diferenças iguais a zero — são
    reportados como tal, em vez de propagar o erro do SciPy.
    """
    baseline, comparison = treatments
    differences = pairs["difference"]
    n_pairs = len(differences)
    n_nonzero = int((differences != 0).sum())

    if n_pairs == 0:
        return WilcoxonResult(
            metric, pairing_unit, 0, 0, None, None, "não aplicável", None, None, None,
            None, True, "nenhum par completo disponível",
        )

    if n_nonzero == 0:
        return WilcoxonResult(
            metric, pairing_unit, n_pairs, 0, None, None, "não aplicável",
            0.0, 0.0, 0.0, None, True,
            "todas as diferenças pareadas são exatamente zero — a métrica é "
            "constante entre os tratamentos e o teste não tem o que ordenar",
        )

    # `auto` usa a distribuição exata com poucos pares, inclusive com empates;
    # forçar a aproximação normal aqui daria p-valores abaixo do piso exato.
    result = wilcoxon(
        pairs[comparison], pairs[baseline], alternative="two-sided", method="auto"
    )
    method = "exact" if n_nonzero <= EXACT_METHOD_MAX_PAIRS else "approx"
    has_ties = len(set(differences[differences != 0].abs())) < n_nonzero

    return WilcoxonResult(
        metric=metric,
        pairing_unit=pairing_unit,
        n_pairs=n_pairs,
        n_nonzero_pairs=n_nonzero,
        statistic=float(result.statistic),
        p_value=float(result.pvalue),
        method=method,
        rank_biserial=_rank_biserial(differences),
        median_difference=float(differences.median()),
        hodges_lehmann=_hodges_lehmann(differences),
        min_achievable_p=_minimum_two_sided_p(n_nonzero) if method == "exact" else None,
        degenerate=False,
        note=(
            "há empates entre os módulos das diferenças; o p exato é aproximado "
            "nesse caso"
            if has_ties
            else ""
        ),
    )


def decision(result: WilcoxonResult, alpha: float = ALPHA) -> str:
    if result.degenerate or result.p_value is None:
        return "teste não aplicável"
    if result.p_value < alpha:
        return f"rejeita H0 (α = {alpha})"
    return f"não rejeita H0 (α = {alpha})"


def format_median_iqr(summary: dict[str, float], decimals: int = 2) -> str:
    if math.isnan(summary["median"]):
        return "—"
    return f"{summary['median']:.{decimals}f} ({summary['iqr']:.{decimals}f})"
