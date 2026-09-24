"""
Boxplots comparativos com IA × sem IA (RQ1, RQ2, RQ3) para o relatório — Issue #17.
Uso: python3 generate_figures.py
"""

from pathlib import Path

from experiment.analysis.consolidated import consolidate
from experiment.analysis.rq1_rq2 import analyze_rq1, analyze_rq2, load_trials
from experiment.analysis.static_metrics_data import load_static_metrics, rq3_tests
from experiment.visualization.boxplots import (
    RQ1_PANEL,
    RQ2_PANELS,
    RQ3_PANELS,
    build_rq1_figure,
    build_rq2_figure,
    build_rq3_figure,
    rank_sums,
    save_figure,
)

OUTPUT_DIR = Path("docs/figures")


def main():
    records = load_trials()
    static_records = load_static_metrics(trials=records)
    data = consolidate(records, static_records)
    rq1_tests = {RQ1_PANEL[1]: analyze_rq1(records).test}
    rq2 = analyze_rq2(records)
    success_label, failing_label = (label for _, label in RQ2_PANELS)
    rq2_tests = {success_label: rq2.success_rate_test, failing_label: rq2.failing_test}
    rq3 = rq3_tests(static_records)

    figures = {
        "rq1_tempo": build_rq1_figure(
            data, rq1_tests[RQ1_PANEL[1]], rank_sums(data, (RQ1_PANEL,), rq1_tests)[RQ1_PANEL[1]]
        ),
        "rq2_defeitos": build_rq2_figure(data, rq2_tests, rank_sums(data, RQ2_PANELS, rq2_tests)),
        "rq3_estrutura": build_rq3_figure(data, rq3, rank_sums(data, RQ3_PANELS, rq3)),
    }
    for name, fig in figures.items():
        for path in save_figure(fig, OUTPUT_DIR, name):
            print(f"Figura gerada em: {path}")


if __name__ == "__main__":
    main()
