"""Análise da RQ3 — métricas estáticas (Issue #16).

RQ3 (formulação oficial em `docs/enunciado/lab02.md`, linha 25):
*"O uso de assistente de IA altera a complexidade ciclomática ou a duplicação
do código produzido?"*

Pipeline completo e reprodutível:

    python -m experiment.analysis.rq3

Lê `data/trials.csv` e `data/static_metrics.csv` (somente leitura), valida,
consolida por trial, calcula mediana/IQR, aplica Wilcoxon pareado com correção
de multiplicidade, gera as figuras e escreve tudo em `results/rq3/`.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from experiment.analysis import rq3_report
from experiment.analysis.metrics import (
    CC_PER_LOC,
    CYCLOMATIC_COMPLEXITY,
    DUPLICATION,
    DUPLICATION_PER_LOC,
    LOC,
    MAINTAINABILITY_INDEX,
    NORMALIZED_METRICS,
    PRIMARY_METRICS,
    Metric,
)
from experiment.analysis.rq3_data import (
    PROJECT_ROOT,
    TREATMENTS,
    WITH_AI,
    WITHOUT_AI,
    DataQualityReport,
    compute_task_allocation_balance,
    load_observations,
)
from experiment.analysis.statistics import (
    ALPHA,
    BENJAMINI_HOCHBERG,
    BONFERRONI,
    WilcoxonResult,
    adjust_p_values,
    build_pairs,
    decision,
    describe_by_group,
    paired_wilcoxon,
)
from experiment.visualization.rq3_figures import generate_figures

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "rq3"
FIGURES_SUBDIR = "figures"

#: MI recomputado sob convenção única, usado só na análise de sensibilidade.
HARMONIZED_MI_KEY = "maintainability_index_harmonized"
HARMONIZED_MI = Metric(
    key=HARMONIZED_MI_KEY,
    label="MI (harmonizado)",
    unit="0–100",
    higher_is_better=True,
    question="A conclusão sobre manutenibilidade muda sob uma convenção única de coleta?",
    inline_unit="pontos de MI",
)


@dataclass(frozen=True)
class PairingUnit:
    """Fator de bloco que define os pares do Wilcoxon."""

    column: str
    label: str
    rationale: str


#: Unidade primária. Não existe par participante×kata, então o participante é
#: o único bloco within-subject disponível.
PARTICIPANT_PAIRING = PairingUnit(
    column="participant",
    label="participante (within-subject)",
    rationale=(
        "Unidade coerente com o desenho crossover within-subject: cada participante "
        "contribui com 3 trials com IA e 3 sem IA, e o par é a mediana de cada metade. "
        "Neutraliza diferenças individuais de estilo — e também a divergência de "
        "convenção de coleta do MI, que é constante dentro de cada participante."
    ),
)

#: Unidade secundária: o kata é o principal determinante do tamanho e da
#: complexidade exigidos pela tarefa.
KATA_PAIRING = PairingUnit(
    column="kata_id",
    label="kata (bloco de dificuldade)",
    rationale=(
        "Análise secundária. Bloqueia pela dificuldade da tarefa, que é o principal "
        "determinante de LOC e CC, e dispõe de 6 blocos em vez de 3. Não é um par "
        "within-subject: os dois lados de cada par vêm de participantes diferentes, "
        "e as células são desbalanceadas (1 ou 2 trials por lado)."
    ),
)


#: A família de inferências é a unidade de pareamento: corrigir também entre
#: elas penalizaria duas vezes a mesma pergunta sob bloqueios alternativos.
MULTIPLICITY_FAMILY_COLUMN = "pairing_unit"


@dataclass
class Rq3Results:
    observations: pd.DataFrame
    quality: DataQualityReport
    descriptive: pd.DataFrame
    tests: pd.DataFrame
    normalized: pd.DataFrame
    allocation_balance: pd.DataFrame
    pairs_by_metric: dict[str, pd.DataFrame]
    figures: list[Path]


def _add_harmonized_mi(observations: pd.DataFrame, quality: DataQualityReport) -> pd.DataFrame:
    """Anexa o MI recomputado sob convenção única."""
    harmonized = quality.integrity[
        ["participant", "kata_id", "treatment", "mi_source_only"]
    ].rename(columns={"mi_source_only": HARMONIZED_MI_KEY})
    return observations.merge(harmonized, on=["participant", "kata_id", "treatment"])


def compute_descriptive(observations: pd.DataFrame, metrics: tuple[Metric, ...]) -> pd.DataFrame:
    rows = []
    for metric in metrics:
        summary = describe_by_group(observations, metric.key, "treatment", TREATMENTS)
        summary.insert(0, "metric", metric.label)
        summary.insert(1, "metric_key", metric.key)
        summary.insert(2, "unit", metric.unit)
        rows.append(summary)
    return pd.concat(rows, ignore_index=True)


def _test_row(result: WilcoxonResult, metric: Metric, observations: pd.DataFrame) -> dict:
    with_ai = observations.loc[observations["treatment"] == WITH_AI, metric.key]
    without_ai = observations.loc[observations["treatment"] == WITHOUT_AI, metric.key]
    return {
        "metric": metric.label,
        "metric_key": metric.key,
        "unit": metric.unit,
        "pairing_unit": result.pairing_unit,
        "test": "Wilcoxon signed-rank (bicaudal)",
        "h0": f"a mediana de {metric.label} é igual nos dois tratamentos",
        "h1": f"a mediana de {metric.label} difere entre os tratamentos",
        "median_without_ai": without_ai.median(),
        "median_with_ai": with_ai.median(),
        "median_difference_pairs": result.median_difference,
        "n_pairs": result.n_pairs,
        "n_nonzero_pairs": result.n_nonzero_pairs,
        "statistic_w": result.statistic,
        "p_value": result.p_value,
        "p_method": result.method,
        "min_achievable_p": result.min_achievable_p,
        "effect_rank_biserial": result.rank_biserial,
        "effect_hodges_lehmann": result.hodges_lehmann,
        "alpha": ALPHA,
        "decision": decision(result),
        "degenerate": result.degenerate,
        "note": result.note,
    }


def run_tests(
    observations: pd.DataFrame,
    metrics: tuple[Metric, ...],
    pairing_units: tuple[PairingUnit, ...],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Roda o Wilcoxon de cada métrica em cada unidade de pareamento."""
    rows: list[dict] = []
    pairs_by_metric: dict[str, pd.DataFrame] = {}

    for pairing in pairing_units:
        for metric in metrics:
            pairs = build_pairs(
                observations,
                value_column=metric.key,
                pairing_column=pairing.column,
                treatment_column="treatment",
                treatments=(WITHOUT_AI, WITH_AI),
            )
            if pairing is PARTICIPANT_PAIRING:
                pairs_by_metric[metric.key] = pairs
            result = paired_wilcoxon(
                pairs, metric=metric.label, pairing_unit=pairing.label,
                treatments=(WITHOUT_AI, WITH_AI),
            )
            rows.append(_test_row(result, metric, observations))

    return _add_multiplicity_correction(pd.DataFrame(rows)), pairs_by_metric


