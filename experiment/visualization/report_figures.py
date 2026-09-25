"""Figuras do relatório final (RQ1, RQ2, RQ3) — Issues #17/#21.

Cada figura responde a uma única pergunta. Os números vêm das análises já
validadas (#15: `rq1_rq2`; #16: `rq3`); nada é digitado à mão, nenhum dado
bruto é alterado e nenhum p-valor é desenhado — a inferência fica nas tabelas
do relatório.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from experiment.analysis.rq1_rq2 import TIME_BOX_SECONDS, Rq1Analysis  # noqa: E402
from experiment.analysis.rq3 import Rq3Results  # noqa: E402
from experiment.analysis.rq3_data import TREATMENTS, WITH_AI, WITHOUT_AI  # noqa: E402

# Duas cores em todas as figuras, seguras para daltonismo (mesma paleta da #16).
COLORS = {WITHOUT_AI: "#2a78d6", WITH_AI: "#eb6834"}
LABELS = {WITHOUT_AI: "Sem IA", WITH_AI: "Com IA"}
INK = "#1f1f1e"
MUTED = "#5b5a56"
GRID = "#e4e3df"

PARTICIPANT_ORDER = ("Arthur", "Guilherme", "Marcos")
#: Ressalvas de proveniência dos tempos (Seção 3.3.4 do relatório).
TIME_CAVEATS = {
    "Marcos": "ressalva: tempos com IA só por autorrelato",
}
TIME_TICKS = {
    30: "30 s", 60: "1 min", 120: "2 min", 300: "5 min",
    600: "10 min", 1200: "20 min", TIME_BOX_SECONDS: "35 min",
}
SAMPLE_NOTE = "n = 9 trials por tratamento · 3 participantes"
#: Deslocamento horizontal fixo dos pontos de uma coluna — determinístico.
SPREAD = (-0.12, 0.0, 0.12, -0.06, 0.06, -0.18, 0.18, -0.24, 0.24)

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 12.5,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": INK,
        "axes.edgecolor": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "xtick.color": INK,
        "ytick.color": MUTED,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def _br(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _footer(fig: Figure, text: str) -> None:
    fig.text(0.01, 0.005, text, ha="left", va="bottom", fontsize=9, color=MUTED, style="italic")


def _treatment_axis(ax: Axes) -> None:
    ax.set_xticks(range(len(TREATMENTS)), [LABELS[t] for t in TREATMENTS])
    ax.set_xlim(-0.6, len(TREATMENTS) - 0.4)
    for tick, treatment in zip(ax.get_xticklabels(), TREATMENTS):
        tick.set_color(COLORS[treatment])
        tick.set_fontweight("bold")


def _box_with_points(
    ax: Axes, values: dict[str, pd.Series], digits: int
) -> dict[tuple[str, float], float]:
    """Boxplot (IQR, bigodes de Tukey) + todos os trials + mediana rotulada.

    Devolve a posição x de cada ponto, para que um rótulo de outlier aponte para o
    ponto desenhado, e não para o centro da coluna.
    """
    x_of: dict[tuple[str, float], float] = {}
    for position, treatment in enumerate(TREATMENTS):
        series = values[treatment].reset_index(drop=True)
        ax.boxplot(
            [series], positions=[position], widths=0.5, whis=1.5, showfliers=False,
            patch_artist=True, zorder=1,
            boxprops={"facecolor": COLORS[treatment], "alpha": 0.18, "edgecolor": COLORS[treatment]},
            whiskerprops={"color": COLORS[treatment]}, capprops={"color": COLORS[treatment]},
            medianprops={"color": INK, "linewidth": 2.4},
        )
        order = series.sort_values().index
        for rank, index in enumerate(order):
            x = position + SPREAD[rank % len(SPREAD)]
            x_of[(treatment, round(float(series[index]), 9))] = x
            ax.scatter(
                x, series[index], s=46,
                color=COLORS[treatment], edgecolor="white", linewidth=0.8, zorder=3,
            )
        median = series.median()
        ax.hlines(median, position - 0.25, position + 0.25, color=INK, linewidth=2.4, zorder=4)
        ax.annotate(
            _br(median, digits), (position + 0.27, median), xytext=(4, 0),
            textcoords="offset points", va="center", fontsize=11, fontweight="bold", color=INK,
        )
    _treatment_axis(ax)
    return x_of


def _label_outlier(
    ax: Axes, x_of: dict[tuple[str, float], float], treatment: str, value: float, text: str,
    dy: float = 0,
) -> None:
    """Rótulo à esquerda do ponto, ligado a ele por um traço curto (dy desloca na vertical)."""
    x = x_of[(treatment, round(float(value), 9))]
    ax.annotate(
        text, (x, value), xytext=(-14, dy), textcoords="offset points",
        ha="right", va="center", fontsize=9, color=MUTED,
        arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.7, "shrinkB": 4},
    )


def _time_axis(ax: Axes) -> None:
    ax.set_yscale("log")
    ax.set_ylim(17, TIME_BOX_SECONDS * 1.25)
    ax.set_yticks(list(TIME_TICKS), list(TIME_TICKS.values()))
    ax.minorticks_off()
    ax.axhline(TIME_BOX_SECONDS, color=MUTED, linestyle="--", linewidth=1)


def _save(fig: Figure, out_dir: Path, name: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    png, pdf = out_dir / f"{name}.png", out_dir / f"{name}.pdf"
    fig.savefig(png, dpi=200, bbox_inches="tight", metadata={"Software": None})
    fig.savefig(pdf, bbox_inches="tight", metadata={"CreationDate": None})
    plt.close(fig)
    return [png, pdf]


# ---------------------------------------------------------------------------
# RQ1
# ---------------------------------------------------------------------------


def rq1_time_by_treatment(obs: pd.DataFrame, rq1: Rq1Analysis) -> Figure:
    """Gráfico 1 — tamanho da diferença entre os tratamentos e dispersão de cada um."""
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    values = {t: obs.loc[obs["treatment"] == t, "elapsed_seconds"] for t in TREATMENTS}
    x_of = _box_with_points(ax, values, digits=1)
    _time_axis(ax)
    ax.text(-0.55, TIME_BOX_SECONDS * 1.05, "time-box (35 min)", fontsize=9, color=MUTED)
    for treatment, result in rq1.outliers.items():
        for trial in result.outliers:
            _label_outlier(
                ax, x_of, treatment.value, trial.elapsed_seconds,
                f"{trial.participant} {trial.kata_id}\n{_br(trial.elapsed_seconds)} s (outlier)",
                # Perto do time-box, o rótulo desce para não cruzar a linha tracejada.
                dy=-12 if trial.elapsed_seconds > 0.7 * TIME_BOX_SECONDS else 0,
            )
    ax.set_ylabel("Tempo até todos os testes passarem (escala log)")
    ax.set_title("RQ1 — Tempo até green por tratamento")
    censored = sum(rq1.censored_by_treatment.values())
    _footer(fig, f"{SAMPLE_NOTE} · {censored} trials censurados · caixa = IQR, traço = mediana")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def rq1_time_by_participant(obs: pd.DataFrame, rq1: Rq1Analysis) -> Figure:
    """Gráfico 2 — a diferença dentro de cada pessoa (unidade do Wilcoxon) e os katas de cada lado."""
    ratios = {c.participant: c.with_ai.median / c.without_ai.median for c in rq1.by_participant}
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 5.2), sharey=True)
    for ax, participant in zip(axes, PARTICIPANT_ORDER):
        rows = obs[obs["participant"] == participant]
        for position, treatment in enumerate(TREATMENTS):
            side = rows[rows["treatment"] == treatment].sort_values("kata_id")
            median = side["elapsed_seconds"].median()
            offsets = (-0.16, 0.0, 0.16)
            for offset, (_, trial) in zip(offsets, side.iterrows()):
                x, y = position + offset, trial["elapsed_seconds"]
                ax.scatter(x, y, s=46, color=COLORS[treatment], edgecolor="white", zorder=3)
                # Abaixo da mediana, o rótulo vai para baixo, para não cair sobre o traço.
                below = y < median * 0.99
                ax.annotate(
                    trial["kata_id"].removeprefix("kata-"), (x, y), xytext=(0, -7 if below else 6),
                    va="top" if below else "bottom",
                    textcoords="offset points", ha="center", fontsize=8.5, color=MUTED, zorder=4,
                    bbox={"boxstyle": "round,pad=0.1", "facecolor": "white", "edgecolor": "none", "alpha": 0.85},
                )
            ax.hlines(median, position - 0.28, position + 0.28, color=INK, linewidth=2.2, zorder=2)
        _treatment_axis(ax)
        _time_axis(ax)
        ax.set_title(
            f"{participant}\ncom IA = {_br(100 * ratios[participant])}% do tempo sem IA",
            fontsize=11.5,
        )
        if participant in TIME_CAVEATS:
            ax.text(
                0.0, -0.13, TIME_CAVEATS[participant], transform=ax.transAxes, fontsize=8.5,
                color=MUTED, style="italic",
            )
    axes[0].set_ylabel("Tempo até todos os testes passarem (escala log)")
    fig.suptitle(
        "RQ1 — Tempo por participante (número = kata; traço = mediana)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(fig, "3 trials por tratamento em cada painel · o Wilcoxon compara as duas medianas de cada participante")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


# ---------------------------------------------------------------------------
# RQ2
# ---------------------------------------------------------------------------


def rq2_trial_outcomes(obs: pd.DataFrame) -> Figure:
    """Gráfico 3 — heatmap participante × kata: testes passando em cada um dos 18 trials.

    A cor da célula é o tratamento; o texto, os testes passando sobre o total do kata.
    Mostra, trial a trial, que a métrica não variou e em qual tratamento cada kata foi feito.
    """
    katas = sorted(obs["kata_id"].unique())
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    for row, participant in enumerate(PARTICIPANT_ORDER):
        for col, kata in enumerate(katas):
            trial = obs[(obs["participant"] == participant) & (obs["kata_id"] == kata)].iloc[0]
            color = COLORS[trial["treatment"]]
            ax.add_patch(Rectangle(
                (col - 0.5, row - 0.5), 1, 1, facecolor=color, alpha=0.22,
                edgecolor="white", linewidth=3, zorder=1,
            ))
            ax.text(
                col, row - 0.08, f"{int(trial['tests_passing'])}/{int(trial['tests_total'])}",
                ha="center", va="center", fontsize=13, fontweight="bold", color=INK, zorder=2,
            )
            ax.text(
                col, row + 0.24, f"{LABELS[trial['treatment']]} · {_br(trial['success_rate_percent'], 0)}%",
                ha="center", va="center", fontsize=8.5, color=color, fontweight="bold", zorder=2,
            )
    ax.set_xlim(-0.5, len(katas) - 0.5)
    ax.set_ylim(len(PARTICIPANT_ORDER) - 0.5, -0.5)
    ax.set_xticks(range(len(katas)), katas)
    ax.set_yticks(range(len(PARTICIPANT_ORDER)), PARTICIPANT_ORDER)
    ax.tick_params(length=0)
    ax.xaxis.tick_top()
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    failing = int(obs["tests_failing"].sum())
    censored = int(obs["censored"].sum())
    ax.set_title(
        f"RQ2 — Testes de aceitação passando em cada trial ({failing} falhando, {censored} censurados)",
        pad=28,
    )
    ax.legend(
        handles=[Patch(color=COLORS[t], alpha=0.35, label=LABELS[t]) for t in (WITHOUT_AI, WITH_AI)],
        loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False,
    )
    _footer(
        fig,
        "Célula = testes passando / total do kata · cor = tratamento. A taxa de sucesso só ficaria abaixo de 100% num trial\n"
        "encerrado pelo time-box. Nenhum foi: a métrica não teve como variar, e isso não indica ausência de defeitos.",
    )
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    return fig


# ---------------------------------------------------------------------------
# RQ3
# ---------------------------------------------------------------------------


def _outliers(results: Rq3Results, metric: str) -> pd.DataFrame:
    table = results.quality.outliers
    return table[table["metric"] == metric] if table is not None else table


def rq3_loc_cc_by_treatment(results: Rq3Results) -> Figure:
    """Gráficos 4 e 5 — tamanho (LOC) e complexidade absoluta (CC), um painel por métrica."""
    obs = results.observations
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2))
    panels = (
        ("loc", "LOC", "Linhas de código (loc bruto do Radon)", "Tamanho — LOC", 0),
        (
            "cyclomatic_complexity_avg", "CC", "Complexidade ciclomática da função",
            "Complexidade — CC", 0,
        ),
    )
    for ax, (column, metric, ylabel, title, digits) in zip(axes, panels):
        values = {t: obs.loc[obs["treatment"] == t, column] for t in TREATMENTS}
        x_of = _box_with_points(ax, values, digits=digits)
        for _, outlier in _outliers(results, metric).iterrows():
            _label_outlier(
                ax, x_of, outlier["treatment"], outlier["value"],
                f"{outlier['participant']} {outlier['kata_id']}\n{_br(outlier['value'], 0)} (outlier)",
            )
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    fig.suptitle("RQ3 — LOC e CC por tratamento", x=0.01, ha="left", fontweight="bold", fontsize=13)
    _footer(fig, f"{SAMPLE_NOTE} · caixa = IQR, traço = mediana · LOC inclui linhas em branco e comentários")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def _slope_panel(ax: Axes, medians: pd.DataFrame, digits: int) -> None:
    """Uma linha por participante, da mediana sem IA à mediana com IA, com rótulos."""
    for participant in PARTICIPANT_ORDER:
        before, after = medians.loc[participant, WITHOUT_AI], medians.loc[participant, WITH_AI]
        ax.plot([0, 1], [before, after], color=MUTED, linewidth=1.4, zorder=1)
        for x, treatment, value in ((0, WITHOUT_AI, before), (1, WITH_AI, after)):
            ax.scatter(x, value, s=60, color=COLORS[treatment], edgecolor="white", zorder=3)
    # Empatados dividem um rótulo; rótulos próximos são afastados na vertical.
    low, high = medians.to_numpy().min(), medians.to_numpy().max()
    min_gap = 0.06 * (high - low if high > low else 1.0)
    for x, treatment, side in ((0, WITHOUT_AI, "right"), (1, WITH_AI, "left")):
        by_value: dict[float, list[str]] = {}
        for participant in PARTICIPANT_ORDER:
            by_value.setdefault(round(float(medians.loc[participant, treatment]), 9), []).append(participant)
        label_y: list[float] = []
        for value in sorted(by_value):
            label_y.append(max(value, label_y[-1] + min_gap) if label_y else value)
        for (value, label_at) in zip(sorted(by_value), label_y):
            names_text = ", ".join(by_value[value])
            text = f"{names_text}  {_br(value, digits)}" if x == 0 else f"{_br(value, digits)}  {names_text}"
            ax.annotate(
                text, (x, value), xytext=(x - 0.07 if x == 0 else x + 0.07, label_at),
                textcoords="data", ha=side, va="center", fontsize=9.5, color=INK,
            )
    _treatment_axis(ax)
    ax.set_xlim(-1.0, 2.0)


def _participant_medians(obs: pd.DataFrame, column: str) -> pd.DataFrame:
    return obs.groupby(["participant", "treatment"])[column].median().unstack()


def rq3_pairs(results: Rq3Results) -> Figure:
    """Gráfico 6 — a comparação que o Wilcoxon faz (N = 3) para LOC e CC."""
    obs = results.observations
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.0))
    for ax, (column, title, digits) in zip(
        axes,
        (("loc", "LOC (linhas)", 0), ("cyclomatic_complexity_avg", "CC", 0)),
    ):
        _slope_panel(ax, _participant_medians(obs, column), digits)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(title)
    fig.suptitle(
        "RQ3 — LOC e CC por participante (mediana dos 3 trials de cada lado)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(fig, "Cada lado contém katas diferentes: a mesma direção nos 3 pares não é, sozinha, evidência de efeito.")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


#: Área da bolha (pt²) por segundo até o green: a área é proporcional ao tempo.
BUBBLE_AREA_PER_SECOND = 1.1
BUBBLE_LEGEND_SECONDS = {30: "30 s", 300: "5 min", 1800: "30 min"}


def rq3_cc_vs_loc(results: Rq3Results) -> Figure:
    """Gráfico 7 — bolhas: tamanho (LOC) × complexidade (CC), com o tempo até green como área."""
    obs = results.observations.copy()
    obs["area"] = obs["elapsed_seconds"] * BUBBLE_AREA_PER_SECOND
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    # Das maiores para as menores: em (9, 4) a bolha pequena com IA fica por cima da grande sem IA.
    for _, trial in obs.sort_values("area", ascending=False).iterrows():
        ax.scatter(
            trial["loc"], trial["cyclomatic_complexity_avg"], s=trial["area"],
            color=COLORS[trial["treatment"]], alpha=0.55, edgecolor="white", linewidth=1, zorder=3,
        )
    placed: list[tuple[float, float]] = []
    for _, trial in obs.sort_values(["loc", "cyclomatic_complexity_avg"]).iterrows():
        x, y = trial["loc"], trial["cyclomatic_complexity_avg"]
        radius = math.sqrt(trial["area"] / math.pi)
        # Rótulo à direita da bolha; acima dela se há outra bolha logo à direita;
        # se outro rótulo já está perto, sobe um pouco.
        neighbour_right = ((obs["loc"] > x) & (obs["loc"] <= x + 2)
                           & ((obs["cyclomatic_complexity_avg"] - y).abs() < 0.6)).any()
        dy = 9 if any(abs(x - px) < 2.5 and abs(y - py) < 0.6 for px, py in placed) else 0
        placed.append((x, y))
        ax.annotate(
            f"{trial['participant'][0]}{trial['kata_id'].removeprefix('kata-')}", (x, y),
            xytext=(0, radius + 3) if neighbour_right else (radius + 3, dy), textcoords="offset points",
            ha="center" if neighbour_right else "left", va="bottom" if neighbour_right else "center",
            fontsize=8.5, color=INK, zorder=4,
        )
    rho = obs["loc"].corr(obs["cyclomatic_complexity_avg"], method="spearman")
    ax.text(0.01, 0.97, f"Spearman ρ (LOC × CC) = {_br(rho, 2)}", transform=ax.transAxes, va="top", fontsize=10.5)
    color_legend = ax.legend(
        handles=[Patch(color=COLORS[t], alpha=0.7, label=LABELS[t]) for t in TREATMENTS],
        loc="lower left", bbox_to_anchor=(1.01, 0.0), frameon=False,
    )
    ax.add_artist(color_legend)
    ax.legend(
        handles=[
            ax.scatter([], [], s=seconds * BUBBLE_AREA_PER_SECOND, color=MUTED, alpha=0.35, edgecolor="white")
            for seconds in BUBBLE_LEGEND_SECONDS
        ],
        labels=list(BUBBLE_LEGEND_SECONDS.values()), title="Tempo até green\n(área da bolha)",
        loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, labelspacing=2.2,
        borderpad=1.2, handletextpad=1.6,
        scatterpoints=1, title_fontsize=9.5, fontsize=9.5,
    )
    ax.set_xlim(4, 44)
    ax.set_ylim(2.8, 15.8)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("LOC (linhas)")
    ax.set_ylabel("CC (complexidade ciclomática)")
    ax.set_title("RQ3 — LOC × CC × tempo até green nos 18 trials")
    _footer(
        fig,
        "Cada bolha é um trial (inicial do participante + kata) · área proporcional ao tempo até green (RQ1) · "
        "em (9, 4) há duas bolhas: G05 sem IA e M05 com IA",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def rq3_mi_two_series(results: Rq3Results) -> Figure:
    """Gráfico 8 — MI pareado nas duas séries (a coletada só é válida dentro do participante)."""
    obs = results.observations
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.9))
    for ax, (column, title) in zip(
        axes,
        (
            ("maintainability_index", "MI como coletado (principal)"),
            ("maintainability_index_harmonized", "MI harmonizado (sensibilidade)"),
        ),
    ):
        _slope_panel(ax, _participant_medians(obs, column), digits=2)
        ax.set_title(title)
    axes[0].set_ylabel("Índice de manutenibilidade (0–100)")
    fig.suptitle(
        "RQ3 — MI por participante, nas duas séries (mediana dos 3 trials de cada lado)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(
        fig,
        "Os níveis das duas séries diferem pela convenção de cálculo (Seção 4.4): compare a direção dentro de cada "
        "painel, não os valores entre painéis.",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def rq3_normalized_cc(results: Rq3Results) -> Figure:
    """Gráfico 9 — CC normalizada por LOC e sua sensibilidade à contagem de linhas."""
    obs = results.observations.merge(
        results.quality.integrity[["participant", "kata_id", "treatment", "sloc_recomputed"]],
        on=["participant", "kata_id", "treatment"],
    )
    obs["cc_per_sloc"] = obs["cyclomatic_complexity_avg"] / obs["sloc_recomputed"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2), sharey=True)
    panels = (
        ("cc_per_loc", "CC / LOC (loc bruto, com linhas em branco)", "CC/LOC"),
        ("cc_per_sloc", "CC / SLOC (só linhas de código)", None),
    )
    for ax, (column, title, outlier_metric) in zip(axes, panels):
        values = {t: obs.loc[obs["treatment"] == t, column] for t in TREATMENTS}
        x_of = _box_with_points(ax, values, digits=3)
        if outlier_metric:
            for _, outlier in _outliers(results, outlier_metric).iterrows():
                _label_outlier(
                    ax, x_of, outlier["treatment"], outlier["value"],
                    f"{outlier['participant']} {outlier['kata_id']}\n{_br(outlier['value'], 3)} (outlier)",
                )
        ax.set_title(title, fontsize=11.5)
    axes[0].set_ylabel("Complexidade ciclomática por linha")
    fig.suptitle(
        "RQ3 — Complexidade ciclomática normalizada por LOC (métrica derivada de CC e LOC)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(fig, f"{SAMPLE_NOTE} · caixa = IQR, traço = mediana · SLOC recalculado do código versionado (#16)")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


FIGURE_NAMES = (
    "rq1_tempo_por_tratamento",
    "rq1_tempo_por_participante",
    "rq2_desfecho_trials",
    "rq3_loc_cc_por_tratamento",
    "rq3_loc_cc_por_participante",
    "rq3_cc_vs_loc",
    "rq3_mi_duas_series",
    "rq3_cc_normalizada",
)


def build_all(rq1: Rq1Analysis, results: Rq3Results) -> dict[str, Figure]:
    obs = results.observations
    figures = (
        rq1_time_by_treatment(obs, rq1),
        rq1_time_by_participant(obs, rq1),
        rq2_trial_outcomes(obs),
        rq3_loc_cc_by_treatment(results),
        rq3_pairs(results),
        rq3_cc_vs_loc(results),
        rq3_mi_two_series(results),
        rq3_normalized_cc(results),
    )
    return dict(zip(FIGURE_NAMES, figures))


def save_all(figures: dict[str, Figure], out_dir: Path) -> list[Path]:
    return [path for name, fig in figures.items() for path in _save(fig, out_dir, name)]



# ---------------------------------------------------------------------------
# Bônus (Issue #18) — exploratório
# ---------------------------------------------------------------------------


def bonus_mi_components(components: pd.DataFrame) -> Figure:
    """O que move o MI nestes dados: MI harmonizado contra cada componente da fórmula."""
    panels = (
        ("lloc", "LLOC (linhas lógicas)"),
        ("cc_total", "CC (complexidade ciclomática)"),
        ("halstead_volume", "Volume de Halstead"),
    )
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.6), sharey=True)
    for ax, (column, xlabel) in zip(axes, panels):
        # Pontos coincidentes (ex.: Arthur kata-06 sem IA e Marcos kata-06 com IA)
        # são deslocados na horizontal para que nenhum fique escondido.
        step = 0.035 * (components[column].max() - components[column].min())
        seen: dict[tuple[float, float], int] = {}
        for treatment in TREATMENTS:
            side = components[components["treatment"] == treatment]
            for _, trial in side.iterrows():
                key = (trial[column], round(trial["maintainability_index_harmonized"], 6))
                nudge = step * seen.get(key, 0)
                seen[key] = seen.get(key, 0) + 1
                ax.scatter(
                    trial[column] + nudge, trial["maintainability_index_harmonized"], s=46,
                    color=COLORS[treatment], edgecolor="white", zorder=3,
                )
        rho = components[column].corr(components["maintainability_index_harmonized"], method="spearman")
        ax.text(0.97, 0.96, f"ρ = {_br(rho, 2)}", transform=ax.transAxes, ha="right", va="top")
        ax.grid(axis="x", visible=True)
        ax.set_xlabel(xlabel)
    axes[0].set_ylabel("MI harmonizado (0–100)")
    axes[-1].legend(
        handles=[Patch(color=COLORS[t], label=LABELS[t]) for t in TREATMENTS],
        loc="lower left", frameon=False,
    )
    fig.suptitle(
        "Bônus — MI harmonizado contra os componentes da fórmula (18 trials)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(
        fig,
        "Exploratório · ρ de Spearman descritivo · comentários = 0% em todos os trials (termo constante) · "
        "parte da associação é mecânica: os componentes entram na fórmula do MI\n"
        "Pontos coincidentes deslocados levemente na horizontal",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig


def bonus_prompts_quality(prompts_quality: pd.DataFrame) -> Figure:
    """Nº de prompts × CC e MI nos trials com IA, com o participante explícito no eixo."""
    values = sorted(prompts_quality["n_prompts"].unique())
    tick_labels = []
    for value in values:
        names = ", ".join(
            sorted(prompts_quality.loc[prompts_quality["n_prompts"] == value, "participant"].unique())
        )
        tick_labels.append(f"{int(value)} prompt{'s' if value > 1 else ''}\n({names})")
    panels = (
        ("cyclomatic_complexity_avg", "CC (complexidade ciclomática)", 0),
        ("maintainability_index_harmonized", "MI harmonizado (0–100)", 1),
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.9))
    for ax, (column, ylabel, digits) in zip(axes, panels):
        for position, value in enumerate(values):
            group = prompts_quality[prompts_quality["n_prompts"] == value].sort_values(["participant", "kata_id"])
            for rank, (_, trial) in enumerate(group.iterrows()):
                x = position + SPREAD[rank % len(SPREAD)]
                ax.scatter(x, trial[column], s=46, color=COLORS[WITH_AI], edgecolor="white", zorder=3)
                ax.annotate(
                    f"{trial['participant'][0]}{trial['kata_id'].removeprefix('kata-')}", (x, trial[column]),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=MUTED,
                )
        ax.set_xticks(range(len(values)), tick_labels)
        ax.set_xlim(-0.6, len(values) - 0.4)
        if digits == 0:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
    fig.suptitle(
        "Bônus — Nº de prompts × CC e MI nos 9 trials com IA",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _footer(
        fig,
        "Rótulo = inicial do participante + kata · o nº de prompts é constante dentro de cada participante:\n"
        "a comparação entre as colunas é também entre participantes e katas diferentes — não mede o efeito dos prompts.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig


#: Métricas dos gráficos multimétricos: (coluna, rótulo, casas decimais). Ordem fixa:
#: tempo, tamanho, complexidade e, por último, o MI, que é composto dos anteriores.
RADAR_AXES = (
    ("elapsed_seconds", "Tempo até green (s)", 1),
    ("loc", "LOC", 0),
    ("lloc", "LLOC", 0),
    ("halstead_volume", "Volume de\nHalstead", 1),
    ("cyclomatic_complexity_avg", "CC", 0),
    ("cc_per_loc", "CC/LOC", 3),
    ("maintainability_index_harmonized", "MI harmonizado", 2),
)
SHORT_LABELS = {
    "elapsed_seconds": "Tempo", "loc": "LOC", "lloc": "LLOC", "halstead_volume": "Volume\nHalstead",
    "cyclomatic_complexity_avg": "CC", "cc_per_loc": "CC/LOC", "maintainability_index_harmonized": "MI\nharmonizado",
}
TRIAL_KEYS = ["participant", "kata_id", "treatment"]


def _trial_metrics(components: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por trial com todas as métricas dos gráficos multimétricos."""
    return observations.merge(components[[*TRIAL_KEYS, "lloc", "halstead_volume"]], on=TRIAL_KEYS)


