"""Figuras de RQ3 — uma ideia por figura, para leitura em segundos.

O formato segue as figuras do material da disciplina: título que já diz o
achado, gráfico limpo e uma nota de rodapé explicando como ler. Três decisões
orientam o módulo:

* uma ideia por figura — se são duas ideias, são duas figuras;
* rótulo direto em vez de legenda a decifrar: nomes e valores ficam escritos
  ao lado dos pontos, para ninguém precisar estimar pelo eixo;
* sem jargão — cada eixo diz se número maior ou menor é melhor.

Boxplot foi evitado: com 9 observações por grupo, os pontos individuais mais
uma marca de mediana mostram o mesmo sem exigir caixa, bigode e IQR.

Este módulo não calcula estatística — apenas lê o que a análise produziu.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend precisa ser fixado antes)
from matplotlib.lines import Line2D  # noqa: E402

from experiment.analysis.metrics import CYCLOMATIC_COMPLEXITY, LOC  # noqa: E402
from experiment.analysis.rq3_data import TREATMENTS, WITH_AI, WITHOUT_AI  # noqa: E402

TREATMENT_COLORS = {WITHOUT_AI: "#2a78d6", WITH_AI: "#eb6834"}
TREATMENT_LABELS = {WITHOUT_AI: "Sem IA", WITH_AI: "Com IA"}

SURFACE = "#ffffff"
TEXT_PRIMARY = "#111111"
TEXT_SECONDARY = "#555555"
GRID_COLOR = "#e4e4e0"
CONNECTOR_COLOR = "#9a9a94"

FIGURE_DPI = 200

#: O rótulo do eixo traz a direção: sem isso o leitor não sabe se um número
#: maior é bom ou ruim.
AXIS_LABELS = {
    "loc": "Linhas de código\n(menos linhas = código mais enxuto)",
    "cyclomatic_complexity_avg": "Complexidade do código\n(número menor = mais simples)",
    "maintainability_index_harmonized": "Facilidade de manutenção, de 0 a 100\n"
                                        "(número maior = mais fácil de manter)",
    "cc_per_loc": "Complexidade para cada linha escrita\n(número menor = mais simples)",
}
SHORT_NAMES = {
    "loc": "Linhas de código",
    "cyclomatic_complexity_avg": "Complexidade",
    "maintainability_index_harmonized": "Facilidade de manutenção",
    "cc_per_loc": "Complexidade por linha",
}
DECIMALS = {
    "loc": 0,
    "cyclomatic_complexity_avg": 0,
    "maintainability_index_harmonized": 1,
    "cc_per_loc": 2,
}

HARMONIZED_MI = "maintainability_index_harmonized"

#: Aviso presente em todas as figuras.
SAMPLE_CAVEAT = "Apenas 3 participantes: resultado indicativo, não conclusivo."

#: Espalhamento horizontal fixo dentro de uma coluna, para que dois trials com
#: o mesmo valor não se escondam. Determinístico, sem sorteio.
COLUMN_SPREAD = 0.17
POINT_SIZE = 130
MEDIAN_BAR_HALF_WIDTH = 0.30


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": GRID_COLOR,
            "axes.labelcolor": TEXT_PRIMARY,
            "axes.labelsize": 13,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.titlepad": 14,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID_COLOR,
            "grid.linewidth": 0.8,
            "text.color": TEXT_PRIMARY,
            "xtick.color": TEXT_PRIMARY,
            "ytick.color": TEXT_SECONDARY,
            "xtick.labelsize": 13,
            "ytick.labelsize": 12,
            "legend.frameon": False,
            "legend.fontsize": 13,
            "font.size": 13,
            "figure.dpi": FIGURE_DPI,
            "savefig.dpi": FIGURE_DPI,
        }
    )


def _format(value: float, metric_key: str) -> str:
    """Número com vírgula decimal.

    A mediana de dois valores pode cair no meio (13,5); arredondar para 14
    faria o rótulo discordar do ponto desenhado.
    """
    decimals = DECIMALS.get(metric_key, 1)
    if abs(value - round(value, decimals)) > 1e-9:
        decimals += 1
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def _horizontal_only_grid(axes: plt.Axes) -> None:
    axes.grid(axis="x", visible=False)
    axes.grid(axis="y", visible=True)


def _treatment_legend() -> list[Line2D]:
    return [
        Line2D(
            [], [], marker="o", linestyle="none", markersize=12,
            markerfacecolor=TREATMENT_COLORS[treatment], markeredgecolor=SURFACE,
            label=TREATMENT_LABELS[treatment],
        )
        for treatment in TREATMENTS
    ]


def _save(figure: plt.Figure, output_dir: Path, name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / name
    figure.savefig(path, facecolor=SURFACE)
    plt.close(figure)
    return path


def _figure_with_footer(nrows: int, ncols: int, figsize: tuple[float, float]):
    """Figura com uma faixa inferior própria para legenda e rodapé.

    Reservar uma linha da grade evita que as duas disputem a margem.
    """
    figure = plt.figure(figsize=figsize, layout="constrained")
    grid = figure.add_gridspec(2, 1, height_ratios=[1 - FOOTER_HEIGHT, FOOTER_HEIGHT])
    panels = np.atleast_1d(grid[0].subgridspec(nrows, ncols).subplots())
    footer = figure.add_subplot(grid[1])
    footer.axis("off")
    return figure, panels, footer


FOOTER_HEIGHT = 0.21


def _fill_footer(footer: plt.Axes, how_to_read: str) -> None:
    """Legenda, instrução de leitura e aviso, em posições verticais fixas."""
    footer.legend(
        handles=_treatment_legend(), loc="upper center", ncol=2,
        fontsize=13, borderaxespad=0, bbox_to_anchor=(0.5, 1.15),
    )
    footer.text(
        0.5, 0.52, how_to_read, transform=footer.transAxes,
        ha="center", va="top", fontsize=12, color=TEXT_SECONDARY, linespacing=1.5,
    )
    footer.text(
        0.5, 0.0, SAMPLE_CAVEAT, transform=footer.transAxes,
        ha="center", va="bottom", fontsize=11.5, color=TEXT_SECONDARY, style="italic",
    )


def _dot_column_panel(
    axes: plt.Axes, observations: pd.DataFrame, metric_key: str
) -> None:
    """Uma coluna de pontos por tratamento, com a mediana marcada e escrita."""
    for base, treatment in enumerate(TREATMENTS):
        values = observations.loc[observations["treatment"] == treatment, metric_key]
        spread = np.linspace(-COLUMN_SPREAD, COLUMN_SPREAD, len(values))
        axes.scatter(
            base + spread, sorted(values), s=POINT_SIZE,
            color=TREATMENT_COLORS[treatment], edgecolor=SURFACE, linewidth=1.6,
            alpha=0.9, zorder=3,
        )
        median = values.median()
        axes.hlines(
            median, base - MEDIAN_BAR_HALF_WIDTH, base + MEDIAN_BAR_HALF_WIDTH,
            color=TEXT_PRIMARY, linewidth=3.2, zorder=4,
        )
        axes.annotate(
            _format(median, metric_key),
            xy=(base + MEDIAN_BAR_HALF_WIDTH, median), xytext=(10, 0),
            textcoords="offset points", va="center", ha="left",
            fontsize=15, fontweight="bold", color=TEXT_PRIMARY, zorder=5,
        )

    axes.set_xticks([0, 1])
    axes.set_xticklabels([TREATMENT_LABELS[treatment] for treatment in TREATMENTS])
    for label, treatment in zip(axes.get_xticklabels(), TREATMENTS):
        label.set_color(TREATMENT_COLORS[treatment])
        label.set_fontweight("bold")
    axes.set_xlim(-0.65, 1.75)
    axes.set_ylabel(AXIS_LABELS[metric_key])
    _horizontal_only_grid(axes)


def plot_where_the_trials_landed(
    observations: pd.DataFrame, output_dir: Path, name: str
) -> Path:
    """Figura 1 — cada um dos 18 trials, lado a lado por tratamento."""
    metrics = (LOC.key, CYCLOMATIC_COMPLEXITY.key, HARMONIZED_MI)
    figure, panels, footer = _figure_with_footer(1, 3, (16.5, 8.0))

    for axes, metric_key in zip(panels, metrics):
        _dot_column_panel(axes, observations, metric_key)
        axes.set_title(SHORT_NAMES[metric_key])

    figure.suptitle(
        "Com IA, os trials tiveram menos linhas, menos complexidade\n"
        "e maior facilidade de manutenção",
        fontsize=19, fontweight="bold",
    )
    _fill_footer(
        footer,
        f"Cada bolinha é um dos {len(observations)} trials. A barra preta e o "
        "número em negrito marcam o valor do meio (mediana) de cada grupo.\n"
        "\"Facilidade de manutenção\" foi recalculada do zero para os 18 trials, "
        "com a mesma regra para todo mundo.",
    )
    return _save(figure, output_dir, name)


LABEL_MIN_SEPARATION = 0.09


def _spread(points: list[tuple[str, float]], axes: plt.Axes) -> list[tuple[str, float]]:
    bottom, top = axes.get_ylim()
    gap = LABEL_MIN_SEPARATION * (top - bottom)
    placed: list[tuple[str, float]] = []
    for label, value in sorted(points, key=lambda point: point[1]):
        if placed and value - placed[-1][1] < gap:
            value = placed[-1][1] + gap
        placed.append((label, value))
    return placed


def _slope_panel(
    axes: plt.Axes, observations: pd.DataFrame, metric_key: str
) -> str:
    participants = sorted(observations["participant"].unique())
    medians = {
        participant: {
            treatment: observations.loc[
                (observations["participant"] == participant)
                & (observations["treatment"] == treatment),
                metric_key,
            ].median()
            for treatment in TREATMENTS
        }
        for participant in participants
    }

    for participant in participants:
        pair = medians[participant]
        axes.plot(
            [0, 1], [pair[WITHOUT_AI], pair[WITH_AI]],
            color=CONNECTOR_COLOR, linewidth=2.4, zorder=2,
        )
        for base, treatment in enumerate(TREATMENTS):
            axes.scatter(
                base, pair[treatment], s=230, color=TREATMENT_COLORS[treatment],
                edgecolor=SURFACE, linewidth=2.2, zorder=3,
            )

    axes.set_xlim(-1.05, 1.95)
    axes.set_xticks([0, 1])
    axes.set_xticklabels([TREATMENT_LABELS[treatment] for treatment in TREATMENTS])
    for label, treatment in zip(axes.get_xticklabels(), TREATMENTS):
        label.set_color(TREATMENT_COLORS[treatment])
        label.set_fontweight("bold")
    axes.set_ylabel(AXIS_LABELS[metric_key])
    axes.margins(y=0.20)
    _horizontal_only_grid(axes)

    _annotate_slope_ends(axes, medians, participants, metric_key)

    lower = sum(medians[p][WITH_AI] < medians[p][WITHOUT_AI] for p in participants)
    higher = len(participants) - lower
    direction = "menores" if lower > higher else "maiores"
    return f"Nos {len(participants)} participantes, os valores com IA foram {direction}."


LABEL_COLUMN_LEFT = -0.22
LABEL_COLUMN_RIGHT = 1.22


def _annotate_slope_ends(
    axes: plt.Axes, medians: dict, participants: list[str], metric_key: str
) -> None:
    """Nome e valor nas pontas, afastados quando coincidem."""
    for treatment, column, align in (
        (WITHOUT_AI, LABEL_COLUMN_LEFT, "right"),
        (WITH_AI, LABEL_COLUMN_RIGHT, "left"),
    ):
        points = [(participant, medians[participant][treatment]) for participant in participants]
        for participant, label_y in _spread(points, axes):
            value = medians[participant][treatment]
            text = (
                f"{participant}  {_format(value, metric_key)}"
                if treatment == WITHOUT_AI
                else _format(value, metric_key)
            )
            axes.annotate(
                text, xy=(0 if treatment == WITHOUT_AI else 1, value),
                xytext=(column, label_y), textcoords="data",
                ha=align, va="center", fontsize=13,
                fontweight="normal" if treatment == WITHOUT_AI else "bold",
                color=TEXT_PRIMARY if treatment == WITHOUT_AI
                else TREATMENT_COLORS[WITH_AI],
                arrowprops={"arrowstyle": "-", "color": GRID_COLOR, "linewidth": 1.2,
                            "shrinkA": 2, "shrinkB": 14},
            )


def plot_paired_by_participant(
    observations: pd.DataFrame, output_dir: Path, name: str
) -> Path:
    """Figura 2 — a comparação que o teste principal realmente faz."""
    metrics = (LOC.key, CYCLOMATIC_COMPLEXITY.key, HARMONIZED_MI)
    figure, panels, footer = _figure_with_footer(1, 3, (17.0, 8.5))

    for axes, metric_key in zip(panels, metrics):
        summary = _slope_panel(axes, observations, metric_key)
        axes.set_title(SHORT_NAMES[metric_key])
        axes.set_xlabel(summary, fontsize=13, labelpad=14)

    figure.suptitle(
        "Cada linha é um participante: como o valor mudou de sem IA para com IA",
        fontsize=19, fontweight="bold",
    )
    _fill_footer(
        footer,
        "São 3 linhas porque são 3 participantes. Cada ponta é o valor do meio "
        "(mediana) dos 3 trials daquela metade — é essa a comparação que o teste faz.",
    )
    return _save(figure, output_dir, name)


def _kata_panel(axes: plt.Axes, observations: pd.DataFrame, metric_key: str) -> None:
    katas = sorted(observations["kata_id"].unique())
    for index, kata in enumerate(katas):
        cell = observations.loc[observations["kata_id"] == kata]
        values = {
            treatment: cell.loc[cell["treatment"] == treatment, metric_key].median()
            for treatment in TREATMENTS
        }
        axes.plot(
            [index, index], [values[WITHOUT_AI], values[WITH_AI]],
            color=CONNECTOR_COLOR, linewidth=2.2, zorder=2,
        )
        for treatment in TREATMENTS:
            axes.scatter(
                index, values[treatment], s=200,
                color=TREATMENT_COLORS[treatment], edgecolor=SURFACE,
                linewidth=2.0, zorder=3,
            )
            above = values[treatment] >= values[
                WITH_AI if treatment == WITHOUT_AI else WITHOUT_AI
            ]
            axes.annotate(
                _format(values[treatment], metric_key),
                xy=(index, values[treatment]),
                xytext=(0, 16 if above else -24), textcoords="offset points",
                ha="center", fontsize=13, fontweight="bold",
                color=TREATMENT_COLORS[treatment],
            )

    axes.set_xticks(range(len(katas)))
    axes.set_xticklabels([kata.replace("kata-", "Kata ") for kata in katas])
    axes.set_xlim(-0.6, len(katas) - 0.4)
    axes.set_ylabel(AXIS_LABELS[metric_key])
    axes.margins(y=0.22)
    _horizontal_only_grid(axes)


def plot_results_by_kata(
    observations: pd.DataFrame, output_dir: Path, name: str
) -> Path:
    """Figura 3 — os valores observados em cada exercício."""
    figure, panels, footer = _figure_with_footer(2, 1, (14.0, 11.0))

    for axes, metric_key in zip(panels, (LOC.key, CYCLOMATIC_COMPLEXITY.key)):
        _kata_panel(axes, observations, metric_key)
        axes.set_title(SHORT_NAMES[metric_key])

    figure.suptitle(
        "Os exercícios são muito diferentes entre si:\n"
        "o Kata 4 tem o código mais longo e mais complexo de todos",
        fontsize=19, fontweight="bold",
    )
    _fill_footer(
        footer,
        "Atenção: os dois pontos de um mesmo kata são de pessoas diferentes — "
        "ninguém fez o mesmo kata nas duas condições.\n"
        "Por isso a diferença dentro de um kata não mede o efeito da IA; mostra "
        "apenas como os valores ficaram.",
    )
    return _save(figure, output_dir, name)


#: Afastamento de pontos que cairiam na mesma coordenada.
OVERLAP_NUDGE = 0.32


def plot_size_versus_complexity(
    observations: pd.DataFrame, output_dir: Path, name: str
) -> Path:
    """Figura 4 — relação entre tamanho e complexidade do código."""
    figure, panels, footer = _figure_with_footer(1, 1, (12.0, 9.5))
    axes = panels[0]

    coincident = observations.duplicated(
        subset=[LOC.key, CYCLOMATIC_COMPLEXITY.key], keep=False
    )
    nudge_rank = observations.groupby(
        [LOC.key, CYCLOMATIC_COMPLEXITY.key]
    ).cumcount()

    for (_, trial), overlaps, rank in zip(
        observations.iterrows(), coincident, nudge_rank
    ):
        offset = (rank - 0.5) * 2 * OVERLAP_NUDGE if overlaps else 0.0
        axes.scatter(
            trial[LOC.key] + offset, trial[CYCLOMATIC_COMPLEXITY.key],
            s=200, color=TREATMENT_COLORS[trial["treatment"]],
            edgecolor=SURFACE, linewidth=2.0, alpha=0.92, zorder=3,
        )

    correlation = observations[LOC.key].corr(
        observations[CYCLOMATIC_COMPLEXITY.key], method="spearman"
    )
    axes.set_xlabel("Linhas de código\n(menos linhas = código mais enxuto)")
    axes.set_ylabel("Complexidade do código\n(número menor = mais simples)")
    axes.set_title(
        "Quanto mais linhas tem o código, maior tende a ser sua complexidade",
        fontsize=17,
    )
    axes.margins(0.10)
    _horizontal_only_grid(axes)

    _fill_footer(
        footer,
        f"Cada bolinha é um dos {len(observations)} trials. A relação é "
        f"moderada ({correlation:.2f}".replace(".", ",") + "): tamanho e complexidade "
        "sobem juntos, mas não de forma exata.\n"
        f"{int(coincident.sum())} trials tinham valores idênticos e foram "
        "levemente afastados para não ficarem um sobre o outro.",
    )
    return _save(figure, output_dir, name)


def plot_complexity_per_line(
    observations: pd.DataFrame, output_dir: Path, name: str
) -> Path:
    """Figura 5 — complexidade já descontado o tamanho do código."""
    figure, panels, footer = _figure_with_footer(1, 1, (10.5, 10.0))
    axes = panels[0]

    _dot_column_panel(axes, observations, "cc_per_loc")
    axes.set_title(
        "Descontando o tamanho, o código com IA teve\nmais complexidade por linha",
        fontsize=17,
    )

    _fill_footer(
        footer,
        "Cada bolinha é um trial. Divide-se a complexidade pelo número\n"
        "de linhas, para comparar códigos de tamanhos diferentes.\n"
        "Parte da diferença vem de linhas em branco, que contam como\n"
        "linha: sem elas, a diferença cai pela metade.",
    )
    return _save(figure, output_dir, name)


def generate_figures(observations: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Gera a suíte de RQ3 e devolve os caminhos em ordem determinística."""
    _apply_style()
    return [
        plot_where_the_trials_landed(
            observations, output_dir, "fig1_distribuicao_por_tratamento.png"
        ),
        plot_paired_by_participant(
            observations, output_dir, "fig2_comparacao_pareada.png"
        ),
        plot_results_by_kata(
            observations, output_dir, "fig3_resultados_por_kata.png"
        ),
        plot_size_versus_complexity(
            observations, output_dir, "fig4_cc_vs_loc.png"
        ),
        plot_complexity_per_line(
            observations, output_dir, "fig5_complexidade_normalizada.png"
        ),
    ]
