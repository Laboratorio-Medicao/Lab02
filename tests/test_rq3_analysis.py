"""Testes da análise de RQ3 (Issue #16).

Cobrem o que pode silenciosamente inverter uma conclusão: a direção do
pareamento, o tratamento de métricas degeneradas, o piso de p-valor do teste
exato e a imutabilidade dos dados brutos.
"""
from pathlib import Path

import pandas as pd
import pytest

from experiment.analysis import rq3
from experiment.analysis.metrics import CC_PER_LOC, CYCLOMATIC_COMPLEXITY, LOC
from experiment.analysis.rq3_data import (
    EXPECTED_TRIALS,
    compute_task_allocation_balance,
    STATIC_METRICS_CSV,
    TRIALS_CSV,
    WITH_AI,
    WITHOUT_AI,
    load_observations,
    recompute_from_source,
)
from experiment.analysis.statistics import (
    ALPHA,
    BENJAMINI_HOCHBERG,
    BONFERRONI,
    adjust_p_values,
    build_pairs,
    describe,
    paired_wilcoxon,
    rank_biserial_levels,
)

TREATMENTS = (WITHOUT_AI, WITH_AI)


@pytest.fixture(scope="module")
def loaded():
    return load_observations()


class TestLoadObservations:
    def test_loads_every_trial_of_the_design(self, loaded):
        observations, _ = loaded

        assert len(observations) == EXPECTED_TRIALS

    def test_keeps_one_row_per_trial_without_aggregating(self, loaded):
        observations, _ = loaded

        assert not observations.duplicated(
            subset=["participant", "kata_id", "treatment"]
        ).any()

    def test_every_participant_is_balanced_across_treatments(self, loaded):
        observations, _ = loaded
        counts = observations.groupby(["participant", "treatment"]).size().unstack()

        assert (counts[WITH_AI] == counts[WITHOUT_AI]).all()

    def test_reports_the_non_reproducible_mi_values_instead_of_hiding_them(self, loaded):
        _, quality = loaded
        failed = {name for name, passed, _ in quality.checks if not passed}

        assert "MI reproduzível pelo coletor no estado atual do repositório" in failed

    def test_marks_exactly_the_six_historical_mi_values_as_not_reproducible(self, loaded):
        _, quality = loaded
        historical = quality.integrity[~quality.integrity["mi_reproducible_now"]]

        assert len(historical) == 6
        assert set(historical["participant"]) == {"Guilherme"}

    def test_normalizes_complexity_by_loc_at_trial_level(self, loaded):
        observations, _ = loaded
        expected = (
            observations[CYCLOMATIC_COMPLEXITY.key] / observations[LOC.key]
        )

        pd.testing.assert_series_equal(
            observations[CC_PER_LOC.key], expected, check_names=False
        )


class TestSourceIntegrity:
    def test_loc_and_cc_reproduce_from_the_versioned_source(self, loaded):
        _, quality = loaded

        assert quality.integrity["loc_matches"].all()
        assert quality.integrity["cc_matches"].all()

    def test_recompute_rejects_a_directory_without_python_files(self, tmp_path: Path):
        with pytest.raises(ValueError):
            recompute_from_source(tmp_path)


class TestPairing:
    def test_pairs_one_row_per_participant(self, loaded):
        observations, _ = loaded

        pairs = build_pairs(
            observations, LOC.key, "participant", "treatment", TREATMENTS
        )

        assert len(pairs) == observations["participant"].nunique()

    def test_difference_is_with_ai_minus_without_ai(self, loaded):
        observations, _ = loaded

        pairs = build_pairs(
            observations, LOC.key, "participant", "treatment", TREATMENTS
        )

        assert (pairs["difference"] == pairs[WITH_AI] - pairs[WITHOUT_AI]).all()

    def test_rejects_data_missing_one_of_the_treatments(self, loaded):
        observations, _ = loaded
        single_treatment = observations[observations["treatment"] == WITH_AI]

        with pytest.raises(ValueError, match="tratamento ausente"):
            build_pairs(
                single_treatment, LOC.key, "participant", "treatment", TREATMENTS
            )


