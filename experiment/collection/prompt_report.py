from pathlib import Path

from experiment.collection.prompt_consolidator import ConsolidatedReport, ParticipantSummary


def _participant_section(summary: ParticipantSummary) -> list[str]:
    return [
        f"### {summary.participant}",
        "",
        f"| Métrica | Valor |",
        f"|---|---|",
        f"| Trials com IA | {summary.trials_with_ai} |",
        f"| Trials sem IA | {summary.trials_without_ai} |",
        f"| Total de prompts (com IA) | {summary.total_prompts} |",
        f"| Média de prompts por trial com IA | {summary.avg_prompts_with_ai} |",
        f"| Percepção de produtividade com IA (média 1–5) | {summary.avg_productivity_with_ai} |",
        f"| Percepção de produtividade sem IA (média 1–5) | {summary.avg_productivity_without_ai} |",
        f"| Tipo de ajuda mais solicitado | {summary.most_requested_help} |",
        "",
    ]


def generate_markdown(report: ConsolidatedReport) -> str:
    lines: list[str] = [
        "# Consolidação de Prompts e Dados Qualitativos — Lab02",
        "",
        "## Visão Geral",
        "",
        f"| Métrica | Valor |",
        f"|---|---|",
        f"| Total de registros | {report.total_records} |",
        f"| Participantes | {', '.join(report.participants)} |",
        f"| Média geral de prompts por trial (com IA) | {report.overall_avg_prompts} |",
        f"| Tipo de ajuda mais solicitado (geral) | {report.most_requested_help_overall} |",
        "",
        "## Por Participante",
        "",
    ]
    for summary in report.summaries:
        lines += _participant_section(summary)

    return "\n".join(lines)


def export(report: ConsolidatedReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_markdown(report), encoding="utf-8")
    print(f"Relatório gerado em: {output_path}")
