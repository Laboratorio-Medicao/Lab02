import hashlib

import matplotlib.pyplot as plt
import pytest

from experiment.analysis.consolidated import consolidate
from experiment.analysis.rq1_rq2 import TIME_BOX_SECONDS, analyze_rq1, analyze_rq2, paired_wilcoxon
from experiment.analysis.static_metrics_data import StaticMetricsRecord, rq3_tests
from experiment.collection.timer import AcceptanceTestResult, TrialRecord
from experiment.config.lab02_design import KATAS, PARTICIPANTS, TREATMENTS_BY_PARTICIPANT
from experiment.domain.enums import Treatment
from experiment.visualization.boxplots import (
    CENSORED_LABEL,
    RQ1_PANEL,
    RQ2_PANELS,
    RQ3_PANELS,
    build_rq1_figure,
    build_rq2_figure,
    build_rq3_figure,
    fmt_p,
    rank_sums,
    save_figure,
    stats_text,
)

WITH_AI = Treatment.WITH_AI
WITHOUT_AI = Treatment.WITHOUT_AI

_WITH_AI_TIMES = (30.0, 40.0, 50.0)
_WITHOUT_AI_TIMES = (600.0, 700.0, 800.0)


def _record(participant, kata_id, treatment, elapsed, censored=False, passing=5, total=5):
    return TrialRecord(
        participant=participant,
        kata_id=kata_id,
        treatment=treatment,
        elapsed_seconds=elapsed,
        censored=censored,
        test_result=AcceptanceTestResult(passing=passing, total=total),
    )


def _design_records(censor_first_without_ai=False):
    records = []
    censored_done = not censor_first_without_ai
    for participant, treatments in TREATMENTS_BY_PARTICIPANT.items():
        with_ai_iter = iter(_WITH_AI_TIMES)
        without_ai_iter = iter(_WITHOUT_AI_TIMES)
        for kata, treatment in zip(KATAS, treatments):
            if treatment == WITH_AI:
                records.append(_record(participant, kata.id, treatment, next(with_ai_iter)))
            elif not censored_done:
                next(without_ai_iter)
                records.append(
                    _record(participant, kata.id, treatment, TIME_BOX_SECONDS, censored=True, passing=3)
                )
                censored_done = True
            else:
                records.append(_record(participant, kata.id, treatment, next(without_ai_iter)))
    return records


def _static_records():
    records = []
    for participant, treatments in TREATMENTS_BY_PARTICIPANT.items():
        for index, (kata, treatment) in enumerate(zip(KATAS, treatments)):
            with_ai = treatment == WITH_AI
            records.append(
                StaticMetricsRecord(
                    participant, kata.id, treatment,
                    loc=10 + index if with_ai else 20 + index,
                    cyclomatic_complexity_avg=4.0 + index % 2,
                    maintainability_index=80.0 - index if with_ai else 75.0 - index,
                    duplicated_lines_percent=0.0,
                )
            )
    return records


def _rq1_tests(records):
    return {RQ1_PANEL[1]: analyze_rq1(records).test}


def _rq2_tests(records):
    rq2 = analyze_rq2(records)
    success_label, failing_label = (label for _, label in RQ2_PANELS)
    return {success_label: rq2.success_rate_test, failing_label: rq2.failing_test}


def _builders(records, static_records):
    """Constrói cada figura sob demanda, para não deixar figuras abertas sem uso."""
    data = consolidate(records, static_records)
    rq1, rq2, rq3 = _rq1_tests(records), _rq2_tests(records), rq3_tests(static_records)
    return {
        "rq1_tempo": lambda: build_rq1_figure(
            data, rq1[RQ1_PANEL[1]], rank_sums(data, (RQ1_PANEL,), rq1)[RQ1_PANEL[1]]
        ),
        "rq2_defeitos": lambda: build_rq2_figure(data, rq2, rank_sums(data, RQ2_PANELS, rq2)),
        "rq3_estrutura": lambda: build_rq3_figure(data, rq3, rank_sums(data, RQ3_PANELS, rq3)),
    }


