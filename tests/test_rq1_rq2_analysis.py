import csv

import pytest

from experiment.analysis.rq1_rq2 import (
    TIME_BOX_SECONDS,
    TrialsDataError,
    analyze_rq1,
    analyze_rq2,
    elapsed_seconds,
    load_trials,
    paired_wilcoxon,
    summarize,
    tukey_outliers,
    validate_trials,
)
from experiment.analysis.rq1_rq2_report import _h0_conclusion, generate_markdown
from experiment.collection.timer import CSV_FIELDNAMES, AcceptanceTestResult, TrialRecord
from experiment.config.lab02_design import KATAS, TREATMENTS_BY_PARTICIPANT
from experiment.domain.enums import Treatment

WITH_AI = Treatment.WITH_AI
WITHOUT_AI = Treatment.WITHOUT_AI

# Tempos sintéticos por participante, na ordem dos katas: com IA sempre
# bem mais rápido, para que a separação completa e o sinal das diferenças
# sejam previsíveis.
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


def _design_records(offsets=None):
    """18 trials válidos, seguindo TREATMENTS_BY_PARTICIPANT."""
    offsets = offsets or {}
    records = []
    for participant, treatments in TREATMENTS_BY_PARTICIPANT.items():
        with_ai_iter = iter(_WITH_AI_TIMES)
        without_ai_iter = iter(_WITHOUT_AI_TIMES)
        for kata, treatment in zip(KATAS, treatments):
            base = next(with_ai_iter) if treatment == WITH_AI else next(without_ai_iter)
            elapsed = base + offsets.get(participant, 0.0)
            records.append(_record(participant, kata.id, treatment, elapsed))
    return records


def _write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())


def _row(**overrides):
    row = {
        "participant": "Arthur",
        "kata_id": "kata-01",
        "treatment": "with_ai",
        "elapsed_seconds": "54.656",
        "censored": "False",
        "tests_total": "6",
        "tests_passing": "5",
        "tests_failing": "1",
        "success_rate_percent": "83.3",
    }
    row.update(overrides)
    return row


class TestTrialRecordFromRow:
    def test_round_trip_with_test_result(self):
        record = _record("Arthur", "kata-01", WITH_AI, 54.656, passing=5, total=6)
        assert TrialRecord.from_row(record.to_row()) == record

    def test_round_trip_without_test_result(self):
        record = TrialRecord("Arthur", "kata-01", WITH_AI, 54.656, False, test_result=None)
        assert TrialRecord.from_row(record.to_row()) == record

    def test_false_string_is_parsed_as_false(self):
        assert TrialRecord.from_row(_row(censored="False")).censored is False

    def test_invalid_censored_value_raises(self):
        with pytest.raises(ValueError, match="censored"):
            TrialRecord.from_row(_row(censored="false"))

    def test_accepts_success_rate_with_one_decimal(self):
        record = TrialRecord.from_row(_row(success_rate_percent="83.3"))
        assert record.test_result == AcceptanceTestResult(passing=5, total=6)

    def test_inconsistent_tests_failing_raises(self):
        with pytest.raises(ValueError, match="tests_failing"):
            TrialRecord.from_row(_row(tests_failing="0"))

    def test_inconsistent_success_rate_raises(self):
        with pytest.raises(ValueError, match="success_rate_percent"):
            TrialRecord.from_row(_row(success_rate_percent="100.0"))

    def test_passing_above_total_raises(self):
        with pytest.raises(ValueError, match="fora de 0..tests_total"):
            TrialRecord.from_row(
                _row(tests_total="5", tests_passing="7", tests_failing="-2", success_rate_percent="140.0")
            )

    def test_partially_blank_test_columns_raise(self):
        with pytest.raises(ValueError, match="parcialmente"):
            TrialRecord.from_row(_row(tests_failing=""))


