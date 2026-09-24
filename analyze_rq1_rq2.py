"""
Análise estatística de RQ1 (tempo) e RQ2 (defeitos) e geração do relatório markdown.
Uso: python3 analyze_rq1_rq2.py
"""

import csv
from pathlib import Path

from experiment.analysis.rq1_rq2 import DEFAULT_TRIALS_PATH, analyze_rq1, analyze_rq2, load_trials
from experiment.analysis.rq1_rq2_report import export

OUTPUT_PATH = Path("docs/analysis_rq1_rq2.md")


def off_format_participants(path: Path = DEFAULT_TRIALS_PATH) -> tuple[str, ...]:
    """Participantes com algum `elapsed_seconds` fora das 3 casas de `TrialRecord.to_row`."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    off = {
        row["participant"]
        for row in rows
        if len(row["elapsed_seconds"].partition(".")[2]) != 3
    }
    return tuple(dict.fromkeys(row["participant"] for row in rows if row["participant"] in off))


def main():
    records = load_trials()
    export(analyze_rq1(records), analyze_rq2(records), OUTPUT_PATH, off_format_participants())


if __name__ == "__main__":
    main()
