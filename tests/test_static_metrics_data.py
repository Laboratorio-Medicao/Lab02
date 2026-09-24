import csv

import pytest

from experiment.analysis.rq1_rq2 import load_trials
from experiment.analysis.static_metrics_data import (
    StaticMetricsDataError,
    StaticMetricsRecord,
    load_static_metrics,
    rq3_tests,
)
from experiment.collection.static_metrics import TRIAL_METRICS_FIELDNAMES
from experiment.collection.timer import AcceptanceTestResult, TrialRecord
from experiment.config.lab02_design import KATAS, TREATMENTS_BY_PARTICIPANT
from experiment.domain.enums import Treatment

WITH_AI = Treatment.WITH_AI
WITHOUT_AI = Treatment.WITHOUT_AI


def _record(participant, kata_id, treatment, elapsed, censored=False, passing=5, total=5):
    return TrialRecord(
        participant=participant,
        kata_id=kata_id,
        treatment=treatment,
        elapsed_seconds=elapsed,
        censored=censored,
        test_result=AcceptanceTestResult(passing=passing, total=total),
    )


def _static(participant, kata_id, treatment, loc=10, cc=5.0, mi=70.0, dup=0.0):
    return StaticMetricsRecord(participant, kata_id, treatment, loc, cc, mi, dup)


def _design_static(values=None):
    """18 linhas válidas, seguindo TREATMENTS_BY_PARTICIPANT; `values(p, i, t)` → kwargs."""
    records = []
    for participant, treatments in TREATMENTS_BY_PARTICIPANT.items():
        for index, (kata, treatment) in enumerate(zip(KATAS, treatments)):
            kwargs = values(participant, index, treatment) if values else {}
            records.append(_static(participant, kata.id, treatment, **kwargs))
    return records


def _design_trials():
    return [
        _record(r.participant, r.kata_id, r.treatment, 100.0) for r in _design_static()
    ]


def _write_csv(path, records, fieldnames=TRIAL_METRICS_FIELDNAMES):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "participant": r.participant,
                    "kata_id": r.kata_id,
                    "treatment": r.treatment.value,
                    "path": "",
                    "loc": r.loc,
                    "cyclomatic_complexity_avg": r.cyclomatic_complexity_avg,
                    "cc_mi_tool": "radon",
                    "cc_mi_tool_version": "6.0.1",
                    "maintainability_index": r.maintainability_index,
                    "duplicated_lines": 0,
                    "duplicated_lines_percent": r.duplicated_lines_percent,
                    "duplicate_blocks": 0,
                    "total_lines": r.loc,
                    "duplication_tool": "jscpd",
                    "duplication_tool_version": "4.0.5",
                }
            )


class TestLoadStaticMetrics:
    def test_loads_valid_file(self, tmp_path):
        path = tmp_path / "static_metrics.csv"
        records = _design_static()
        _write_csv(path, records)
        assert load_static_metrics(path, trials=_design_trials()) == records

    def test_header_must_match_collection_fieldnames(self, tmp_path):
        path = tmp_path / "static_metrics.csv"
        _write_csv(path, _design_static(), fieldnames=TRIAL_METRICS_FIELDNAMES[:-1])
        with pytest.raises(StaticMetricsDataError, match="Cabeçalho"):
            load_static_metrics(path)

    def test_duplicate_raises(self, tmp_path):
        path = tmp_path / "static_metrics.csv"
        records = _design_static()
        _write_csv(path, records[:-1] + [records[0]])
        with pytest.raises(StaticMetricsDataError, match="duplicadas"):
            load_static_metrics(path)

    def test_treatment_outside_design_raises(self, tmp_path):
        path = tmp_path / "static_metrics.csv"
        records = _design_static()
        first = records[0]
        flipped = WITHOUT_AI if first.treatment == WITH_AI else WITH_AI
        _write_csv(path, [_static(first.participant, first.kata_id, flipped)] + records[1:])
        with pytest.raises(StaticMetricsDataError, match="difere do desenho"):
            load_static_metrics(path)

    @pytest.mark.parametrize(
        "field, value",
        [("mi", float("nan")), ("mi", 120.0), ("dup", -1.0), ("loc", -3), ("cc", float("inf"))],
    )
    def test_invalid_metric_values_raise(self, tmp_path, field, value):
        path = tmp_path / "static_metrics.csv"
        records = _design_static()
        first = records[0]
        bad = _static(first.participant, first.kata_id, first.treatment, **{field: value})
        _write_csv(path, [bad] + records[1:])
        with pytest.raises(StaticMetricsDataError, match="inválido"):
            load_static_metrics(path)

    def test_key_missing_from_trials_raises(self, tmp_path):
        path = tmp_path / "static_metrics.csv"
        _write_csv(path, _design_static())
        trials = _design_trials()
        orphan = trials[0]
        trials[0] = _record(orphan.participant, "kata-99", orphan.treatment, 100.0)
        with pytest.raises(StaticMetricsDataError, match="não correspondem"):
            load_static_metrics(path, trials=trials)

    def test_real_data_matches_trials_integration(self):
        records = load_static_metrics(trials=load_trials())
        assert len(records) == 18


class TestRq3Tests:
    def test_all_zero_differences_are_not_applicable(self):
        results = rq3_tests(_design_static())
        assert all(not result.applicable for result in results.values())

    def test_tied_differences_use_permutation_and_are_two_sided(self):
        # CC com IA 2 menor para dois participantes e 3 menor para o terceiro: empate em |d|.
        drop = {"Guilherme": 2.0, "Arthur": 3.0, "Marcos": 2.0}

        def values(participant, index, treatment):
            cc = 8.0 - drop[participant] if treatment == WITH_AI else 8.0
            return {"cc": cc}

        result = rq3_tests(_design_static(values))["CC média"]
        assert result.applicable
        assert result.alternative == "two-sided"
        assert result.method.startswith("permutação")
        assert result.p_two_sided == pytest.approx(0.25)