def _legend_labels(fig):
    labels = [text.get_text() for text in fig.legends[0].get_texts()]
    plt.close(fig)
    return labels


class TestAnnotationText:
    def test_fmt_p_below_one_thousandth(self):
        assert fmt_p(2.06e-5) == "< 0,001"
        assert fmt_p(0.125) == "0,125"

    def test_two_sided_min_attainable_p_with_three_pairs(self):
        paired = paired_wilcoxon([1.0, 2.0, 3.0], [5.0, 7.0, 9.0], alternative="two-sided")
        static = _static_records()
        data = consolidate(_design_records(), static)
        mw = rank_sums(data, RQ3_PANELS, rq3_tests(static))["LOC (controle)"]
        text = stats_text(paired, mw)
        assert "p = 0,250" in text
        assert "mín. possível 0,250" in text.replace("\n", " ")

    def test_mann_whitney_below_threshold_reads_p_less_than(self):
        records = _design_records()
        data = consolidate(records, _static_records())
        mw = rank_sums(data, (RQ1_PANEL,), _rq1_tests(records))[RQ1_PANEL[1]]
        assert "p < 0,001" in stats_text(analyze_rq1(records).test, mw)

    def test_no_variation_note(self):
        records = _design_records()
        data = consolidate(records, _static_records())
        mw = rank_sums(data, RQ2_PANELS, _rq2_tests(records))[RQ2_PANELS[0][1]]
        assert stats_text(analyze_rq2(records).success_rate_test, mw) == (
            "Sem variação — testes não aplicáveis"
        )


class TestLegend:
    def test_one_entry_per_participant_without_censored(self):
        fig = _builders(_design_records(), _static_records())["rq2_defeitos"]()
        assert _legend_labels(fig) == list(PARTICIPANTS)

    def test_censored_entry_only_when_a_trial_is_censored(self):
        records = _design_records(censor_first_without_ai=True)
        fig = _builders(records, _static_records())["rq1_tempo"]()
        assert _legend_labels(fig) == [*PARTICIPANTS, CENSORED_LABEL]

    def test_only_present_participants(self):
        records = [r for r in _design_records() if r.participant != "Marcos"]
        static = [r for r in _static_records() if r.participant != "Marcos"]
        fig = _builders(records, static)["rq1_tempo"]()
        assert "Marcos" not in _legend_labels(fig)


class TestSaveFigures:
    def test_all_figures_are_written(self, tmp_path):
        records = _design_records(censor_first_without_ai=True)
        for name, build in _builders(records, _static_records()).items():
            for path in save_figure(build(), tmp_path / "figures", name):
                assert path.exists() and path.stat().st_size > 0

    @pytest.mark.parametrize("name", ["rq1_tempo", "rq2_defeitos", "rq3_estrutura"])
    def test_output_is_deterministic(self, tmp_path, name):
        digests = []
        for run in ("a", "b"):
            fig = _builders(_design_records(), _static_records())[name]()
            paths = save_figure(fig, tmp_path / run, name)
            digests.append([hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
        assert digests[0] == digests[1]


class TestPanels:
    def test_mann_whitney_follows_paired_test_side(self):
        records = _design_records()
        data = consolidate(records, _static_records())
        rq2 = _rq2_tests(records)
        mws = rank_sums(data, RQ2_PANELS, rq2)
        assert {label: mw.alternative for label, mw in mws.items()} == {
            label: test.alternative for label, test in rq2.items()
        }

    def test_log_scale_rejects_non_positive_values(self):
        records = _design_records()
        records[0] = _record(records[0].participant, records[0].kata_id, records[0].treatment, 0.0)
        with pytest.raises(ValueError, match="escala log"):
            _builders(records, _static_records())["rq1_tempo"]()
        plt.close("all")

    def test_time_box_line_is_inside_the_axis(self):
        fig = _builders(_design_records(censor_first_without_ai=True), _static_records())["rq1_tempo"]()
        top = fig.axes[0].get_ylim()[1]
        plt.close(fig)
        assert top > TIME_BOX_SECONDS