def _side_panel(fig: Figure, x: float, top: float, title: str, rows: list[str]) -> None:
    """Bloco de texto à direita da figura: título em negrito e uma linha por item."""
    fig.text(x, top, title, fontsize=11, fontweight="bold", color=INK, va="top")
    fig.text(x, top - 0.07, "\n".join(rows), fontsize=9.5, color=INK, va="top", linespacing=1.55)


def bonus_radar_profile(components: pd.DataFrame, observations: pd.DataFrame) -> Figure:
    """Perfil multimétrico de cada tratamento: mediana de cada métrica em % da maior das duas."""
    merged = _trial_metrics(components, observations)
    columns = [column for column, _, _ in RADAR_AXES]
    medians = merged.groupby("treatment")[columns].median()
    shares = 100 * medians / medians.max()

    angles = [2 * math.pi * i / len(RADAR_AXES) for i in range(len(RADAR_AXES))]
    closed = angles + angles[:1]
    fig = plt.figure(figsize=(10.5, 5.4))
    ax = fig.add_axes((0.06, 0.1, 0.44, 0.74), projection="polar")
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    for treatment in (WITHOUT_AI, WITH_AI):
        values = shares.loc[treatment].tolist()
        ax.plot(closed, values + values[:1], color=COLORS[treatment], linewidth=2, zorder=3)
        ax.fill(closed, values + values[:1], color=COLORS[treatment], alpha=0.16, zorder=2)
        ax.scatter(angles, values, s=34, color=COLORS[treatment], edgecolor="white", zorder=4)
    labels = [
        f"{label}\n{_br(medians.loc[WITHOUT_AI, column], digits)} × {_br(medians.loc[WITH_AI, column], digits)}"
        for column, label, digits in RADAR_AXES
    ]
    ax.set_xticks(angles, labels, fontsize=9.5)
    ax.tick_params(axis="x", pad=12)
    ax.set_ylim(0, 105)
    ax.set_yticks([25, 50, 75, 100], ["25%", "50%", "75%", "100%"], fontsize=8, color=MUTED)
    ax.set_rlabel_position(180 / len(RADAR_AXES))
    ax.grid(color=GRID)
    ax.spines["polar"].set_color(MUTED)
    fig.suptitle(
        "Bônus — Perfil multimétrico por tratamento (mediana, % da maior das duas)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    fig.legend(
        handles=[Patch(color=COLORS[t], label=LABELS[t]) for t in (WITHOUT_AI, WITH_AI)],
        loc="upper left", bbox_to_anchor=(0.6, 0.86), ncol=2, frameon=False, fontsize=10.5,
    )
    with_ai_share = shares.loc[WITH_AI]
    rows = [
        f"{label.replace(chr(10), ' ').removesuffix(' (s)')}: {_br(with_ai_share[column], 1)}%"
        for column, label, _ in RADAR_AXES
    ]
    _side_panel(fig, 0.6, 0.74, "Com IA, em % do sem IA", rows)
    fig.text(
        0.6, 0.2,
        "Rótulo de cada eixo: mediana sem IA × com IA.\n"
        "MI: maior = melhor; demais: maior = mais tempo,\n"
        "código ou complexidade. Descritivo, sem teste;\n"
        "ressalvas na Seção 5.1 do relatório.",
        fontsize=9, color=MUTED, style="italic", va="top", linespacing=1.5,
    )
    return fig