class TestPairedWilcoxon:
    def _pairs(self, differences: list[float]) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "unit": range(len(differences)),
                WITHOUT_AI: [0.0] * len(differences),
                WITH_AI: differences,
                "difference": differences,
            }
        )

    def test_flags_a_constant_metric_as_degenerate_instead_of_raising(self):
        result = paired_wilcoxon(
            self._pairs([0.0, 0.0, 0.0]), "Duplicação", "participante", TREATMENTS
        )

        assert result.degenerate
        assert result.p_value is None
        assert "zero" in result.note

    def test_three_pairs_cannot_go_below_the_exact_two_sided_floor(self):
        result = paired_wilcoxon(
            self._pairs([-5.0, -7.0, -11.0]), "LOC", "participante", TREATMENTS
        )

        assert result.n_nonzero_pairs == 3
        assert result.min_achievable_p == pytest.approx(0.25)
        assert result.p_value >= result.min_achievable_p

    def test_rank_biserial_is_minus_one_when_every_pair_decreases(self):
        result = paired_wilcoxon(
            self._pairs([-5.0, -7.0, -11.0]), "LOC", "participante", TREATMENTS
        )

        assert result.rank_biserial == pytest.approx(-1.0)

    def test_rank_biserial_is_plus_one_when_every_pair_increases(self):
        result = paired_wilcoxon(
            self._pairs([5.0, 7.0, 11.0]), "LOC", "participante", TREATMENTS
        )

        assert result.rank_biserial == pytest.approx(1.0)

    def test_hodges_lehmann_is_the_pseudomedian_of_the_differences(self):
        result = paired_wilcoxon(
            self._pairs([-5.0, -7.0, -11.0]), "LOC", "participante", TREATMENTS
        )

        # Médias de Walsh: -5, -6, -8, -7, -9, -11 → mediana -7,5.
        assert result.hodges_lehmann == pytest.approx(-7.5)


class TestDescribe:
    def test_reports_median_and_iqr(self):
        summary = describe(pd.Series([1.0, 2.0, 3.0, 4.0]))

        assert summary["median"] == pytest.approx(2.5)
        assert summary["iqr"] == pytest.approx(1.5)
        assert summary["n"] == 4


class TestPipeline:
    def test_writes_every_artifact_and_leaves_raw_data_untouched(self, tmp_path: Path):
        before = (TRIALS_CSV.read_bytes(), STATIC_METRICS_CSV.read_bytes())

        results = rq3.write_outputs(rq3.analyse(), tmp_path)

        assert (tmp_path / "rq3_summary.md").exists()
        assert (tmp_path / "data_quality_report.md").exists()
        assert (tmp_path / "descriptive_statistics.csv").exists()
        assert (tmp_path / "statistical_tests.csv").exists()
        assert (tmp_path / "normalized_metrics.csv").exists()
        assert len(results.figures) == 5
        assert all(figure.exists() for figure in results.figures)
        assert (TRIALS_CSV.read_bytes(), STATIC_METRICS_CSV.read_bytes()) == before

    def test_summary_never_claims_significance_the_tests_do_not_support(
        self, tmp_path: Path
    ):
        results = rq3.write_outputs(rq3.analyse(), tmp_path)
        summary = (tmp_path / "rq3_summary.md").read_text(encoding="utf-8")
        primary = results.tests[
            results.tests["pairing_unit"] == rq3.PARTICIPANT_PAIRING.label
        ]

        assert not (primary["p_value"] < 0.05).any()
        assert "não permitem estabelecer" in summary
        assert "A IA não altera" not in summary
        assert "os tratamentos são equivalentes" not in summary


