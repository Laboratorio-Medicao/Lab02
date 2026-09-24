"""Mann-Whitney (Wilcoxon rank-sum) complementar e exploratório — Issue #17.

Compara todos os trials com IA contra todos sem IA, sem parear. É apenas
exploratório: os trials não são independentes (os mesmos participantes
aparecem nos dois tratamentos — ver `docs/analysis_rq1_rq2.md`), então o
teste confirmatório continua sendo o Wilcoxon pareado da #15.

Segue o padrão de `paired_wilcoxon`: sempre `with_ai` contra `without_ai`,
nessa ordem; sem empates, distribuição exata; com empates, permutação
enumerando todas as partições (`n_resamples=np.inf`). O `"exact"` do scipy
não corrige empates, e o `PermutationMethod()` padrão sorteia reamostragens
quando há mais partições que `n_resamples` — o p mudaria a cada execução.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.stats import PermutationMethod, mannwhitneyu


@dataclass(frozen=True)
class RankSumResult:
    n_with_ai: int
    n_without_ai: int
    alternative: str
    applicable: bool
    method: str | None = None
    statistic: float | None = None
    # Com alternative="two-sided", p_one_sided repete o bilateral (como em PairedTestResult).
    p_one_sided: float | None = None
    p_two_sided: float | None = None


def rank_sum_test(
    with_ai: Sequence[float], without_ai: Sequence[float], alternative: str
) -> RankSumResult:
    values = [round(v, 9) for v in (*with_ai, *without_ai)]
    if len(set(values)) <= 1:
        return RankSumResult(
            n_with_ai=len(with_ai),
            n_without_ai=len(without_ai),
            alternative=alternative,
            applicable=False,
        )

    if len(set(values)) < len(values):
        method, method_name = PermutationMethod(n_resamples=np.inf), "permutação (exato)"
    else:
        method, method_name = "exact", "exato"

    one_sided = mannwhitneyu(with_ai, without_ai, alternative=alternative, method=method)
    # Com empates, cada chamada enumera as C(n₁+n₂, n₁) partições: não repetir à toa.
    two_sided = (
        one_sided
        if alternative == "two-sided"
        else mannwhitneyu(with_ai, without_ai, alternative="two-sided", method=method)
    )
    return RankSumResult(
        n_with_ai=len(with_ai),
        n_without_ai=len(without_ai),
        alternative=alternative,
        applicable=True,
        method=method_name,
        statistic=float(one_sided.statistic),
        p_one_sided=float(one_sided.pvalue),
        p_two_sided=float(two_sided.pvalue),
    )
