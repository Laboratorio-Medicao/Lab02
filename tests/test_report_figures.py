"""Figuras do relatório: uma por pergunta, sem p-valores e com os números das análises."""

import matplotlib.pyplot as plt
import pytest

from experiment.analysis.rq1_rq2 import analyze_rq1, load_trials
from experiment.analysis.rq3 import analyse
from experiment.visualization.report_figures import FIGURE_NAMES, build_all, save_all


@pytest.fixture(scope="module")
def figures():
    built = build_all(analyze_rq1(load_trials()), analyse())
    yield built
    plt.close("all")


def _texts(fig):
    return [t.get_text() for ax in fig.axes for t in ax.texts] + [t.get_text() for t in fig.texts]


def test_builds_one_figure_per_name(figures):
    assert list(figures) == list(FIGURE_NAMES)


def test_no_p_value_is_drawn(figures):
    for fig in figures.values():
        assert not any("p =" in text or "p <" in text for text in _texts(fig))


def test_rq1_medians_match_the_analysis(figures):
    texts = _texts(figures["rq1_tempo_por_tratamento"])
    assert "37,6" in texts and "721,6" in texts


def test_rq2_figure_does_not_claim_absence_of_defects(figures):
    footer = " ".join(_texts(figures["rq2_desfecho_trials"]))
    assert "não indica ausência de defeitos" in footer
    assert "0 no time-box\n(censurados)" in _texts(figures["rq2_desfecho_trials"])


def test_rq3_normalized_panels_show_both_denominators(figures):
    texts = _texts(figures["rq3_cc_normalizada"])
    assert {"0,282", "0,444", "0,429", "0,500"} <= set(texts)


def test_save_is_deterministic(figures, tmp_path):
    first = save_all(build_all(analyze_rq1(load_trials()), analyse()), tmp_path / "a")
    second = save_all(build_all(analyze_rq1(load_trials()), analyse()), tmp_path / "b")
    for a, b in zip(first, second):
        assert a.read_bytes() == b.read_bytes(), a.name