class TestRankBiserialLevels:
    """Impede o retorno da lista fixa e errada que a auditoria encontrou."""

    def test_three_pairs_allow_more_than_plus_minus_one_and_one_third(self):
        levels = rank_biserial_levels(3)

        assert levels == pytest.approx(
            [-1.0, -2 / 3, -1 / 3, 0.0, 1 / 3, 2 / 3, 1.0]
        )

    def test_two_thirds_and_zero_are_attainable_with_three_pairs(self):
        levels = rank_biserial_levels(3)

        assert any(value == pytest.approx(2 / 3) for value in levels)
        assert any(value == pytest.approx(-2 / 3) for value in levels)
        assert any(value == pytest.approx(0.0) for value in levels)

    def test_levels_are_computed_generally_not_tabulated(self):
        for n_pairs in range(1, 10):
            levels = rank_biserial_levels(n_pairs)
            total = n_pairs * (n_pairs + 1) // 2

            assert len(levels) == total + 1
            assert levels[0] == pytest.approx(-1.0)
            assert levels[-1] == pytest.approx(1.0)
            assert levels == tuple(sorted(levels))

    def test_report_text_lists_every_level_for_three_pairs(self):
        from experiment.analysis.rq3_report import _rank_biserial_levels

        text = _rank_biserial_levels(3)

        assert "0,667" in text
        assert "0,000" in text
        assert "±1,00, ±0,33" not in text


class TestMultiplicityCorrection:
    def test_bonferroni_never_reports_a_smaller_p_than_the_raw_one(self):
        raw = pd.Series([0.03125, 0.0625, 0.3125, 0.375, 0.84375])

        adjusted = adjust_p_values(raw, BONFERRONI)

        assert (adjusted >= raw).all()

    def test_benjamini_hochberg_never_reports_a_smaller_p_than_the_raw_one(self):
        raw = pd.Series([0.03125, 0.0625, 0.3125, 0.375, 0.84375])

        adjusted = adjust_p_values(raw, BENJAMINI_HOCHBERG)

        assert (adjusted >= raw).all()

    def test_degenerate_tests_stay_missing_and_do_not_enlarge_the_family(self):
        raw = pd.Series([0.01, 0.02, float("nan")])

        adjusted = adjust_p_values(raw, BONFERRONI)

        assert pd.isna(adjusted.iloc[2])
        assert adjusted.iloc[0] == pytest.approx(0.02)  # família de 2, não de 3

    def test_adjusted_p_is_capped_at_one(self):
        adjusted = adjust_p_values(pd.Series([0.5, 0.6]), BONFERRONI)

        assert (adjusted <= 1.0).all()

    def test_rejects_an_unknown_method(self):
        with pytest.raises(ValueError, match="desconhecido"):
            adjust_p_values(pd.Series([0.01]), "holm")


class TestMultiplicityInPipeline:
    def test_every_test_with_a_p_value_also_carries_adjusted_p_values(self, loaded):
        tests = rq3.analyse().tests
        with_p = tests[tests["p_value"].notna()]

        assert not with_p.empty
        assert with_p["p_bonferroni"].notna().all()
        assert with_p["p_fdr_bh"].notna().all()
        assert (with_p["p_bonferroni"] >= with_p["p_value"]).all()
        assert (with_p["p_fdr_bh"] >= with_p["p_value"]).all()

    def test_raw_p_values_are_preserved_alongside_the_adjusted_ones(self):
        tests = rq3.analyse().tests

        assert "p_value" in tests.columns
        assert tests.loc[
            tests["metric"] == "MI (harmonizado)", "p_value"
        ].min() == pytest.approx(0.03125)

    def test_the_secondary_result_is_not_significant_after_correction(self):
        tests = rq3.analyse().tests
        secondary = tests[
            (tests["metric"] == "MI (harmonizado)")
            & (tests["pairing_unit"] == rq3.KATA_PAIRING.label)
        ].iloc[0]

        assert secondary["p_value"] == pytest.approx(0.03125)
        assert secondary["p_bonferroni"] >= ALPHA
        assert secondary["p_fdr_bh"] >= ALPHA
        assert "não rejeita" in secondary["decision_bonferroni"]

    def test_no_test_survives_multiplicity_correction(self):
        tests = rq3.analyse().tests

        assert not (tests["p_bonferroni"] < ALPHA).any()


