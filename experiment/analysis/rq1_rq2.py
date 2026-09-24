"""Análise estatística de RQ1 (tempo até green) e RQ2 (defeitos) — Issue #15.

Consolida `data/trials.csv`, valida os dados contra o desenho do experimento,
calcula a estatística descritiva por tratamento (mediana e IQR) e aplica o
teste de Wilcoxon pareado por participante (desenho within-subject).

Decisões estatísticas:

- O teste confirmatório pareia cada participante consigo mesmo (n = nº de
  participantes): em RQ1, mediana dos tempos com IA contra sem IA; em RQ2,
  média — com a mediana, um único trial com testes falhando entre 3 sumiria
  do par. Unilateral, pois as H1 de RQ1 e RQ2 são direcionais ("a IA
  reduz ...").
- A comparação por kata é apenas descritiva/exploratória: cada kata foi
  resolvido por pessoas diferentes em cada tratamento, então não é pareada.
- Trials censurados (time-box atingido) entram com o tempo travado no
  time-box, nunca são descartados. O tempo real seria ao menos o time-box:
  censura sem IA é conservadora quanto a H1 (subestima o tempo sem IA), mas
  censura com IA favorece H1 (subestima o tempo com IA).
- Quartis via `statistics.quantiles(method="inclusive")`, equivalente ao
  padrão (interpolação linear) do numpy/pandas.
"""
from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from scipy.stats import PermutationMethod, wilcoxon

from experiment.collection.timer import CSV_FIELDNAMES, TrialRecord
from experiment.config.lab02_design import (
    KATAS,
    N_KATAS,
    PARTICIPANTS,
    TIME_BOX_MINUTES,
    TREATMENTS_BY_PARTICIPANT,
)
from experiment.domain.enums import Treatment

ALPHA = 0.05
TIME_BOX_SECONDS = TIME_BOX_MINUTES * 60
DEFAULT_TRIALS_PATH = Path("data/trials.csv")

# `to_row` grava o tempo com 3 casas decimais, então um trial censurado é
# lido como exatamente 2100.000. Caso-limite conhecido: um green em
# 2099,9996 s também seria gravado como 2100.000 e, sem a marca de censura,
# é rejeitado pela validação — nesse caso o CSV precisa ser corrigido à mão.
_CENSORED_TOLERANCE = 0.001

# Participante excluído na verificação de robustez descritiva: seus três
# trials com IA têm tempos quase idênticos (36,781 / 36,824 / 36,757 s),
# confirmados apenas por autorrelato — ver docs/experiment_design.md.
LEAVE_OUT_PARTICIPANT = "Marcos"


class TrialsDataError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Carga e validação
# ---------------------------------------------------------------------------


def load_trials(path: Path = DEFAULT_TRIALS_PATH) -> list[TrialRecord]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != CSV_FIELDNAMES:
            raise TrialsDataError(
                f"Cabeçalho de {path} difere de CSV_FIELDNAMES: {reader.fieldnames}"
            )
        records = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise TrialsDataError(f"{path}, linha {line_number}: colunas a mais que o cabeçalho.")
            try:
                records.append(TrialRecord.from_row(row))
            except (ValueError, KeyError) as error:
                raise TrialsDataError(f"{path}, linha {line_number}: {error}") from error
    validate_trials(records)
    return records


