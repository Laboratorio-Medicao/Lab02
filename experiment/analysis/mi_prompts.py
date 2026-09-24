"""Bônus da S03 (Issue #18): o MI em profundidade e nº de prompts × qualidade do código.

Análise **exploratória e descritiva**. Nenhum teste de hipótese novo é feito:
os testes de MI entre tratamentos já estão na análise da RQ3 (#16), com correção
de multiplicidade, e acrescentar testes aqui só inflaria a família sem pergunta
confirmatória nova.

1. **MI em profundidade.** O Radon calcula
   ``MI = max(0, (171 − 5,2·ln V − 0,23·G − 16,2·ln L + 50·sen(√(2,4·C))) · 100/171)``,
   com V = volume de Halstead, G = complexidade ciclomática, L = linhas lógicas
   (LLOC) e C = % de linhas de comentário. Os componentes são recalculados do
   `solution.py` versionado — a mesma convenção do MI harmonizado da #16 — e o
   MI reconstruído a partir deles é conferido contra essa série.
2. **Nº de prompts × qualidade.** Nos 9 trials com IA, cruza `n_prompts`
   (`data/prompts/prompt_records.csv`) com CC, MI e LOC. O MI usado aqui é o
   harmonizado: a comparação é **entre participantes**, e o MI como coletado não
   é comparável entre participantes (ver `results/rq3/data_quality_report.md`).

Os CSVs de `data/` são abertos somente para leitura.

Uso: ``python -m experiment.analysis.mi_prompts``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from radon.metrics import mi_compute, mi_parameters
from radon.raw import analyze

from experiment.analysis.metrics import CYCLOMATIC_COMPLEXITY, LOC, Metric
from experiment.analysis.rq3 import HARMONIZED_MI, HARMONIZED_MI_KEY, compute_descriptive
from experiment.analysis.rq3 import analyse as analyse_rq3
from experiment.analysis.rq3_data import PROJECT_ROOT, TRIAL_KEY, WITH_AI, _non_test_python_files
from experiment.collection.prompt_registry import PromptRegistry

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "mi_prompts"
PROMPTS_CSV = PROJECT_ROOT / "data" / "prompts" / "prompt_records.csv"
#: Tolerância para conferir o MI reconstruído contra a série harmonizada (2 casas).
MI_TOLERANCE = 0.01

HALSTEAD_VOLUME = Metric(
    key="halstead_volume", label="Volume de Halstead (V)", unit="bits",
    higher_is_better=False, question="Quanto vocabulário e quantos operandos o código usa?",
)
LLOC = Metric(
    key="lloc", label="LLOC (L)", unit="linhas lógicas",
    higher_is_better=False, question="Quantas instruções lógicas o código tem?",
)
COMMENTS = Metric(
    key="comments_percent", label="Comentários (C)", unit="% de linhas",
    higher_is_better=True, question="Quanto do código é comentário?",
)
CC_TOTAL = Metric(
    key="cc_total", label="CC (G)", unit="adimensional",
    higher_is_better=False, question="Qual a complexidade ciclomática do arquivo?",
)
COMPONENT_METRICS = (HARMONIZED_MI, HALSTEAD_VOLUME, LLOC, CC_TOTAL, COMMENTS)
#: Métricas de qualidade cruzadas com o nº de prompts (MI harmonizado: ver docstring).
QUALITY_METRICS = (CYCLOMATIC_COMPLEXITY, HARMONIZED_MI, LOC)


@dataclass
class MiPromptsResults:
    components: pd.DataFrame
    component_descriptive: pd.DataFrame
    component_correlations: pd.DataFrame
    prompts_quality: pd.DataFrame
    prompts_by_participant: pd.DataFrame
    prompt_correlations: pd.DataFrame
    checks: list[tuple[str, bool, str]]


# ---------------------------------------------------------------------------
# 1. MI em profundidade
# ---------------------------------------------------------------------------


def _solution_source(trial_path: Path) -> str:
    """O único arquivo com código do trial (os `__init__.py` vazios ficam de fora)."""
    files = [
        f for f in _non_test_python_files(PROJECT_ROOT / trial_path)
        if analyze(f.read_text(encoding="utf-8")).sloc > 0
    ]
    if len(files) != 1:
        raise ValueError(f"{trial_path}: esperado 1 arquivo com código, encontrados {len(files)}")
    return files[0].read_text(encoding="utf-8")


def compute_mi_components(observations: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, trial in observations.iterrows():
        volume, complexity, lloc, comments = mi_parameters(
            _solution_source(Path(trial["path"])), count_multi=True
        )
        rows.append(
            {
                **{key: trial[key] for key in TRIAL_KEY},
                HALSTEAD_VOLUME.key: volume,
                CC_TOTAL.key: complexity,
                LLOC.key: lloc,
                COMMENTS.key: comments,
                "mi_from_components": mi_compute(volume, complexity, lloc, comments),
                HARMONIZED_MI_KEY: trial[HARMONIZED_MI_KEY],
                LOC.key: trial[LOC.key],
            }
        )
    return pd.DataFrame(rows)


def spearman_table(data: pd.DataFrame, target: Metric, others: tuple[Metric, ...]) -> pd.DataFrame:
    """ρ de Spearman descritivo; métricas constantes ficam sem ρ (correlação indefinida)."""
    rows = []
    for metric in others:
        constant = data[metric.key].nunique() == 1
        rho = None if constant else data[target.key].corr(data[metric.key], method="spearman")
        rows.append(
            {
                "target": target.label,
                "metric": metric.label,
                "metric_key": metric.key,
                "n": len(data),
                "spearman_rho": rho,
                "note": "métrica constante — correlação indefinida" if constant else "",
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Nº de prompts × qualidade
# ---------------------------------------------------------------------------


def load_prompts(path: Path = PROMPTS_CSV) -> pd.DataFrame:
    records = PromptRegistry(path).load_all()
    return pd.DataFrame(
        [
            {
                "participant": r.participant,
                "kata_id": r.kata_id,
                "treatment": r.treatment.value,
                "n_prompts": r.n_prompts,
                "productivity_perception": r.productivity_perception,
            }
            for r in records
        ]
    )


def join_prompts(observations: pd.DataFrame, prompts: pd.DataFrame) -> pd.DataFrame:
    with_ai = observations[observations["treatment"] == WITH_AI]
    return with_ai.merge(prompts, on=list(TRIAL_KEY), how="left")[
        [*TRIAL_KEY, "n_prompts", "productivity_perception",
         CYCLOMATIC_COMPLEXITY.key, HARMONIZED_MI_KEY, LOC.key]
    ].sort_values(["participant", "kata_id"], ignore_index=True)


def prompts_by_participant(joined: pd.DataFrame) -> pd.DataFrame:
    grouped = joined.groupby("participant")
    return pd.DataFrame(
        {
            "trials": grouped.size(),
            "n_prompts_values": grouped["n_prompts"].agg(lambda s: sorted(s.unique().tolist())),
            **{f"median_{m.key}": grouped[m.key].median() for m in QUALITY_METRICS},
        }
    ).reset_index()


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def analyse() -> MiPromptsResults:
    observations = analyse_rq3().observations
    checks: list[tuple[str, bool, str]] = []

    components = compute_mi_components(observations)
    divergence = (components["mi_from_components"] - components[HARMONIZED_MI_KEY]).abs()
    checks.append(
        (
            "MI reconstruído dos componentes = MI harmonizado (#16)",
            bool((divergence <= MI_TOLERANCE).all()),
            f"{int((divergence <= MI_TOLERANCE).sum())}/{len(components)} trials; "
            f"maior diferença {divergence.max():.4f}".replace(".", ","),
        )
    )

    prompts = load_prompts()
    joined = join_prompts(observations, prompts)
    covered = int(joined["n_prompts"].notna().sum())
    checks.append(
        (
            "Nº de prompts registrado para os trials com IA",
            covered == len(joined),
            f"{covered}/{len(joined)} trials com IA têm `n_prompts`",
        )
    )
    joined = joined.dropna(subset=["n_prompts"])
    within = joined.groupby("participant")["n_prompts"].nunique()
    checks.append(
        (
            "Nº de prompts varia dentro de algum participante",
            bool((within > 1).any()),
            "nº de valores distintos de `n_prompts` por participante: "
            + ", ".join(f"{p} {n}" for p, n in within.items())
            + " — sem variação interna, o nº de prompts se confunde com o participante",
        )
    )

    return MiPromptsResults(
        components=components,
        component_descriptive=compute_descriptive(components, COMPONENT_METRICS),
        component_correlations=spearman_table(
            components, HARMONIZED_MI, (HALSTEAD_VOLUME, LLOC, CC_TOTAL, COMMENTS)
        ),
        prompts_quality=joined,
        prompts_by_participant=prompts_by_participant(joined),
        prompt_correlations=spearman_table(
            joined.assign(n_prompts=joined["n_prompts"].astype(float)),
            Metric("n_prompts", "Nº de prompts", "prompts", False, ""),
            QUALITY_METRICS,
        ),
        checks=checks,
    )


def write_outputs(results: MiPromptsResults, output_dir: Path) -> None:
    from experiment.analysis.mi_prompts_report import generate_markdown

    output_dir.mkdir(parents=True, exist_ok=True)
    results.components.to_csv(output_dir / "mi_components.csv", index=False)
    results.component_descriptive.to_csv(output_dir / "mi_components_descriptive.csv", index=False)
    results.component_correlations.to_csv(output_dir / "mi_component_correlations.csv", index=False)
    results.prompts_quality.to_csv(output_dir / "prompts_quality.csv", index=False)
    results.prompt_correlations.to_csv(output_dir / "prompt_correlations.csv", index=False)
    (output_dir / "mi_prompts_summary.md").write_text(generate_markdown(results), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    results = analyse()
    for name, passed, detail in results.checks:
        print(f"  [{'OK   ' if passed else 'ATENÇÃO'}] {name}: {detail}")
    write_outputs(results, args.output_dir)
    print(f"\nArtefatos em {args.output_dir}")


if __name__ == "__main__":
    main()