class TestTaskAllocationBalance:
    def test_reports_one_row_per_participant_with_both_sides(self, loaded):
        observations, _ = loaded

        balance = compute_task_allocation_balance(observations)

        assert len(balance) == observations["participant"].nunique()
        assert (balance[f"katas_{WITH_AI}"].str.split().str.len() == 3).all()
        assert (balance[f"katas_{WITHOUT_AI}"].str.split().str.len() == 3).all()

    def test_detects_that_the_allocation_is_not_balanced(self, loaded):
        observations, _ = loaded

        balance = compute_task_allocation_balance(observations)
        difference = balance["cyclomatic_complexity_avg_difference"]

        # A auditoria encontrou katas menos complexos no lado com IA em 2 de 3
        # pares; o teste falha se o desequilíbrio deixar de ser reportado.
        assert (difference < 0).sum() == 2
        assert difference.abs().max() > 1.0

    def test_summary_declares_the_confounding(self, tmp_path: Path):
        rq3.write_outputs(rq3.analyse(), tmp_path)
        summary = (tmp_path / "rq3_summary.md").read_text(encoding="utf-8")

        assert "Confundimento entre tratamento e dificuldade dos katas" in summary
        assert "possível confundimento" in summary
        assert "não permite separar completamente" in summary
        assert "mesma direção observada" in summary

    def test_summary_declares_multiplicity_and_the_uncorrected_secondary_result(
        self, tmp_path: Path
    ):
        rq3.write_outputs(rq3.analyse(), tmp_path)
        summary = (tmp_path / "rq3_summary.md").read_text(encoding="utf-8")

        assert "Multiplicidade" in summary
        assert "Bonferroni" in summary
        assert "não permanece significativo após correção de multiplicidade" in summary

    def test_summary_does_not_claim_the_treatments_are_equivalent(
        self, tmp_path: Path
    ):
        rq3.write_outputs(rq3.analyse(), tmp_path)
        summary = (tmp_path / "rq3_summary.md").read_text(encoding="utf-8")

        assert "não permitem estabelecer" in summary
        assert "não pôde ser avaliada adequadamente" in summary
        assert "não significa que os tratamentos sejam" in summary


class TestFigureSuite:
    """A suíte é curta de propósito: uma figura por pergunta analítica."""

    def test_produces_one_figure_per_analytical_question(self, tmp_path: Path):
        results = rq3.write_outputs(rq3.analyse(), tmp_path)

        assert [figure.name for figure in results.figures] == [
            "fig1_distribuicao_por_tratamento.png",
            "fig2_comparacao_pareada.png",
            "fig3_resultados_por_kata.png",
            "fig4_cc_vs_loc.png",
            "fig5_complexidade_normalizada.png",
        ]

    def test_does_not_draw_a_chart_for_the_unmeasured_duplication(
        self, tmp_path: Path
    ):
        results = rq3.write_outputs(rq3.analyse(), tmp_path)
        names = " ".join(figure.name for figure in results.figures)

        assert "duplic" not in names

    def test_summary_explains_the_forms_left_out(self, tmp_path: Path):
        rq3.write_outputs(rq3.analyse(), tmp_path)
        summary = (tmp_path / "rq3_summary.md").read_text(encoding="utf-8")

        assert "Histograma" in summary
        assert "Violino" in summary
        assert "grande volume de dados" in summary

    def test_every_figure_is_written_at_report_resolution(self, tmp_path: Path):
        results = rq3.write_outputs(rq3.analyse(), tmp_path)

        for figure in results.figures:
            assert figure.stat().st_size > 100_000, figure.name
