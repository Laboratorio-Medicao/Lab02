"""Coleta de métricas estáticas via Radon para RQ3.

Métricas: complexidade ciclomática média (`radon cc`), índice de
manutenibilidade (`radon mi`) e LOC — obrigatória como controle sempre que
complexidade for reportada. Preparado na S01 (Issue #5); a execução sobre o
código final de cada trial real é escopo da S02.

O MI (`radon mi`) é uma métrica opcional de aprofundamento (linha 55 do
enunciado) — o grupo decidiu deliberadamente sempre coletá-la junto de CC e
LOC (ver justificativa em `docs/experiment_design.md`), em vez de torná-la
condicional a uma flag, porque seu custo de cálculo é o mesmo de CC/LOC e ela
enriquece a análise de RQ3 sem exigir uma execução separada.
"""
from __future__ import annotations

import json
import csv
from dataclasses import dataclass
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

from experiment.collection.duplication_metrics import (
    DuplicationMetrics,
    collect_duplication_metrics,
)

TRIAL_METRICS_FIELDNAMES = [
    "participant",
    "kata_id",
    "treatment",
    "path",
    "loc",
    "cyclomatic_complexity_avg",
    "maintainability_index",
    "duplicated_lines",
    "duplicated_lines_percent",
    "duplicate_blocks",
    "total_lines",
    "tool",
    "tool_version",
]


@dataclass(frozen=True)
class StaticMetrics:
    path: str
    loc: int
    cyclomatic_complexity_avg: float
    maintainability_index: float
    duplication: DuplicationMetrics

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "loc": self.loc,
            "cyclomatic_complexity_avg": round(self.cyclomatic_complexity_avg, 2),
            "maintainability_index": round(self.maintainability_index, 2),
            **self.duplication.to_dict(),
        }


def _python_files(path: Path, include_tests: bool) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".py" else []

    candidates = sorted(path.rglob("*.py"))
    if include_tests:
        return candidates
    return [p for p in candidates if not (p.name.startswith("test_") or p.name.endswith("_test.py"))]


def collect_static_metrics(path: Path, include_tests: bool = False) -> StaticMetrics:
    """Coleta LOC, complexidade ciclomática média e índice de manutenibilidade.

    Por padrão, arquivos de teste (`test_*.py` / `*_test.py`) são excluídos,
    já que RQ3 avalia a estrutura do código produzido pelo participante, não
    dos testes de aceitação do kata.
    """
    files = _python_files(path, include_tests)
    if not files:
        raise ValueError(f"Nenhum arquivo .py encontrado em {path}")

    total_loc = 0
    all_blocks = []
    mi_values = []

    for file in files:
        source = file.read_text(encoding="utf-8")
        total_loc += analyze(source).loc
        all_blocks.extend(cc_visit(source))
        mi_values.append(mi_visit(source, multi=True))

    cc_avg = (
        sum(block.complexity for block in all_blocks) / len(all_blocks) if all_blocks else 0.0
    )
    mi_avg = sum(mi_values) / len(mi_values) if mi_values else 0.0

    return StaticMetrics(
        path=str(path),
        loc=total_loc,
        cyclomatic_complexity_avg=cc_avg,
        maintainability_index=mi_avg,
        duplication=collect_duplication_metrics(path, include_tests=include_tests),
    )


def append_trial_metrics(
    metrics: StaticMetrics,
    participant: str,
    kata_id: str,
    treatment: str,
    output: Path,
) -> None:
    """Acrescenta métricas estáticas identificadas por um trial ao CSV."""
    output.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "participant": participant,
        "kata_id": kata_id,
        "treatment": treatment,
        **metrics.to_dict(),
    }
    with output.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=TRIAL_METRICS_FIELDNAMES)
        if output.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(row)


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Coleta métricas estáticas (Radon cc/mi + LOC) de um kata."
    )
    parser.add_argument("path", type=Path, help="Arquivo ou diretório Python a analisar")
    parser.add_argument(
        "--include-tests", action="store_true", help="Inclui arquivos test_*.py na análise"
    )
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--participant", help="Participante do trial")
    parser.add_argument("--kata-id", help="Identificador do kata")
    parser.add_argument("--treatment", help="Tratamento do trial")
    parser.add_argument("--output", type=Path, help="CSV de métricas por trial")
    args = parser.parse_args()

    metadata = [args.participant, args.kata_id, args.treatment]
    if args.output and not all(metadata):
        parser.error("--output exige --participant, --kata-id e --treatment")
    if not args.output and any(metadata):
        parser.error("--participant, --kata-id e --treatment exigem --output")

    metrics = collect_static_metrics(args.path, include_tests=args.include_tests)

    if args.output:
        append_trial_metrics(
            metrics,
            participant=args.participant,
            kata_id=args.kata_id,
            treatment=args.treatment,
            output=args.output,
        )

    if args.json:
        print(json.dumps(metrics.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Path: {metrics.path}")
        print(f"LOC: {metrics.loc}")
        print(f"Complexidade ciclomática média (CC): {metrics.cyclomatic_complexity_avg:.2f}")
        print(f"Índice de Manutenibilidade (MI): {metrics.maintainability_index:.2f}")
        print(f"Linhas duplicadas: {metrics.duplication.duplicated_lines}")
        print(
            "Percentual de linhas duplicadas: "
            f"{metrics.duplication.duplicated_lines_percent:.2f}%"
        )


if __name__ == "__main__":
    _cli()
