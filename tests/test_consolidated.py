import pandas as pd
import pytest

from experiment.analysis.consolidated import ConsolidationError, consolidate
from experiment.analysis.rq1_rq2 import (
    elapsed_seconds,
    load_trials,
    summarize_by_treatment,
)
from experiment.analysis.static_metrics_data import load_static_metrics
from experiment.domain.enums import Treatment
from tests.test_figures import _design_records, _static_records


def test_one_row_per_trial_with_all_columns():
    data = consolidate(_design_records(), _static_records())
    assert len(data) == 18
    assert not data.isna().any().any()
    assert {"elapsed_seconds", "censored", "tests_failing", "loc", "maintainability_index"} <= set(
        data.columns
    )
    assert "_merge" not in data.columns


def test_unmatched_trial_raises():
    static = _static_records()[:-1]
    with pytest.raises(ConsolidationError, match="não correspondem"):
        consolidate(_design_records(), static)


def test_duplicate_key_raises():
    static = _static_records()
    with pytest.raises(pd.errors.MergeError):
        consolidate(_design_records(), static + [static[0]])


def test_medians_match_issue_15_on_real_data_integration():
    records = load_trials()
    data = consolidate(records, load_static_metrics(trials=records))
    expected = summarize_by_treatment(records, elapsed_seconds)
    medians = data.groupby("treatment")["elapsed_seconds"].median()
    for treatment in Treatment:
        assert medians[treatment.value] == pytest.approx(expected[treatment].median)
