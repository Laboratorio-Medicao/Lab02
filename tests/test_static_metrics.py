from pathlib import Path

import pytest

from experiment.collection.static_metrics import collect_static_metrics

SAMPLE_KATA = Path(__file__).parent / "fixtures" / "sample_kata"


class TestCollectStaticMetrics:
    def test_collects_loc_cc_and_mi_for_sample_kata(self):
        metrics = collect_static_metrics(SAMPLE_KATA)

        assert metrics.loc > 0
        assert metrics.cyclomatic_complexity_avg > 0
        assert 0 <= metrics.maintainability_index <= 100

    def test_excludes_test_files_by_default(self):
        without_tests = collect_static_metrics(SAMPLE_KATA)
        with_tests = collect_static_metrics(SAMPLE_KATA, include_tests=True)

        assert with_tests.loc > without_tests.loc

    def test_accepts_a_single_file(self):
        metrics = collect_static_metrics(SAMPLE_KATA / "fizzbuzz.py")

        assert metrics.loc > 0
        assert metrics.cyclomatic_complexity_avg > 0

    def test_raises_when_no_python_files_are_found(self, tmp_path):
        (tmp_path / "readme.txt").write_text("sem código Python aqui")

        with pytest.raises(ValueError):
            collect_static_metrics(tmp_path)

    def test_to_dict_has_expected_shape_and_rounding(self):
        metrics = collect_static_metrics(SAMPLE_KATA)

        as_dict = metrics.to_dict()

        assert set(as_dict) == {"path", "loc", "cyclomatic_complexity_avg", "maintainability_index"}
        assert as_dict["loc"] == metrics.loc