def bonus_correlation_heatmap(components: pd.DataFrame, observations: pd.DataFrame) -> Figure:
    """Heatmap de correlação de Spearman entre as métricas, nos 18 trials (triângulo inferior)."""
    merged = _trial_metrics(components, observations)
    columns = [column for column, _, _ in RADAR_AXES]
    rho = merged[columns].corr(method="spearman")
    labels = [SHORT_LABELS[c].replace("\n", " ") for c in columns]

    fig = plt.figure(figsize=(10.5, 5.4))
    ax = fig.add_axes((0.15, 0.2, 0.42, 0.66))
    cax = fig.add_axes((0.59, 0.2, 0.014, 0.66))
    cmap = plt.get_cmap("RdBu_r")
    size = len(columns) - 1
    # Só o triângulo inferior, sem a diagonal (ρ = 1 de cada métrica consigo mesma).
    for i in range(size):
        for j in range(i + 1):
            value = rho.iloc[i + 1, j]
            ax.add_patch(Rectangle(
                (j - 0.5, i - 0.5), 1, 1, facecolor=cmap((value + 1) / 2),
                edgecolor="white", linewidth=2,
            ))
            ax.text(
                j, i, _br(value, 2), ha="center", va="center", fontsize=9.5,
                color="white" if abs(value) >= 0.6 else INK, fontweight="bold" if abs(value) >= 0.6 else None,
            )
    ax.set_xlim(-0.5, size - 0.5)
    ax.set_ylim(size - 0.5, -0.5)
    ax.set_xticks(range(size), labels[:-1], rotation=30, ha="right")
    ax.set_yticks(range(size), labels[1:])
    ax.tick_params(length=0)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    mappable = plt.cm.ScalarMappable(cmap=cmap, norm=matplotlib.colors.Normalize(-1, 1))
    bar = fig.colorbar(mappable, cax=cax)
    bar.set_label("ρ de Spearman")
    bar.outline.set_visible(False)
    fig.suptitle(
        "Bônus — Correlação entre as métricas (Spearman, 18 trials)",
        x=0.01, ha="left", fontweight="bold", fontsize=12.5,
    )
    _side_panel(fig, 0.7, 0.86, "Como ler", [
        "Vermelho = positiva; azul = negativa.",
        "Negrito: |ρ| ≥ 0,6.",
        "",
        "Os 18 trials misturam os dois",
        "tratamentos: parte das correlações",
        "vem da diferença entre eles",
        "(ex.: tempo × LOC).",
        "",
        "Parte é mecânica: o MI é calculado",
        "a partir de LLOC, CC e volume",
        "de Halstead.",
        "",
        "Descritivo, sem p-valor.",
    ])
    return fig


BONUS_FIGURE_NAMES = (
    "bonus_radar_perfil",
    "bonus_correlacao",
    "bonus_mi_componentes",
    "bonus_prompts_qualidade",
)


def build_bonus(
    components: pd.DataFrame, prompts_quality: pd.DataFrame, observations: pd.DataFrame
) -> dict[str, Figure]:
    figures = (
        bonus_radar_profile(components, observations),
        bonus_correlation_heatmap(components, observations),
        bonus_mi_components(components),
        bonus_prompts_quality(prompts_quality),
    )
    return dict(zip(BONUS_FIGURE_NAMES, figures))
