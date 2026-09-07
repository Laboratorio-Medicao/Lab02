"""Coleta de métricas estáticas via Radon para RQ3.

Métricas: complexidade ciclomática média (`radon cc`), índice de
manutenibilidade (`radon mi`) e LOC — obrigatória como controle sempre que
complexidade for reportada. Preparado na S01 (Issue #5); a execução sobre o
código final de cada trial real é escopo da S02.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


@dataclass(frozen=True)
class StaticMetrics:
    path: str
    loc: int
    cyclomatic_complexity_avg: float
    maintainability_index: float

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "loc": self.loc,
            "cyclomatic_complexity_avg": round(self.cyclomatic_complexity_avg, 2),
            "maintainability_index": round(self.maintainability_index, 2),
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
    )


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
    args = parser.parse_args()

    metrics = collect_static_metrics(args.path, include_tests=args.include_tests)

    if args.json:
        print(json.dumps(metrics.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Path: {metrics.path}")
        print(f"LOC: {metrics.loc}")
        print(f"Complexidade ciclomática média (CC): {metrics.cyclomatic_complexity_avg:.2f}")
        print(f"Índice de Manutenibilidade (MI): {metrics.maintainability_index:.2f}")


if __name__ == "__main__":
    _cli()
