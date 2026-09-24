"""Boxplots comparativos com IA × sem IA para o relatório — Issue #17.

Gera três figuras (RQ1 tempo, RQ2 defeitos, RQ3 estrutura) a partir da
tabela consolidada em pandas (`experiment/analysis/consolidated.py`: uma
linha por trial, com tempo, testes e métricas estáticas). Os testes
estatísticos não são recalculados aqui: o Wilcoxon pareado vem da análise da
#15 (`PairedTestResult`) e o Mann-Whitney (`rank_sum.py`) aparece como
complemento exploratório.

Cada painel mostra:

- a caixa de cada tratamento (sem outliers desenhados: todos os pontos já
  aparecem individualmente, com deslocamento horizontal fixo — sem jitter
  aleatório, para a saída ser reproduzível byte a byte);
- uma linha por participante ligando o valor dele sem IA ao valor com IA —
  o mesmo agregado usado no teste pareado (mediana; média na RQ2);
- a mediana geral de cada tratamento, por fora da caixa;
- no rótulo do eixo X, o p do Wilcoxon pareado e do Mann-Whitney, ou o
  motivo de o teste não se aplicar.

Trials censurados (time-box atingido) aparecem com marcador vazado em todas
as figuras, inclusive na RQ3: o código de um trial censurado ficou
incompleto, o que vale sinalizar também nas métricas estáticas.

Cores: slots 1 e 2 da paleta categórica de referência (validados quanto a
daltonismo e contraste). O participante é codificado pelo formato do
marcador, nunca por cor.
"""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

from experiment.analysis.rank_sum import RankSumResult, rank_sum_test  # noqa: E402
from experiment.analysis.rq1_rq2 import TIME_BOX_SECONDS, PairedTestResult  # noqa: E402
from experiment.analysis.rq1_rq2_report import _num, _p  # noqa: E402
from experiment.analysis.static_metrics_data import RQ3_METRICS  # noqa: E402
from experiment.config.lab02_design import PARTICIPANTS  # noqa: E402
from experiment.domain.enums import Treatment  # noqa: E402

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "pdf.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

# Ordem visual fixa: sem IA à esquerda, com IA à direita. Independe da ordem
# dos argumentos dos testes (sempre com IA primeiro).
POSITIONS = (1, 2)
TREATMENT_ORDER = (Treatment.WITHOUT_AI, Treatment.WITH_AI)
TREATMENT_LABEL = {Treatment.WITHOUT_AI: "Sem IA", Treatment.WITH_AI: "Com IA"}
TREATMENT_COLOR = {Treatment.WITHOUT_AI: "#eb6834", Treatment.WITH_AI: "#2a78d6"}

# Largura explícita: com posições [1, 2] o padrão do matplotlib seria 0,15.
BOX_W = 0.5
P_OFFSET = 0.08
K_OFFSET = 0.02
X_LIMITS = (0.1, 2.9)

INK = "#1f1f1e"
MUTED = "#52514e"
GRID = "#e4e3df"
PARTICIPANT_MARKERS = dict(zip(PARTICIPANTS, ("o", "s", "^", "D", "v")))
CENSORED_LABEL = "Censurado (marcador vazado)"
STATS_WRAP = 52

# (coluna da tabela consolidada, rótulo). O lado de cada teste não fica aqui:
# vem do `PairedTestResult` (definido pela #15 e por `rq3_tests`), e o
# Mann-Whitney o segue, para os dois testes de um painel nunca divergirem.
RQ1_PANEL = ("elapsed_seconds", "Tempo até green (s, escala log)")
RQ2_PANELS = (
    ("success_rate_percent", "Taxa de sucesso (%)"),
    ("tests_failing", "Testes falhando por trial"),
)
RQ3_PANELS = tuple((column, label) for _, column, label in RQ3_METRICS)
# Folga acima do time-box para a linha tracejada e os censurados ficarem visíveis.
RQ1_TOP_MARGIN = 1.2