class TestLoadAndValidate:
    def test_loads_valid_csv(self, tmp_path):
        path = tmp_path / "trials.csv"
        _write_csv(path, _design_records())
        assert len(load_trials(path)) == 18

    def test_short_row_raises_data_error(self, tmp_path):
        path = tmp_path / "trials.csv"
        path.write_text(
            ",".join(CSV_FIELDNAMES) + "\nArthur,kata-01,with_ai,10.0,False,5\n", encoding="utf-8"
        )
        with pytest.raises(TrialsDataError, match="linha 2"):
            load_trials(path)

    def test_extra_columns_raise(self, tmp_path):
        path = tmp_path / "trials.csv"
        row = _design_records()[0].to_row()
        path.write_text(
            ",".join(CSV_FIELDNAMES) + "\n" + ",".join(row.values()) + ",extra\n", encoding="utf-8"
        )
        with pytest.raises(TrialsDataError, match="colunas a mais"):
            load_trials(path)

    def test_non_censored_trial_with_failing_tests_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(
            first.participant, first.kata_id, first.treatment, first.elapsed_seconds, passing=4
        )
        with pytest.raises(TrialsDataError, match="não censurado"):
            validate_trials(records)

    def test_nan_elapsed_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(first.participant, first.kata_id, first.treatment, float("nan"))
        with pytest.raises(TrialsDataError, match="inválido"):
            validate_trials(records)

    def test_wrong_header_raises(self, tmp_path):
        path = tmp_path / "trials.csv"
        path.write_text("participant,kata_id\nArthur,kata-01\n", encoding="utf-8")
        with pytest.raises(TrialsDataError, match="Cabeçalho"):
            load_trials(path)

    def test_missing_test_result_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = TrialRecord(
            first.participant, first.kata_id, first.treatment, first.elapsed_seconds, False
        )
        with pytest.raises(TrialsDataError, match="resultado dos testes"):
            validate_trials(records)

    def test_duplicate_trial_is_rejected(self):
        records = _design_records()
        records[1] = records[0]
        with pytest.raises(TrialsDataError, match="duplicados"):
            validate_trials(records)

    def test_wrong_trial_count_is_rejected(self):
        with pytest.raises(TrialsDataError, match="Esperados 18"):
            validate_trials(_design_records()[:-1])

    def test_treatment_diverging_from_design_is_rejected(self):
        records = _design_records()
        first = records[0]
        other = WITHOUT_AI if first.treatment == WITH_AI else WITH_AI
        records[0] = _record(first.participant, first.kata_id, other, first.elapsed_seconds)
        with pytest.raises(TrialsDataError, match="difere do desenho"):
            validate_trials(records)

    def test_censored_trial_below_time_box_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(first.participant, first.kata_id, first.treatment, 100.0, censored=True)
        with pytest.raises(TrialsDataError, match="travado no time-box"):
            validate_trials(records)

    def test_trial_at_time_box_not_marked_censored_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(first.participant, first.kata_id, first.treatment, TIME_BOX_SECONDS)
        with pytest.raises(TrialsDataError, match="não está marcado como censurado"):
            validate_trials(records)

    def test_censored_trial_at_time_box_is_accepted(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(
            first.participant, first.kata_id, first.treatment, TIME_BOX_SECONDS, censored=True,
            passing=3,
        )
        validate_trials(records)

    def test_tests_total_diverging_for_same_kata_is_rejected(self):
        records = _design_records()
        first = records[0]
        records[0] = _record(
            first.participant, first.kata_id, first.treatment, first.elapsed_seconds,
            passing=6, total=6,
        )
        with pytest.raises(TrialsDataError, match="tests_total"):
            validate_trials(records)


class TestSummarize:
    def test_quartiles_use_inclusive_method(self):
        summary = summarize([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
        assert (summary.q1, summary.median, summary.q3) == (3.0, 5.0, 7.0)
        assert summary.iqr == 4.0

    def test_quartiles_interpolate_like_numpy(self):
        summary = summarize([1.0, 2.0, 3.0, 4.0])
        assert (summary.q1, summary.q3) == (1.75, 3.25)

    def test_single_value(self):
        summary = summarize([7.0])
        assert (summary.q1, summary.median, summary.q3, summary.iqr) == (7.0, 7.0, 7.0, 0.0)


class TestTukeyOutliers:
    def test_flags_values_outside_fences(self):
        records = _design_records()
        first_with_ai = next(r for r in records if r.treatment == WITH_AI)
        records[records.index(first_with_ai)] = _record(
            first_with_ai.participant, first_with_ai.kata_id, WITH_AI, 500.0
        )

        result = tukey_outliers(records, elapsed_seconds)

        assert [r.elapsed_seconds for r in result[WITH_AI].outliers] == [500.0]
        assert result[WITHOUT_AI].outliers == ()


class TestPairedWilcoxon:
    def test_three_negative_pairs_give_one_sided_p_of_one_eighth(self):
        result = paired_wilcoxon([10, 20, 30], [110, 230, 330], alternative="less")
        assert result.method == "exato"
        assert result.p_one_sided == pytest.approx(0.125)
        assert not result.reject_h0
        assert not result.has_power

    def test_two_sided_p_is_twice_the_smaller_one_sided_p(self):
        with_ai, without_ai = [10, 20, 30], [110, 230, 330]
        less = paired_wilcoxon(with_ai, without_ai, alternative="less")
        greater = paired_wilcoxon(with_ai, without_ai, alternative="greater")
        assert less.p_two_sided == pytest.approx(
            min(1.0, 2 * min(less.p_one_sided, greater.p_one_sided))
        )
        assert less.p_two_sided == pytest.approx(0.25)

    def test_argument_order_matters(self):
        in_order = paired_wilcoxon([10, 20, 30], [110, 230, 330], alternative="less")
        swapped = paired_wilcoxon([110, 230, 330], [10, 20, 30], alternative="less")
        assert in_order.p_one_sided == pytest.approx(0.125)
        assert swapped.p_one_sided == pytest.approx(1.0)

    def test_six_negative_pairs_can_reject_h0(self):
        result = paired_wilcoxon([1, 2, 3, 4, 5, 6], [11, 22, 33, 44, 55, 66], alternative="less")
        assert result.p_one_sided == pytest.approx(1 / 64)
        assert result.reject_h0

    def test_all_zero_differences_are_not_applicable(self):
        result = paired_wilcoxon([100.0] * 3, [100.0] * 3, alternative="less")
        assert not result.applicable
        assert result.p_one_sided is None
        assert not result.reject_h0

    def test_min_attainable_p_ignores_zero_differences(self):
        result = paired_wilcoxon([5, 5, 1], [5, 5, 3], alternative="less")
        assert result.n_nonzero == 1
        assert result.method.startswith("permutação")
        assert result.min_attainable_p == pytest.approx(0.5)
        assert result.p_one_sided == pytest.approx(0.5)

    def test_tied_absolute_differences_use_exact_permutation(self):
        result = paired_wilcoxon([1, 2, 3], [2, 3, 5], alternative="less")
        assert result.method.startswith("permutação")
        assert result.p_one_sided == pytest.approx(0.125)


class TestAnalyses:
    def test_rq1_on_design_records(self):
        records = _design_records(offsets={"Marcos": 5.0})

        rq1 = analyze_rq1(records)

        assert rq1.by_treatment[WITH_AI].median == 40.0
        assert rq1.by_treatment[WITHOUT_AI].median == 700.0
        assert rq1.censored_by_treatment == {WITH_AI: 0, WITHOUT_AI: 0}
        assert rq1.fully_separated
        assert rq1.test.p_one_sided == pytest.approx(0.125)
        assert all(c.difference < 0 for c in rq1.by_participant)

    def test_leave_one_out_excludes_participant(self):
        records = _design_records(offsets={"Marcos": 1000.0})

        rq1 = analyze_rq1(records, leave_out="Marcos")

        assert rq1.leave_out_by_treatment[WITH_AI].n == 6
        assert rq1.leave_out_by_treatment[WITH_AI].median == 40.0
        assert rq1.leave_out_fully_separated
        assert not rq1.fully_separated

    def test_by_kata_has_both_treatments_for_every_kata(self):
        rq1 = analyze_rq1(_design_records())
        assert len(rq1.by_kata) == len(KATAS)
        assert all(k.with_ai and k.without_ai for k in rq1.by_kata)

    def test_rq2_with_all_tests_passing_is_not_applicable(self):
        rq2 = analyze_rq2(_design_records())

        assert rq2.success_rate_by_treatment[WITH_AI].median == 100.0
        assert rq2.failing_by_treatment[WITHOUT_AI].maximum == 0
        assert not rq2.success_rate_test.applicable
        assert not rq2.failing_test.applicable

    def test_rq2_pairs_use_mean_so_a_single_failing_trial_counts(self):
        records = _design_records()
        first = next(r for r in records if r.treatment == WITHOUT_AI)
        records[records.index(first)] = _record(
            first.participant, first.kata_id, WITHOUT_AI, TIME_BOX_SECONDS, censored=True,
            passing=2,
        )

        rq2 = analyze_rq2(records)

        # Com a mediana, 1 trial com falhas entre 3 não mudaria o par (seria 0).
        assert rq2.failing_test.applicable
        assert rq2.failing_test.n_nonzero == 1
        assert rq2.failing_test.differences == pytest.approx((-1.0, 0.0, 0.0))
        assert rq2.failing_test.alternative == "less"
        assert rq2.failing_test.p_one_sided == pytest.approx(0.5)
        assert rq2.success_rate_test.alternative == "greater"
        assert rq2.success_rate_test.p_one_sided == pytest.approx(0.5)

    def test_report_ceiling_note_reflects_censored_trials(self):
        records = _design_records()
        first = next(r for r in records if r.treatment == WITHOUT_AI)
        records[records.index(first)] = _record(
            first.participant, first.kata_id, WITHOUT_AI, TIME_BOX_SECONDS, censored=True,
            passing=3,
        )

        markdown = generate_markdown(analyze_rq1(records), analyze_rq2(records))

        assert "nenhum trial foi censurado" not in markdown
        assert "Houve 1 trial(s) censurado(s) e 1 trial(s) com testes falhando" in markdown

    def test_report_flags_censoring_with_ai_as_favoring_h1(self):
        records = _design_records()
        first = next(r for r in records if r.treatment == WITH_AI)
        records[records.index(first)] = _record(
            first.participant, first.kata_id, WITH_AI, TIME_BOX_SECONDS, censored=True, passing=3
        )

        markdown = generate_markdown(analyze_rq1(records), analyze_rq2(records))

        assert "conservador quanto a H1" not in markdown
        assert "favorece H1" in markdown

    def test_h0_conclusion_when_rejected(self):
        result = paired_wilcoxon([1, 2, 3, 4, 5, 6], [11, 22, 33, 44, 55, 66], alternative="less")

        conclusion = _h0_conclusion(result)

        assert conclusion.startswith("**H0 rejeitada**")
        assert "não tem poder" not in conclusion

    def test_h0_conclusion_with_power_but_not_rejected(self):
        # 6 pares com sinais mistos: tem poder (1/64 < α), mas p ≥ α.
        result = paired_wilcoxon([1, 22, 3, 44, 5, 66], [11, 2, 33, 4, 55, 6], alternative="less")

        conclusion = _h0_conclusion(result)

        assert result.has_power and not result.reject_h0
        assert conclusion.startswith("**H0 não rejeitada**")
        assert "não tem poder" not in conclusion

    def test_report_states_h0_conclusions(self):
        records = _design_records()
        markdown = generate_markdown(analyze_rq1(records), analyze_rq2(records))

        assert "p unilateral (H1: com IA < sem IA) = 0,125" in markdown
        assert "o teste não tem poder para rejeitar H0" in markdown
        assert "não aplicável" in markdown
