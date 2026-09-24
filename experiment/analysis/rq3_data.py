"""Carga, validação e consolidação dos dados de RQ3.

Junta `data/trials.csv` e `data/static_metrics.csv` no nível de trial, sem
agregar, e roda as verificações de qualidade antes de qualquer estatística —
incluindo a conferência dos valores do CSV contra uma recomputação a partir do
código-fonte dos trials.

Os CSVs de `data/` são abertos somente para leitura: divergências são
reportadas, nunca corrigidas em silêncio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

from experiment.analysis.metrics import (
    NORMALIZATION_NUMERATORS,
    NORMALIZED_METRICS,
    PRIMARY_METRICS,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRIALS_CSV = PROJECT_ROOT / "data" / "trials.csv"
STATIC_METRICS_CSV = PROJECT_ROOT / "data" / "static_metrics.csv"

TRIAL_KEY = ("participant", "kata_id", "treatment")

WITH_AI = "with_ai"
WITHOUT_AI = "without_ai"
TREATMENTS = (WITHOUT_AI, WITH_AI)

#: Desenho fechado na S01 (`docs/experiment_design.md`).
EXPECTED_PARTICIPANTS = ("Guilherme", "Marcos", "Arthur")
EXPECTED_KATAS = tuple(f"kata-0{index}" for index in range(1, 7))
EXPECTED_TRIALS = len(EXPECTED_PARTICIPANTS) * len(EXPECTED_KATAS)
EXPECTED_TRIALS_PER_TREATMENT = len(EXPECTED_KATAS) // 2

#: Faixas possíveis de cada métrica, só para detectar dados corrompidos.
METRIC_BOUNDS = {
    "loc": (1, None),
    "cyclomatic_complexity_avg": (1.0, None),
    "maintainability_index": (0.0, 100.0),
    "duplicated_lines_percent": (0.0, 100.0),
    "duplicated_lines": (0, None),
}

#: Critério de Tukey para sinalizar — não remover — observações extremas.
OUTLIER_IQR_FACTOR = 1.5

#: O coletor grava as métricas arredondadas em 2 casas.
RECOMPUTE_TOLERANCE = 0.01


@dataclass
class DataQualityReport:
    """Achados das verificações de qualidade. Nenhum dado é removido."""

    checks: list[tuple[str, bool, str]] = field(default_factory=list)
    excluded_trials: list[str] = field(default_factory=list)
    outliers: pd.DataFrame | None = None
    integrity: pd.DataFrame | None = None

    def record(self, name: str, passed: bool, detail: str) -> None:
        self.checks.append((name, passed, detail))

    @property
    def failures(self) -> list[tuple[str, bool, str]]:
        return [check for check in self.checks if not check[1]]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"arquivo de dados não encontrado: {path}")
    return pd.read_csv(path)


def _non_test_python_files(directory: Path) -> list[Path]:
    """Mesma seleção de arquivos do coletor da S02."""
    return sorted(
        file
        for file in directory.rglob("*.py")
        if not (file.name.startswith("test_") or file.name.endswith("_test.py"))
    )


def recompute_from_source(trial_path: Path) -> dict[str, float]:
    """Recalcula LOC, CC e MI a partir do código do trial, via Radon.

    São duas leituras de MI porque o coletor tira a média do MI por arquivo:
    `mi_all_files` inclui os `__init__.py` vazios (que pontuam MI = 100) e
    `mi_source_only` considera só os arquivos com código. A diferença entre as
    duas identifica quais linhas do CSV o coletor atual não reproduz.
    """
    files = _non_test_python_files(trial_path)
    if not files:
        raise ValueError(f"nenhum arquivo .py encontrado em {trial_path}")

    total_loc = 0
    total_sloc = 0
    empty_files = 0
    blocks = []
    mi_all: list[float] = []
    mi_source: list[float] = []

    for file in files:
        source = file.read_text(encoding="utf-8")
        raw = analyze(source)
        total_loc += raw.loc
        total_sloc += raw.sloc
        blocks.extend(cc_visit(source))
        mi_all.append(mi_visit(source, multi=True))
        if raw.sloc > 0:
            mi_source.append(mi_visit(source, multi=True))
        else:
            empty_files += 1

    return {
        "loc": total_loc,
        "sloc": total_sloc,
        "cyclomatic_complexity_avg": (
            sum(block.complexity for block in blocks) / len(blocks) if blocks else 0.0
        ),
        "cc_blocks": len(blocks),
        "mi_all_files": sum(mi_all) / len(mi_all) if mi_all else 0.0,
        "mi_source_only": sum(mi_source) / len(mi_source) if mi_source else 0.0,
        "empty_files": empty_files,
    }


def load_observations() -> tuple[pd.DataFrame, DataQualityReport]:
    """Devolve uma linha por trial, com as razões por LOC já calculadas.

    A junção usa a chave completa do trial para que um tratamento divergente
    entre os dois CSVs apareça como linha sem correspondência.
    """
    trials = _read_csv(TRIALS_CSV)
    static = _read_csv(STATIC_METRICS_CSV)
    report = DataQualityReport()

    observations = trials.merge(
        static, on=list(TRIAL_KEY), how="outer", indicator=True, validate="one_to_one"
    )
    _check_join(observations, trials, static, report)
    observations = observations.drop(columns="_merge")

    _check_design_coverage(observations, report)
    _check_missing_values(observations, report)
    _check_value_bounds(observations, report)
    _check_constant_metrics(observations, report)

    observations = _add_normalized_metrics(observations)
    report.integrity = check_integrity_against_source(observations, report)
    report.outliers = _flag_outliers(observations)

    return observations, report


def _check_join(
    observations: pd.DataFrame,
    trials: pd.DataFrame,
    static: pd.DataFrame,
    report: DataQualityReport,
) -> None:
    for name, frame in (("trials.csv", trials), ("static_metrics.csv", static)):
        duplicated = frame.duplicated(subset=list(TRIAL_KEY)).sum()
        report.record(
            f"Chaves únicas em {name}",
            duplicated == 0,
            f"{len(frame)} linhas, {duplicated} chave(s) duplicada(s)",
        )

    unmatched = observations.loc[observations["_merge"] != "both"]
    for _, row in unmatched.iterrows():
        origin = "só em trials.csv" if row["_merge"] == "left_only" else "só em static_metrics.csv"
        report.excluded_trials.append(
            f"{row['participant']}/{row['kata_id']}/{row['treatment']} ({origin})"
        )
    report.record(
        "Junção trials.csv × static_metrics.csv",
        unmatched.empty,
        f"{len(observations) - len(unmatched)} trial(is) com as duas fontes; "
        f"{len(unmatched)} sem correspondência",
    )


def _check_design_coverage(observations: pd.DataFrame, report: DataQualityReport) -> None:
    report.record(
        "Total de trials",
        len(observations) == EXPECTED_TRIALS,
        f"esperados {EXPECTED_TRIALS}, encontrados {len(observations)}",
    )

    unexpected = sorted(set(observations["treatment"]) - set(TREATMENTS))
    report.record(
        "Tratamentos válidos",
        not unexpected,
        f"valores fora de {TREATMENTS}: {unexpected or 'nenhum'}",
    )

    counts = observations.pivot_table(
        index="participant", columns="treatment", values="kata_id", aggfunc="count"
    ).reindex(columns=list(TREATMENTS)).fillna(0)
    balanced = bool((counts == EXPECTED_TRIALS_PER_TREATMENT).all().all())
    report.record(
        "Balanceamento within-subject",
        balanced,
        "; ".join(
            f"{participant}: {int(row[WITHOUT_AI])} sem IA / {int(row[WITH_AI])} com IA"
            for participant, row in counts.iterrows()
        ),
    )

    repeated = (
        observations.groupby(["participant", "kata_id"])["treatment"].nunique().gt(1).sum()
    )
    report.record(
        "Repetição do mesmo kata sob os dois tratamentos",
        True,
        f"{repeated} par(es) participante×kata com os dois tratamentos — "
        "0 é o esperado neste desenho e determina a unidade de pareamento",
    )


def _check_missing_values(observations: pd.DataFrame, report: DataQualityReport) -> None:
    columns = [metric.key for metric in PRIMARY_METRICS]
    missing = observations[columns].isna().sum()
    report.record(
        "Valores ausentes nas métricas de RQ3",
        bool(missing.sum() == 0),
        "; ".join(f"{column}: {int(count)}" for column, count in missing.items()),
    )


def _check_value_bounds(observations: pd.DataFrame, report: DataQualityReport) -> None:
    violations: list[str] = []
    for column, (minimum, maximum) in METRIC_BOUNDS.items():
        if column not in observations:
            continue
        values = observations[column]
        below = values < minimum if minimum is not None else values.notna() & False
        above = values > maximum if maximum is not None else values.notna() & False
        count = int((below | above).sum())
        if count:
            violations.append(f"{column}: {count} fora de [{minimum}, {maximum}]")
    report.record(
        "Valores dentro das faixas possíveis",
        not violations,
        "; ".join(violations) if violations else "nenhum valor impossível ou negativo",
    )


def _check_constant_metrics(observations: pd.DataFrame, report: DataQualityReport) -> None:
    constant = [
        metric.label
        for metric in PRIMARY_METRICS
        if observations[metric.key].nunique(dropna=False) == 1
    ]
    report.record(
        "Métricas com variância",
        not constant,
        f"sem variância (valor único nos {len(observations)} trials): "
        f"{', '.join(constant) if constant else 'nenhuma'}",
    )


def _add_normalized_metrics(observations: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as razões por LOC no nível do trial, sem agregar."""
    observations = observations.copy()
    for metric in NORMALIZED_METRICS:
        numerator = NORMALIZATION_NUMERATORS[metric.key]
        observations[metric.key] = observations[numerator] / observations["loc"]
    return observations