# ---------------------------------------------------------------------------
# Texto das anotações
# ---------------------------------------------------------------------------


def fmt_p(p: float) -> str:
    return "< 0,001" if p < 0.001 else _p(p)


def p_expr(p: float) -> str:
    """`p < 0,001` ou `p = 0,125` — sem o `p = < 0,001` de concatenar direto."""
    formatted = fmt_p(p)
    return f"p {formatted}" if formatted.startswith("<") else f"p = {formatted}"


def _side(alternative: str) -> str:
    return "bilateral" if alternative == "two-sided" else "unilateral"


def paired_p(test: PairedTestResult) -> float:
    return test.p_two_sided if test.alternative == "two-sided" else test.p_one_sided


def paired_min_p(test: PairedTestResult) -> float:
    """Menor p possível no lado do teste: `min_attainable_p` da #15 é unilateral."""
    if test.alternative == "two-sided":
        return min(1.0, 2 * test.min_attainable_p)
    return test.min_attainable_p


def stats_text(paired: PairedTestResult, rank_sum: RankSumResult) -> str:
    if not paired.applicable and not rank_sum.applicable:
        return "Sem variação — testes não aplicáveis"

    lines = []
    if paired.applicable:
        line = (
            f"Wilcoxon pareado n={paired.n_pairs} ({_side(paired.alternative)}): "
            f"{p_expr(paired_p(paired))}"
        )
        p_min = paired_min_p(paired)
        if not p_min < paired.alpha:
            line += f" (mín. possível {fmt_p(p_min)})"
        lines.append(line)
    else:
        lines.append("Diferenças pareadas nulas — Wilcoxon não aplicável")

    if rank_sum.applicable:
        p = rank_sum.p_two_sided if rank_sum.alternative == "two-sided" else rank_sum.p_one_sided
        lines.append(
            f"MW {rank_sum.n_with_ai}×{rank_sum.n_without_ai} (exploratório, "
            f"{_side(rank_sum.alternative)}): {p_expr(p)}"
        )
    return "\n".join(textwrap.fill(line, STATS_WRAP) for line in lines)


# ---------------------------------------------------------------------------
# Dados por tratamento
# ---------------------------------------------------------------------------


def treatment_values(data: pd.DataFrame, column: str, treatment: Treatment) -> list[float]:
    return data.loc[data["treatment"] == treatment.value, column].tolist()


def rank_sums(
    data: pd.DataFrame,
    panels: Sequence[tuple[str, str]],
    paired_tests: dict[str, PairedTestResult],
) -> dict[str, RankSumResult]:
    """Mann-Whitney por painel, com IA contra sem IA, no mesmo lado do teste pareado."""
    return {
        label: rank_sum_test(
            treatment_values(data, column, Treatment.WITH_AI),
            treatment_values(data, column, Treatment.WITHOUT_AI),
            alternative=paired_tests[label].alternative,
        )
        for column, label in panels
    }


def _participants_present(data: pd.DataFrame) -> list[str]:
    present = set(data["participant"])
    return [p for p in PARTICIPANTS if p in present]


def _participant_offset(participant: str) -> float:
    index = PARTICIPANTS.index(participant)
    return (index - (len(PARTICIPANTS) - 1) / 2) * P_OFFSET


# ---------------------------------------------------------------------------
# Painel
# ---------------------------------------------------------------------------