def validate_trials(records: Sequence[TrialRecord]) -> None:
    """Confere os trials contra o desenho do experimento (`lab02_design`)."""
    expected_count = len(PARTICIPANTS) * N_KATAS
    if len(records) != expected_count:
        raise TrialsDataError(
            f"Esperados {expected_count} trials ({len(PARTICIPANTS)} participantes × "
            f"{N_KATAS} katas), encontrados {len(records)}."
        )

    keys = Counter((r.participant, r.kata_id) for r in records)
    duplicates = [key for key, count in keys.items() if count > 1]
    if duplicates:
        raise TrialsDataError(f"Trials duplicados (participante, kata): {duplicates}")

    kata_index = {kata.id: index for index, kata in enumerate(KATAS)}
    tests_total_by_kata: dict[str, set[int]] = {}
    for r in records:
        label = f"{r.participant}/{r.kata_id}"
        if r.participant not in TREATMENTS_BY_PARTICIPANT:
            raise TrialsDataError(f"{label}: participante fora do desenho.")
        if r.kata_id not in kata_index:
            raise TrialsDataError(f"{label}: kata fora do desenho.")
        expected_treatment = TREATMENTS_BY_PARTICIPANT[r.participant][kata_index[r.kata_id]]
        if r.treatment != expected_treatment:
            raise TrialsDataError(
                f"{label}: tratamento {r.treatment.value} difere do desenho "
                f"({expected_treatment.value})."
            )
        if r.test_result is None:
            raise TrialsDataError(f"{label}: resultado dos testes de aceitação ausente.")
        if r.test_result.total <= 0:
            raise TrialsDataError(f"{label}: nenhum teste de aceitação registrado (tests_total=0).")
        if not (math.isfinite(r.elapsed_seconds) and r.elapsed_seconds >= 0):
            raise TrialsDataError(f"{label}: elapsed={r.elapsed_seconds} inválido.")
        # O cronômetro só encerra um trial não censurado no green (todos os
        # testes passando): falha em trial não censurado é registro inconsistente.
        if not r.censored and r.test_result.failing > 0:
            raise TrialsDataError(
                f"{label}: trial não censurado (green) com {r.test_result.failing} teste(s) falhando."
            )
        if r.censored and abs(r.elapsed_seconds - TIME_BOX_SECONDS) > _CENSORED_TOLERANCE:
            raise TrialsDataError(
                f"{label}: censurado, mas elapsed={r.elapsed_seconds} não está "
                f"travado no time-box ({TIME_BOX_SECONDS} s)."
            )
        if not r.censored and r.elapsed_seconds >= TIME_BOX_SECONDS:
            raise TrialsDataError(
                f"{label}: elapsed={r.elapsed_seconds} atinge o time-box, mas o "
                "trial não está marcado como censurado."
            )
        tests_total_by_kata.setdefault(r.kata_id, set()).add(r.test_result.total)

    inconsistent = {k: v for k, v in tests_total_by_kata.items() if len(v) > 1}
    if inconsistent:
        raise TrialsDataError(f"tests_total diverge entre participantes: {inconsistent}")


# ---------------------------------------------------------------------------
# Estatística descritiva
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Summary:
    n: int
    median: float
    mean: float
    q1: float
    q3: float
    minimum: float
    maximum: float

    @property
    def iqr(self) -> float:
        return self.q3 - self.q1


def summarize(values: Sequence[float]) -> Summary:
    if not values:
        raise ValueError("Não é possível resumir uma amostra vazia.")
    if len(values) == 1:
        q1 = q3 = values[0]
    else:
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return Summary(
        n=len(values),
        median=statistics.median(values),
        mean=statistics.fmean(values),
        q1=q1,
        q3=q3,
        minimum=min(values),
        maximum=max(values),
    )


Metric = Callable[[TrialRecord], float]


def elapsed_seconds(record: TrialRecord) -> float:
    return record.elapsed_seconds


def success_rate_percent(record: TrialRecord) -> float:
    return record.test_result.success_rate_percent


def tests_failing(record: TrialRecord) -> float:
    return record.test_result.failing


def _values(records: Sequence[TrialRecord], treatment: Treatment, metric: Metric) -> list[float]:
    return [metric(r) for r in records if r.treatment == treatment]


def summarize_by_treatment(
    records: Sequence[TrialRecord], metric: Metric
) -> dict[Treatment, Summary]:
    return {t: summarize(_values(records, t, metric)) for t in Treatment}


@dataclass(frozen=True)
class ParticipantComparison:
    participant: str
    with_ai: Summary
    without_ai: Summary

    @property
    def difference(self) -> float:
        """Mediana com IA − mediana sem IA (negativo = IA menor)."""
        return self.with_ai.median - self.without_ai.median

    @property
    def ratio(self) -> float | None:
        """Mediana com IA como fração da mediana sem IA."""
        if self.without_ai.median == 0:
            return None
        return self.with_ai.median / self.without_ai.median


def compare_by_participant(
    records: Sequence[TrialRecord], metric: Metric
) -> tuple[ParticipantComparison, ...]:
    participants = [p for p in PARTICIPANTS if any(r.participant == p for r in records)]
    comparisons = []
    for participant in participants:
        own = [r for r in records if r.participant == participant]
        comparisons.append(
            ParticipantComparison(
                participant=participant,
                with_ai=summarize(_values(own, Treatment.WITH_AI, metric)),
                without_ai=summarize(_values(own, Treatment.WITHOUT_AI, metric)),
            )
        )
    return tuple(comparisons)


@dataclass(frozen=True)
class KataComparison:
    """Comparação exploratória por kata — não pareada (pessoas diferentes)."""

    kata_id: str
    with_ai: tuple[tuple[str, float], ...]
    without_ai: tuple[tuple[str, float], ...]

    @property
    def median_with_ai(self) -> float:
        return statistics.median(v for _, v in self.with_ai)

    @property
    def median_without_ai(self) -> float:
        return statistics.median(v for _, v in self.without_ai)


