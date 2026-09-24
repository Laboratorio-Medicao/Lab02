"""Tabela consolidada do experimento (pandas) — base das figuras da Issue #17.

Junta, numa linha por trial, o tempo e os testes (`data/trials.csv`) com as
métricas estáticas (`data/static_metrics.csv`). Parte dos registros já
validados por `load_trials` (#15) e `load_static_metrics`, em vez de reler os
CSVs: a validação contra o desenho do experimento continua num lugar só.

O merge é `outer` com `indicator=True` e `validate="one_to_one"`: uma chave
duplicada levanta `MergeError`, e uma linha sem par em um dos lados levanta
`ConsolidationError` — nada é descartado em silêncio.
"""
from __future__ import annotations

from typing import Sequence

import pandas as pd

from experiment.analysis.static_metrics_data import StaticMetricsRecord
from experiment.collection.timer import TrialRecord

KEYS = ["participant", "kata_id", "treatment"]


class ConsolidationError(ValueError):
    pass


def trials_frame(trials: Sequence[TrialRecord]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant": t.participant,
                "kata_id": t.kata_id,
                "treatment": t.treatment.value,
                "elapsed_seconds": t.elapsed_seconds,
                "censored": t.censored,
                "tests_total": t.test_result.total,
                "tests_failing": t.test_result.failing,
                "success_rate_percent": t.test_result.success_rate_percent,
            }
            for t in trials
        ]
    )


def static_metrics_frame(records: Sequence[StaticMetricsRecord]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant": r.participant,
                "kata_id": r.kata_id,
                "treatment": r.treatment.value,
                "loc": r.loc,
                "cyclomatic_complexity_avg": r.cyclomatic_complexity_avg,
                "maintainability_index": r.maintainability_index,
                "duplicated_lines_percent": r.duplicated_lines_percent,
            }
            for r in records
        ]
    )


def consolidate(
    trials: Sequence[TrialRecord], static_records: Sequence[StaticMetricsRecord]
) -> pd.DataFrame:
    """Uma linha por trial, com tempo, testes e métricas estáticas, ordenada pelas chaves."""
    merged = pd.merge(
        trials_frame(trials),
        static_metrics_frame(static_records),
        on=KEYS,
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    unmatched = merged[merged["_merge"] != "both"]
    if not unmatched.empty:
        raise ConsolidationError(
            "Trials e métricas estáticas não correspondem: "
            f"{unmatched[KEYS + ['_merge']].to_dict('records')}"
        )
    return merged.drop(columns="_merge").sort_values(KEYS, ignore_index=True)