def plot_treatment_boxplot(
    ax: Axes,
    data: pd.DataFrame,
    column: str,
    *,
    paired: PairedTestResult,
    rank_sum: RankSumResult,
    aggregate: str,
    label: str,
    log_scale: bool = False,
    integer_axis: bool = False,
) -> None:
    """`aggregate` ("median" ou "mean") é o valor por participante usado no teste pareado."""
    values = {t: treatment_values(data, column, t) for t in TREATMENT_ORDER}

    boxes = ax.boxplot(
        [values[t] for t in TREATMENT_ORDER],
        positions=POSITIONS,
        widths=BOX_W,
        showfliers=False,
        patch_artist=True,
        medianprops={"color": INK, "linewidth": 2},
        whiskerprops={"color": MUTED},
        capprops={"color": MUTED},
    )
    for patch, treatment in zip(boxes["boxes"], TREATMENT_ORDER):
        patch.set_facecolor(TREATMENT_COLOR[treatment])
        patch.set_alpha(0.28)
        patch.set_edgecolor(TREATMENT_COLOR[treatment])
        patch.set_linewidth(1.5)

    # Linhas de pareamento: o mesmo agregado por participante usado no teste.
    by_participant = (
        data.groupby(["participant", "treatment"])[column].agg(aggregate).unstack("treatment")
    )
    for participant in _participants_present(data):
        offset = _participant_offset(participant)
        ax.plot(
            [POSITIONS[0] + offset, POSITIONS[1] + offset],
            [by_participant.loc[participant, t.value] for t in TREATMENT_ORDER],
            color=MUTED,
            linewidth=1,
            alpha=0.55,
            zorder=2,
        )

    # Pontos: deslocamento fixo por participante e, dentro dele, por kata.
    for position, treatment in zip(POSITIONS, TREATMENT_ORDER):
        for participant in _participants_present(data):
            own = data[
                (data["participant"] == participant) & (data["treatment"] == treatment.value)
            ].sort_values("kata_id")
            for index, (value, censored) in enumerate(zip(own[column], own["censored"])):
                x = (
                    position
                    + _participant_offset(participant)
                    + (index - (len(own) - 1) / 2) * K_OFFSET
                )
                ax.scatter(
                    x,
                    value,
                    marker=PARTICIPANT_MARKERS[participant],
                    s=30,
                    facecolors="none" if censored else INK,
                    edgecolors=INK,
                    linewidths=1,
                    zorder=3,
                )

    medians = data.groupby("treatment")[column].median()
    for position, treatment in zip(POSITIONS, TREATMENT_ORDER):
        median = medians[treatment.value]
        left = treatment == TREATMENT_ORDER[0]
        ax.annotate(
            _num(median),
            xy=(position - BOX_W / 2 if left else position + BOX_W / 2, median),
            xytext=(-4 if left else 4, 0),
            textcoords="offset points",
            ha="right" if left else "left",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=INK,
            bbox={"fc": "white", "ec": "none", "alpha": 0.8, "pad": 1},
        )

    if log_scale:
        non_positive = [v for vs in values.values() for v in vs if v <= 0]
        if non_positive:
            # A escala log descartaria esses pontos sem aviso.
            raise ValueError(f"{column}: valores não positivos em escala log: {non_positive}")
        ax.set_yscale("log")
    else:
        all_values = values[Treatment.WITH_AI] + values[Treatment.WITHOUT_AI]
        if min(all_values) == max(all_values):
            # Sem variação: a escala automática colapsaria num intervalo ínfimo.
            # Todas as métricas são não negativas, então o eixo parte de zero.
            top = max(all_values[0], 1.0) * 1.05
            ax.set_ylim(-0.05 * top, top)
        if integer_axis:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        # Vírgula decimal, como nas anotações e no relatório da #15.
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))

    ax.set_xticks(POSITIONS, labels=[TREATMENT_LABEL[t] for t in TREATMENT_ORDER])
    ax.set_xlim(*X_LIMITS)
    ax.set_title(label, fontsize=10.5, loc="left", color=INK)
    ax.set_xlabel(stats_text(paired, rank_sum), fontsize=8.5, color=MUTED, labelpad=6)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelcolor=INK)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(MUTED)


def _add_legend(fig: Figure, data: pd.DataFrame) -> None:
    handles = [
        Line2D(
            [], [], marker=PARTICIPANT_MARKERS[p], linestyle="none",
            markerfacecolor=INK, markeredgecolor=INK, markersize=6, label=p,
        )
        for p in _participants_present(data)
    ]
    if data["censored"].any():
        handles.append(
            Line2D(
                [], [], marker="o", linestyle="none", markerfacecolor="none",
                markeredgecolor=INK, markersize=6, label=CENSORED_LABEL,
            )
        )
    fig.legend(handles=handles, loc="outside right upper", frameon=False, fontsize=9)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------