def compare_by_kata(
    records: Sequence[TrialRecord], metric: Metric
) -> tuple[KataComparison, ...]:
    comparisons = []
    for kata in KATAS:
        own = [r for r in records if r.kata_id == kata.id]
        comparisons.append(
            KataComparison(
                kata_id=kata.id,
                with_ai=tuple((r.participant, metric(r)) for r in own if r.treatment == Treatment.WITH_AI),
                without_ai=tuple(
                    (r.participant, metric(r)) for r in own if r.treatment == Treatment.WITHOUT_AI
                ),
            )
        )
    return tuple(comparisons)


@dataclass(frozen=True)
class TukeyResult:
    lower_fence: float
    upper_fence: float
    outliers: tuple[TrialRecord, ...]


def tukey_outliers(
    records: Sequence[TrialRecord], metric: Metric
) -> dict[Treatment, TukeyResult]:
    """Cercas de Tukey (Q1 − 1,5·IQR, Q3 + 1,5·IQR) sobre todos os trials de cada tratamento."""
    results = {}
    for treatment in Treatment:
        own = [r for r in records if r.treatment == treatment]
        summary = summarize([metric(r) for r in own])
        lower = summary.q1 - 1.5 * summary.iqr
        upper = summary.q3 + 1.5 * summary.iqr
        results[treatment] = TukeyResult(
            lower_fence=lower,
            upper_fence=upper,
            outliers=tuple(r for r in own if not lower <= metric(r) <= upper),
        )
    return results


def fully_separated(records: Sequence[TrialRecord], metric: Metric) -> bool:
    """Todo valor com IA é menor que todo valor sem IA?"""
    return max(_values(records, Treatment.WITH_AI, metric)) < min(
        _values(records, Treatment.WITHOUT_AI, metric)
    )


# ---------------------------------------------------------------------------
# Teste de Wilcoxon pareado
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PairedTestResult:
    n_pairs: int
    differences: tuple[float, ...]
    alternative: str
    applicable: bool
    method: str | None = None
    statistic: float | None = None
    p_one_sided: float | None = None
    p_two_sided: float | None = None
    alpha: float = ALPHA

    @property
    def reject_h0(self) -> bool:
        return self.applicable and self.p_one_sided < self.alpha

    @property
    def n_nonzero(self) -> int:
        """Pares efetivamente usados: o scipy (zero_method="wilcox") descarta diferenças zero."""
        return sum(1 for d in self.differences if d != 0)

    @property
    def min_attainable_p(self) -> float:
        """Menor p unilateral possível (todos os sinais iguais): 1/2ⁿ, n = pares não nulos."""
        return 1 / 2**self.n_nonzero

    @property
    def all_same_sign(self) -> bool:
        nonzero = [d for d in self.differences if d != 0]
        return bool(nonzero) and (all(d < 0 for d in nonzero) or all(d > 0 for d in nonzero))

    @property
    def has_power(self) -> bool:
        """Com esse n, o teste consegue ao menos em tese rejeitar H0 a α?"""
        return self.min_attainable_p < self.alpha


def paired_wilcoxon(
    with_ai: Sequence[float],
    without_ai: Sequence[float],
    alternative: str,
    alpha: float = ALPHA,
) -> PairedTestResult:
    """Wilcoxon signed-rank sobre `with_ai − without_ai`, sempre nessa ordem.

    `alternative="less"` testa H1: com IA < sem IA. Sem zeros nem empates
    entre os |d|, usa a distribuição exata; com zeros ou empates, usa
    `PermutationMethod`, que com n pequeno enumera todos os 2ⁿ sinais e
    continua exato. A aproximação normal nunca é usada — não vale com n tão
    pequeno.
    """
    if len(with_ai) != len(without_ai):
        raise ValueError("Amostras pareadas precisam ter o mesmo tamanho.")
    differences = tuple(a - b for a, b in zip(with_ai, without_ai))
    if all(d == 0 for d in differences):
        return PairedTestResult(
            n_pairs=len(differences),
            differences=differences,
            alternative=alternative,
            applicable=False,
            alpha=alpha,
        )

    abs_differences = [round(abs(d), 9) for d in differences]
    has_zeros = 0 in abs_differences
    has_ties = len(set(abs_differences)) < len(abs_differences)
    if has_zeros or has_ties:
        method, method_name = PermutationMethod(), "permutação (exato, 2ⁿ sinais)"
    else:
        method, method_name = "exact", "exato"

    one_sided = wilcoxon(with_ai, without_ai, alternative=alternative, method=method)
    two_sided = wilcoxon(with_ai, without_ai, alternative="two-sided", method=method)
    return PairedTestResult(
        n_pairs=len(differences),
        differences=differences,
        alternative=alternative,
        applicable=True,
        method=method_name,
        statistic=float(one_sided.statistic),
        p_one_sided=float(one_sided.pvalue),
        p_two_sided=float(two_sided.pvalue),
        alpha=alpha,
    )


