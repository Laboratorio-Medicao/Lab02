"""Bônus da S03 (Issue #18): MI em profundidade e nº de prompts × qualidade."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from experiment.analysis.metrics import Metric
from experiment.analysis.mi_prompts import analyse, spearman_table
from experiment.analysis.mi_prompts_report import generate_markdown
from experiment.analysis.rq3 import HARMONIZED_MI_KEY
from experiment.visualization.report_figures import BONUS_FIGURE_NAMES, build_bonus


@pytest.fixture(scope="module")
def results():
    return analyse()


def test_mi_rebuilt_from_components_matches_harmonized_series(results):
    diff = (results.components["mi_from_components"] - results.components[HARMONIZED_MI_KEY]).abs()
    assert len(results.components) == 18
    assert (diff <= 0.01).all()


def test_every_with_ai_trial_has_a_prompt_count(results):
    assert len(results.prompts_quality) == 9
    assert results.prompts_quality["n_prompts"].notna().all()


def test_confounding_with_participant_is_flagged(results):
    name, passed, _ = results.checks[2]
    assert name.startswith("Nº de prompts varia")
    assert passed is False


def test_constant_metric_has_no_correlation():
    data = pd.DataFrame({"y": [1.0, 2.0, 3.0], "x": [0.0, 0.0, 0.0]})
    table = spearman_table(data, Metric("y", "Y", "", False, ""), (Metric("x", "X", "", False, ""),))
    assert table.loc[0, "spearman_rho"] is None
    assert "constante" in table.loc[0, "note"]


def test_report_is_descriptive_and_does_not_conclude_about_prompts(results):
    text = generate_markdown(results)
    assert "p =" not in text and "p <" not in text
    assert "não permitem avaliar" in text
    assert "constante dentro de cada participante" in text


def test_bonus_figures_build(results):
    figures = build_bonus(results.components, results.prompts_quality)
    assert list(figures) == list(BONUS_FIGURE_NAMES)
    plt.close("all")