def check_integrity_against_source(
    observations: pd.DataFrame, report: DataQualityReport
) -> pd.DataFrame:
    """Confere cada linha do CSV contra o código-fonte do próprio trial.

    Responde se os números publicados vêm mesmo do código versionado.
    """
    rows = []
    for _, observation in observations.iterrows():
        trial_path = PROJECT_ROOT / observation["path"]
        recomputed = recompute_from_source(trial_path)
        mi_csv = observation["maintainability_index"]
        # O que o coletor produziria hoje, com os arquivos que existem agora.
        reproducible_now = abs(mi_csv - recomputed["mi_all_files"]) <= RECOMPUTE_TOLERANCE
        matches_source_only = abs(mi_csv - recomputed["mi_source_only"]) <= RECOMPUTE_TOLERANCE
        rows.append(
            {
                "participant": observation["participant"],
                "kata_id": observation["kata_id"],
                "treatment": observation["treatment"],
                "loc_csv": observation["loc"],
                "loc_recomputed": recomputed["loc"],
                "sloc_recomputed": recomputed["sloc"],
                "loc_matches": abs(observation["loc"] - recomputed["loc"]) <= RECOMPUTE_TOLERANCE,
                "cc_csv": observation["cyclomatic_complexity_avg"],
                "cc_recomputed": round(recomputed["cyclomatic_complexity_avg"], 2),
                "cc_blocks": recomputed["cc_blocks"],
                "cc_matches": abs(
                    observation["cyclomatic_complexity_avg"]
                    - recomputed["cyclomatic_complexity_avg"]
                )
                <= RECOMPUTE_TOLERANCE,
                "mi_csv": mi_csv,
                "mi_collector_today": round(recomputed["mi_all_files"], 2),
                "mi_source_only": round(recomputed["mi_source_only"], 2),
                "mi_reproducible_now": reproducible_now,
                "mi_status": (
                    "reproduzível pelo coletor atual"
                    if reproducible_now
                    else "histórico — não reproduzível no estado atual"
                    if matches_source_only
                    else "origem não identificada"
                ),
                "empty_package_files": recomputed["empty_files"],
            }
        )

    integrity = pd.DataFrame(rows)

    report.record(
        "LOC reproduzido a partir do código-fonte",
        bool(integrity["loc_matches"].all()),
        f"{int(integrity['loc_matches'].sum())}/{len(integrity)} trials reproduzidos",
    )
    report.record(
        "CC reproduzida a partir do código-fonte",
        bool(integrity["cc_matches"].all()),
        f"{int(integrity['cc_matches'].sum())}/{len(integrity)} trials reproduzidos",
    )
    reproducible = int(integrity["mi_reproducible_now"].sum())
    historical = len(integrity) - reproducible
    report.record(
        "MI reproduzível pelo coletor no estado atual do repositório",
        historical == 0,
        f"{reproducible}/{len(integrity)} trials reproduzem o valor gravado; "
        f"{historical} são valores históricos que o coletor não reproduz hoje "
        f"(os diretórios de trial contêm hoje "
        f"{int(integrity['empty_package_files'].sum())} arquivo(s) .py vazio(s) de pacote, "
        "que entram na média por arquivo do MI)",
    )
    report.record(
        "Unidade de cálculo da CC uniforme entre os trials",
        integrity["cc_blocks"].nunique() == 1,
        f"blocos (funções/métodos) por trial: "
        f"{sorted(int(value) for value in integrity['cc_blocks'].unique())}",
    )
    return integrity