def build_rq1_figure(
    data: pd.DataFrame, rq1_test: PairedTestResult, rank_sum: RankSumResult
) -> Figure:
    fig, ax = plt.subplots(figsize=(6, 4.5), layout="constrained")
    column, label = RQ1_PANEL
    plot_treatment_boxplot(
        ax, data, column, paired=rq1_test, rank_sum=rank_sum,
        aggregate="median", label=label, log_scale=True,
    )
    ax.axhline(TIME_BOX_SECONDS, color=MUTED, linestyle="--", linewidth=1, zorder=1)
    ax.text(
        X_LIMITS[0] + 0.05, TIME_BOX_SECONDS, f"time-box ({_num(TIME_BOX_SECONDS, 0)} s)",
        va="bottom", ha="left", fontsize=8, color=MUTED,
    )
    ax.set_ylim(top=TIME_BOX_SECONDS * RQ1_TOP_MARGIN)
    fig.suptitle("RQ1 — Tempo até todos os testes passarem", x=0.02, ha="left", fontsize=12)
    _add_legend(fig, data)
    return fig


def build_rq2_figure(
    data: pd.DataFrame,
    rq2_tests: dict[str, PairedTestResult],
    rank_sums_by_label: dict[str, RankSumResult],
) -> Figure:
    fig, axes = plt.subplots(1, len(RQ2_PANELS), figsize=(10, 4.5), layout="constrained")
    for ax, (column, label) in zip(axes, RQ2_PANELS):
        # Média por participante, como no teste da #15: com a mediana, um único
        # trial com falhas entre os 3 de um tratamento sumiria do par.
        plot_treatment_boxplot(
            ax, data, column, paired=rq2_tests[label], rank_sum=rank_sums_by_label[label],
            aggregate="mean", label=label, integer_axis=column == "tests_failing",
        )
    fig.suptitle("RQ2 — Testes de aceitação ao final do trial", x=0.02, ha="left", fontsize=12)
    # O trial termina no green, então a métrica só varia em trial censurado:
    # 100% / 0 falhas não é evidência de ausência de defeitos.
    fig.supxlabel(
        "O trial encerra quando todos os testes passam: sem censura, a métrica não tem como "
        "variar (efeito de teto). Não indica ausência de defeitos.",
        fontsize=9, color=MUTED,
    )
    _add_legend(fig, data)
    return fig


def build_rq3_figure(
    data: pd.DataFrame,
    rq3_tests: dict[str, PairedTestResult],
    rank_sums_by_label: dict[str, RankSumResult],
) -> Figure:
    fig, axes = plt.subplots(1, len(RQ3_PANELS), figsize=(14, 4.5), layout="constrained")
    for ax, (column, label) in zip(axes, RQ3_PANELS):
        plot_treatment_boxplot(
            ax, data, column, paired=rq3_tests[label],
            rank_sum=rank_sums_by_label[label], aggregate="median", label=label,
        )
    fig.suptitle("RQ3 — Estrutura do código produzido", x=0.02, ha="left", fontsize=12)
    _add_legend(fig, data)
    return fig


def save_figure(fig: Figure, out_dir: Path, name: str, dpi: int = 300) -> list[Path]:
    """Salva PNG (para o Markdown) e PDF (vetorial), com metadados fixos, e fecha a figura."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{name}.png"
    pdf = out_dir / f"{name}.pdf"
    fig.savefig(png, dpi=dpi, bbox_inches="tight", facecolor="white", metadata={"Software": None})
    fig.savefig(pdf, bbox_inches="tight", facecolor="white", metadata={"CreationDate": None})
    plt.close(fig)
    return [png, pdf]