def _add_multiplicity_correction(tests: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta p-valores ajustados sem substituir os brutos.

    O bruto é a saída direta do teste; o ajustado é o que sustenta a decisão
    sobre H0 quando vários testes são reportados juntos.
    """
    tests = tests.copy()
    tests["family"] = tests[MULTIPLICITY_FAMILY_COLUMN]
    tests["family_size"] = tests.groupby("family")["p_value"].transform(
        lambda p_values: p_values.notna().sum()
    )
    for column, method in (("p_bonferroni", BONFERRONI), ("p_fdr_bh", BENJAMINI_HOCHBERG)):
        tests[column] = (
            tests.groupby("family", group_keys=False)["p_value"]
            .apply(lambda p_values: adjust_p_values(p_values, method))
            .reindex(tests.index)
        )
    tests["decision_bonferroni"] = [
        "teste não aplicável"
        if pd.isna(adjusted)
        else f"rejeita H0 (α = {ALPHA}, corrigido)"
        if adjusted < ALPHA
        else f"não rejeita H0 (α = {ALPHA}, corrigido)"
        for adjusted in tests["p_bonferroni"]
    ]
    return tests


def analyse() -> Rq3Results:
    observations, quality = load_observations()
    observations = _add_harmonized_mi(observations, quality)

    analysed_metrics = PRIMARY_METRICS + (HARMONIZED_MI,)
    descriptive = compute_descriptive(observations, analysed_metrics + NORMALIZED_METRICS)
    tests, pairs_by_metric = run_tests(
        observations,
        metrics=analysed_metrics + NORMALIZED_METRICS,
        pairing_units=(PARTICIPANT_PAIRING, KATA_PAIRING),
    )
    normalized = compute_descriptive(observations, NORMALIZED_METRICS)

    return Rq3Results(
        observations=observations,
        quality=quality,
        descriptive=descriptive,
        tests=tests,
        normalized=normalized,
        allocation_balance=compute_task_allocation_balance(observations),
        pairs_by_metric=pairs_by_metric,
        figures=[],
    )


def write_outputs(results: Rq3Results, output_dir: Path) -> Rq3Results:
    output_dir.mkdir(parents=True, exist_ok=True)

    results.observations.to_csv(output_dir / "consolidated_trials.csv", index=False)
    results.descriptive.to_csv(output_dir / "descriptive_statistics.csv", index=False)
    results.tests.to_csv(output_dir / "statistical_tests.csv", index=False)
    results.normalized.to_csv(output_dir / "normalized_metrics.csv", index=False)
    results.allocation_balance.to_csv(
        output_dir / "task_allocation_balance.csv", index=False
    )
    results.quality.integrity.to_csv(output_dir / "source_integrity_check.csv", index=False)
    results.quality.outliers.to_csv(output_dir / "outliers.csv", index=False)

    results.figures = generate_figures(
        results.observations, output_dir / FIGURES_SUBDIR
    )

    (output_dir / "data_quality_report.md").write_text(
        rq3_report.render_data_quality(results), encoding="utf-8"
    )
    (output_dir / "rq3_summary.md").write_text(
        rq3_report.render_summary(results, FIGURES_SUBDIR), encoding="utf-8"
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help=f"diretório dos artefatos (padrão: {DEFAULT_OUTPUT_DIR.relative_to(PROJECT_ROOT)})",
    )
    arguments = parser.parse_args()

    results = write_outputs(analyse(), arguments.output_dir)

    print(f"Trials analisados: {len(results.observations)}")
    for name, passed, detail in results.quality.checks:
        print(f"  [{'OK   ' if passed else 'ATENÇÃO'}] {name}: {detail}")
    print(f"\nArtefatos em {arguments.output_dir}")
    for path in sorted(arguments.output_dir.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(arguments.output_dir)}")


if __name__ == "__main__":
    main()
