"""
Figuras do relatório final (RQ1, RQ2, RQ3) — Issues #17/#21.
Uso: python3 generate_figures.py
"""

from pathlib import Path

from experiment.analysis import mi_prompts
from experiment.analysis.rq1_rq2 import analyze_rq1, load_trials
from experiment.analysis.rq3 import analyse
from experiment.visualization.report_figures import build_all, build_bonus, save_all

OUTPUT_DIR = Path("docs/figures")


def main():
    results = analyse()
    figures = build_all(analyze_rq1(load_trials()), results)
    bonus = mi_prompts.analyse()
    figures |= build_bonus(bonus.components, bonus.prompts_quality, results.observations)
    for path in save_all(figures, OUTPUT_DIR):
        print(f"Figura gerada em: {path}")


if __name__ == "__main__":
    main()
