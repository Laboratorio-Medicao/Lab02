"""
Análise estatística de RQ1 (tempo) e RQ2 (defeitos) e geração do relatório markdown.
Uso: python3 analyze_rq1_rq2.py
"""

from pathlib import Path

from experiment.analysis.rq1_rq2 import analyze_rq1, analyze_rq2, load_trials
from experiment.analysis.rq1_rq2_report import export

OUTPUT_PATH = Path("docs/analysis_rq1_rq2.md")


def main():
    records = load_trials()
    export(analyze_rq1(records), analyze_rq2(records), OUTPUT_PATH)


if __name__ == "__main__":
    main()
