"""Carga e teste pareado das métricas estáticas da RQ3 — apoio às figuras (Issue #17).

Lê `data/static_metrics.csv`, valida contra o desenho do experimento e contra
`data/trials.csv`, e aplica o mesmo Wilcoxon pareado por participante da
#15 (`participant_wilcoxon`), bilateral porque a RQ3 pergunta se a IA
"altera" a estrutura do código.

`StaticMetricsRecord` expõe `participant` e `treatment` com os mesmos nomes
de `TrialRecord`, então as funções da #15 (`compare_by_participant`,
`summarize_by_treatment`) funcionam sobre ele sem mudança. Se a análise da
RQ3 (Issue #16) criar a própria versão destes testes, as figuras passam a
consumi-la.
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from experiment.analysis.rq1_rq2 import (
    PairedTestResult,
    compare_by_participant,
    participant_wilcoxon,
)
from experiment.collection.static_metrics import TRIAL_METRICS_FIELDNAMES
from experiment.collection.timer import TrialRecord
from experiment.config.lab02_design import (
    KATAS,
    N_KATAS,
    PARTICIPANTS,
    TREATMENTS_BY_PARTICIPANT,
)
from experiment.domain.enums import Treatment

DEFAULT_STATIC_METRICS_PATH = Path("data/static_metrics.csv")


class StaticMetricsDataError(ValueError):
    pass


@dataclass(frozen=True)
class StaticMetricsRecord:
    participant: str
    kata_id: str
    treatment: Treatment
    loc: int
    cyclomatic_complexity_avg: float
    maintainability_index: float
    duplicated_lines_percent: float

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "StaticMetricsRecord":
        return cls(
            participant=row["participant"],
            kata_id=row["kata_id"],
            treatment=Treatment(row["treatment"]),
            loc=int(row["loc"]),
            cyclomatic_complexity_avg=float(row["cyclomatic_complexity_avg"]),
            maintainability_index=float(row["maintainability_index"]),
            duplicated_lines_percent=float(row["duplicated_lines_percent"]),
        )


def loc_value(record: StaticMetricsRecord) -> float:
    return record.loc


def cc_value(record: StaticMetricsRecord) -> float:
    return record.cyclomatic_complexity_avg


def mi_value(record: StaticMetricsRecord) -> float:
    return record.maintainability_index


def duplication_value(record: StaticMetricsRecord) -> float:
    return record.duplicated_lines_percent


StaticMetric = Callable[[StaticMetricsRecord], float]

# Ordem dos painéis da figura da RQ3: (extrator, coluna no CSV/tabela
# consolidada, rótulo). LOC é variável de controle, não métrica da RQ3 (ver
# docs/experiment_design.md), e aparece como tal no rótulo.
RQ3_METRICS: tuple[tuple[StaticMetric, str, str], ...] = (
    (cc_value, "cyclomatic_complexity_avg", "CC média"),
    (mi_value, "maintainability_index", "MI como coletado (0–100)"),
    (loc_value, "loc", "LOC (controle)"),
    (duplication_value, "duplicated_lines_percent", "Duplicação (%)"),
)


# ---------------------------------------------------------------------------
# Carga e validação
# ---------------------------------------------------------------------------


def load_static_metrics(
    path: Path = DEFAULT_STATIC_METRICS_PATH,
    trials: Sequence[TrialRecord] | None = None,
) -> list[StaticMetricsRecord]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != TRIAL_METRICS_FIELDNAMES:
            raise StaticMetricsDataError(
                f"Cabeçalho de {path} difere de TRIAL_METRICS_FIELDNAMES: {reader.fieldnames}"
            )
        records = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise StaticMetricsDataError(f"{path}, linha {line_number}: colunas a mais que o cabeçalho.")
            try:
                records.append(StaticMetricsRecord.from_row(row))
            except (ValueError, KeyError) as error:
                raise StaticMetricsDataError(f"{path}, linha {line_number}: {error}") from error
    validate_static_metrics(records, trials)
    return records


def validate_static_metrics(
    records: Sequence[StaticMetricsRecord],
    trials: Sequence[TrialRecord] | None = None,
) -> None:
    """Confere as métricas contra o desenho (`lab02_design`) e, se dados, contra os trials."""
    expected_count = len(PARTICIPANTS) * N_KATAS
    if len(records) != expected_count:
        raise StaticMetricsDataError(
            f"Esperadas {expected_count} linhas de métricas ({len(PARTICIPANTS)} participantes × "
            f"{N_KATAS} katas), encontradas {len(records)}."
        )

    keys = Counter((r.participant, r.kata_id) for r in records)
    duplicates = [key for key, count in keys.items() if count > 1]
    if duplicates:
        raise StaticMetricsDataError(f"Métricas duplicadas (participante, kata): {duplicates}")

    kata_index = {kata.id: index for index, kata in enumerate(KATAS)}
    for r in records:
        label = f"{r.participant}/{r.kata_id}"
        if r.participant not in TREATMENTS_BY_PARTICIPANT:
            raise StaticMetricsDataError(f"{label}: participante fora do desenho.")
        if r.kata_id not in kata_index:
            raise StaticMetricsDataError(f"{label}: kata fora do desenho.")
        expected_treatment = TREATMENTS_BY_PARTICIPANT[r.participant][kata_index[r.kata_id]]
        if r.treatment != expected_treatment:
            raise StaticMetricsDataError(
                f"{label}: tratamento {r.treatment.value} difere do desenho "
                f"({expected_treatment.value})."
            )
        # Um NaN passaria despercebido: a mediana do pandas o ignora, a do
        # `statistics` não — figura e teste pareado divergiriam em silêncio.
        for name, value, low, high in (
            ("loc", r.loc, 0, math.inf),
            ("cyclomatic_complexity_avg", r.cyclomatic_complexity_avg, 0, math.inf),
            ("maintainability_index", r.maintainability_index, 0, 100),
            ("duplicated_lines_percent", r.duplicated_lines_percent, 0, 100),
        ):
            if not (math.isfinite(value) and low <= value <= high):
                raise StaticMetricsDataError(f"{label}: {name}={value} inválido.")

    if trials is not None:
        metric_keys = {(r.participant, r.kata_id, r.treatment) for r in records}
        trial_keys = {(t.participant, t.kata_id, t.treatment) for t in trials}
        missing = sorted(trial_keys - metric_keys, key=str)
        extra = sorted(metric_keys - trial_keys, key=str)
        if missing or extra:
            raise StaticMetricsDataError(
                f"Métricas e trials não correspondem. Sem métricas: {missing}; sem trial: {extra}."
            )


# ---------------------------------------------------------------------------
# Teste pareado (RQ3)
# ---------------------------------------------------------------------------


def rq3_tests(records: Sequence[StaticMetricsRecord]) -> dict[str, PairedTestResult]:
    """Wilcoxon pareado por participante (mediana), bilateral, para cada métrica da RQ3."""
    return {
        label: participant_wilcoxon(
            compare_by_participant(records, metric), alternative="two-sided"
        )
        for metric, _, label in RQ3_METRICS
    }