def participant_wilcoxon(
    comparisons: Sequence[ParticipantComparison],
    alternative: str,
    aggregate: Callable[[Summary], float] = lambda s: s.median,
) -> PairedTestResult:
    """Wilcoxon sobre um valor por participante e tratamento (`aggregate`)."""
    return paired_wilcoxon(
        [aggregate(c.with_ai) for c in comparisons],
        [aggregate(c.without_ai) for c in comparisons],
        alternative=alternative,
    )


def _mean(summary: Summary) -> float:
    return summary.mean


# ---------------------------------------------------------------------------
# Análises por RQ
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Rq1Analysis:
    by_treatment: dict[Treatment, Summary]
    censored_by_treatment: dict[Treatment, int]
    by_participant: tuple[ParticipantComparison, ...]
    by_kata: tuple[KataComparison, ...]
    outliers: dict[Treatment, TukeyResult]
    fully_separated: bool
    test: PairedTestResult
    leave_out_participant: str
    leave_out_by_treatment: dict[Treatment, Summary]
    leave_out_fully_separated: bool
    leave_out_with_ai_times: tuple[float, ...]


@dataclass(frozen=True)
class Rq2Analysis:
    success_rate_by_treatment: dict[Treatment, Summary]
    failing_by_treatment: dict[Treatment, Summary]
    success_rate_by_participant: tuple[ParticipantComparison, ...]
    failing_by_participant: tuple[ParticipantComparison, ...]
    success_rate_test: PairedTestResult
    failing_test: PairedTestResult
    censored_count: int
    trials_with_failures: int


def analyze_rq1(
    records: Sequence[TrialRecord], leave_out: str = LEAVE_OUT_PARTICIPANT
) -> Rq1Analysis:
    by_participant = compare_by_participant(records, elapsed_seconds)
    remaining = [r for r in records if r.participant != leave_out]
    return Rq1Analysis(
        by_treatment=summarize_by_treatment(records, elapsed_seconds),
        censored_by_treatment={
            t: sum(1 for r in records if r.treatment == t and r.censored) for t in Treatment
        },
        by_participant=by_participant,
        by_kata=compare_by_kata(records, elapsed_seconds),
        outliers=tukey_outliers(records, elapsed_seconds),
        fully_separated=fully_separated(records, elapsed_seconds),
        # H1 (RQ1): com IA leva menos tempo.
        test=participant_wilcoxon(by_participant, alternative="less"),
        leave_out_participant=leave_out,
        leave_out_by_treatment=summarize_by_treatment(remaining, elapsed_seconds),
        leave_out_fully_separated=fully_separated(remaining, elapsed_seconds),
        leave_out_with_ai_times=tuple(
            r.elapsed_seconds
            for r in records
            if r.participant == leave_out and r.treatment == Treatment.WITH_AI
        ),
    )


def analyze_rq2(records: Sequence[TrialRecord]) -> Rq2Analysis:
    success_rate_by_participant = compare_by_participant(records, success_rate_percent)
    failing_by_participant = compare_by_participant(records, tests_failing)
    return Rq2Analysis(
        success_rate_by_treatment=summarize_by_treatment(records, success_rate_percent),
        failing_by_treatment=summarize_by_treatment(records, tests_failing),
        success_rate_by_participant=success_rate_by_participant,
        failing_by_participant=failing_by_participant,
        # H1 (RQ2): com IA, taxa de sucesso maior e menos testes falhando.
        # Média por participante: com a mediana, um único trial com falhas
        # entre os 3 de um tratamento não alteraria o par.
        success_rate_test=participant_wilcoxon(
            success_rate_by_participant, alternative="greater", aggregate=_mean
        ),
        failing_test=participant_wilcoxon(
            failing_by_participant, alternative="less", aggregate=_mean
        ),
        censored_count=sum(1 for r in records if r.censored),
        trials_with_failures=sum(1 for r in records if r.test_result.failing > 0),
    )