def compute_task_allocation_balance(
    observations: pd.DataFrame, proxy_metrics: tuple[str, ...] = ("cyclomatic_complexity_avg", "loc")
) -> pd.DataFrame:
    """Compara a dificuldade aparente dos katas dos dois lados de cada par.

    Como ninguém resolveu o mesmo kata nos dois tratamentos, cada lado do par
    contém katas diferentes. A dificuldade aparente de um kata é a média dos
    seus valores entre os três participantes.

    O proxy vem das próprias medições da análise, não de uma avaliação
    independente: serve para descrever a alocação, não para estimar um efeito
    de tarefa isolado.
    """
    rows = []
    difficulty = {
        metric: observations.groupby("kata_id")[metric].mean() for metric in proxy_metrics
    }
    for participant, trials in observations.groupby("participant"):
        row = {"participant": participant}
        for treatment in TREATMENTS:
            katas = sorted(trials.loc[trials["treatment"] == treatment, "kata_id"])
            row[f"katas_{treatment}"] = " ".join(katas)
            for metric in proxy_metrics:
                row[f"{metric}_{treatment}"] = round(
                    difficulty[metric].loc[katas].mean(), 4
                )
        for metric in proxy_metrics:
            row[f"{metric}_difference"] = round(
                row[f"{metric}_{WITH_AI}"] - row[f"{metric}_{WITHOUT_AI}"], 4
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _flag_outliers(observations: pd.DataFrame) -> pd.DataFrame:
    """Sinaliza observações extremas por tratamento, sem removê-las."""
    rows = []
    for metric in PRIMARY_METRICS + NORMALIZED_METRICS:
        for treatment in TREATMENTS:
            values = observations.loc[observations["treatment"] == treatment, metric.key]
            q1, q3 = values.quantile(0.25), values.quantile(0.75)
            span = OUTLIER_IQR_FACTOR * (q3 - q1)
            extreme = observations.loc[
                (observations["treatment"] == treatment)
                & ((observations[metric.key] < q1 - span) | (observations[metric.key] > q3 + span))
            ]
            for _, observation in extreme.iterrows():
                rows.append(
                    {
                        "metric": metric.label,
                        "treatment": treatment,
                        "participant": observation["participant"],
                        "kata_id": observation["kata_id"],
                        "value": observation[metric.key],
                        "lower_fence": round(q1 - span, 4),
                        "upper_fence": round(q3 + span, 4),
                        "decision": "mantido na análise",
                    }
                )
    return pd.DataFrame(rows, columns=[
        "metric", "treatment", "participant", "kata_id",
        "value", "lower_fence", "upper_fence", "decision",
    ])
