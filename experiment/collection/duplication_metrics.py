"""Coleta percentual de linhas duplicadas usando jscpd."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class DuplicationMetricsError(RuntimeError):
    """Indica que o jscpd não pôde produzir um relatório válido."""


@dataclass(frozen=True)
class DuplicationMetrics:
    duplicated_lines: int
    duplicated_lines_percent: float
    duplicate_blocks: int
    total_lines: int
    tool: str = "jscpd"
    tool_version: str = "4.0.5"

    def to_dict(self) -> dict[str, int | float | str]:
        return {
            "duplicated_lines": self.duplicated_lines,
            "duplicated_lines_percent": round(self.duplicated_lines_percent, 2),
            "duplicate_blocks": self.duplicate_blocks,
            "total_lines": self.total_lines,
            "tool": self.tool,
            "tool_version": self.tool_version,
        }


def _jscpd_executable() -> str:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        project_root / "node_modules/.bin/jscpd.cmd",
        project_root / "node_modules/.bin/jscpd",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())
    executable = shutil.which("jscpd") or shutil.which("jscpd.cmd")
    if executable:
        return executable
    raise DuplicationMetricsError(
        "jscpd não encontrado. Execute 'npm ci' antes de coletar duplicação."
    )


def _python_files(path: Path, include_tests: bool) -> list[Path]:
    if path.is_file():
        candidates = [path] if path.suffix == ".py" else []
    else:
        candidates = sorted(path.rglob("*.py"))
    if include_tests:
        return candidates
    return [
        file
        for file in candidates
        if not (file.name.startswith("test_") or file.name.endswith("_test.py"))
    ]


def collect_duplication_metrics(path: Path, include_tests: bool = False) -> DuplicationMetrics:
    """Executa jscpd somente sobre os arquivos Python selecionados."""
    files = _python_files(path, include_tests)
    if not files:
        raise ValueError(f"Nenhum arquivo .py encontrado em {path}")

    with tempfile.TemporaryDirectory(prefix="lab02-jscpd-") as temporary_dir:
        source_root = Path(temporary_dir) / "source"
        source_root.mkdir()
        for index, file in enumerate(files):
            shutil.copy2(file, source_root / f"source_{index}.py")

        report_dir = Path(temporary_dir) / "report"
        command = [
            _jscpd_executable(),
            "--format",
            "python",
            "--reporters",
            "json",
            "--min-lines",
            "5",
            "--min-tokens",
            "20",
            "--output",
            "report",
            "source",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=temporary_dir,
        )
        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip()
            raise DuplicationMetricsError(f"jscpd falhou: {details}")

        report_path = report_dir / "jscpd-report.json"
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise DuplicationMetricsError("jscpd não gerou um JSON válido.") from error

    try:
        statistics = report["statistics"]["formats"]["python"]["total"]
        return DuplicationMetrics(
            duplicated_lines=int(statistics["duplicatedLines"]),
            duplicated_lines_percent=float(statistics["percentage"]),
            duplicate_blocks=int(statistics["clones"]),
            total_lines=int(statistics["lines"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise DuplicationMetricsError("Campos ausentes no relatório do jscpd.") from error