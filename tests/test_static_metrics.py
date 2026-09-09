from pathlib import Path

import pytest

from experiment.collection.duplication_metrics import (
    collect_duplication_metrics,
    is_jscpd_available,
)
from experiment.collection.static_metrics import append_trial_metrics, collect_static_metrics

SAMPLE_KATA = Path(__file__).parent / "fixtures" / "sample_kata"

requires_jscpd = pytest.mark.skipif(
    not is_jscpd_available(),
    reason="jscpd não instalado — execute 'npm ci' antes de rodar esta suíte (ver README).",
)


class TestCollectStaticMetrics:
    @requires_jscpd
    def test_collects_loc_cc_and_mi_for_sample_kata(self):
        metrics = collect_static_metrics(SAMPLE_KATA)

        assert metrics.loc > 0
        assert metrics.cyclomatic_complexity_avg > 0
        assert 0 <= metrics.maintainability_index <= 100

    @requires_jscpd
    def test_excludes_test_files_by_default(self):
        without_tests = collect_static_metrics(SAMPLE_KATA)
        with_tests = collect_static_metrics(SAMPLE_KATA, include_tests=True)

        assert with_tests.loc > without_tests.loc
        assert with_tests.duplication.total_lines > without_tests.duplication.total_lines

    @requires_jscpd
    def test_accepts_a_single_file(self):
        metrics = collect_static_metrics(SAMPLE_KATA / "fizzbuzz.py")

        assert metrics.loc > 0
        assert metrics.cyclomatic_complexity_avg > 0

    def test_raises_when_no_python_files_are_found(self, tmp_path):
        (tmp_path / "readme.txt").write_text("sem código Python aqui")

        with pytest.raises(ValueError):
            collect_static_metrics(tmp_path)

    @requires_jscpd
    def test_to_dict_has_expected_shape_and_rounding(self):
        metrics = collect_static_metrics(SAMPLE_KATA)

        as_dict = metrics.to_dict()

        assert set(as_dict) == {
            "path",
            "loc",
            "cyclomatic_complexity_avg",
            "maintainability_index",
            "duplicated_lines",
            "duplicated_lines_percent",
            "duplicate_blocks",
            "total_lines",
            "tool",
            "tool_version",
        }
        assert as_dict["loc"] == metrics.loc

    @requires_jscpd
    def test_appends_trial_metrics_to_csv(self, tmp_path):
        metrics = collect_static_metrics(SAMPLE_KATA)
        output = tmp_path / "static_metrics.csv"

        append_trial_metrics(metrics, "Arthur", "kata-01", "with_ai", output)

        rows = output.read_text(encoding="utf-8").splitlines()
        assert rows[0].startswith("participant,kata_id,treatment")
        assert "Arthur,kata-01,with_ai" in rows[1]
        assert ",0.0," in rows[1]

    @requires_jscpd
    def test_detects_duplicate_lines_between_source_files(self, tmp_path):
        source = """def repeated(value):
    first = value + 1
    second = first + 2
    third = second + 3
    fourth = third + 4
    fifth = fourth + 5
    sixth = fifth + 6
    seventh = sixth + 7
    return seventh
"""
        (tmp_path / "first.py").write_text(source, encoding="utf-8")
        (tmp_path / "second.py").write_text(source, encoding="utf-8")

        metrics = collect_duplication_metrics(tmp_path)

        assert metrics.duplicated_lines > 0
        assert metrics.duplicated_lines_percent > 0
        assert metrics.duplicate_blocks > 0
