from pathlib import Path

from experiment.config.experiment_design import ExperimentDesign
from experiment.domain.enums import ResearchQuestion, Treatment


def generate_markdown(design: ExperimentDesign) -> str:
    lines: list[str] = []

    lines += [
        "# Desenho do Experimento — Lab02",
        "",
        "## Objetivo (GQM)",
        "",
        design.goal,
        "",
    ]

    lines += ["## Hipóteses", ""]
    for rq in ResearchQuestion:
        h0, h1 = design.get_hypotheses(rq)
        lines += [
            f"### {rq.value}",
            "",
            f"- **H0:** {h0.statement}",
            f"- **H1:** {h1.statement}",
            "",
        ]

    lines += [
        "## Variáveis",
        "",
        f"**Variável independente:** {design.independent_variable.name} "
        f"— {design.independent_variable.description}",
        "",
        "**Variáveis dependentes:**",
        "",
    ]
    for var in design.dependent_variables:
        rqs = ", ".join(rq.value for rq in var.research_questions)
        lines.append(f"- **{var.name}** ({var.unit}) — {var.description} `[{rqs}]`")

    lines += [
        "",
        "**Variáveis de controle:**",
        "",
    ]
    for var in design.control_variables:
        rqs = ", ".join(rq.value for rq in var.research_questions)
        lines.append(f"- **{var.name}** ({var.unit}) — {var.description} `[{rqs}]`")

    protocol = design.protocol
    lines += [
        "",
        "## Protocolo Experimental",
        "",
        f"- **Tipo:** Crossover within-subject contrabalanceado",
        f"- **Participantes:** {', '.join(protocol.participants)}",
        f"- **Katas:** {protocol.n_katas}",
        f"- **Time-box por trial:** {protocol.time_box_minutes} min",
        f"- **Medições totais:** {len(protocol.assignments)} trials "
        f"({protocol.n_katas} katas × {len(protocol.participants)} participantes)",
        "",
        "### Atribuição de tratamentos",
        "",
        "| Participante | Kata | Tratamento |",
        "|---|---|---|",
    ]
    for assignment in protocol.assignments:
        treatment_label = "Com IA" if assignment.treatment == Treatment.WITH_AI else "Sem IA"
        lines.append(
            f"| {assignment.participant} | Kata {assignment.kata_index + 1} | {treatment_label} |"
        )

    lines += [
        "",
        "## Ameaças à Validade",
        "",
    ]
    category_labels = {
        "internal_validity": "Validade Interna",
        "external_validity": "Validade Externa",
        "statistical_conclusion": "Conclusão Estatística",
        "construct_validity": "Validade de Constructo",
    }
    for threat in design.threats:
        label = category_labels.get(threat.category.value, threat.category.value)
        lines += [
            f"### {threat.name} `[{label}]`",
            "",
            f"**Descrição:** {threat.description}",
            "",
            f"**Mitigação:** {threat.mitigation}",
            "",
        ]

    return "\n".join(lines)


def export(design: ExperimentDesign, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_markdown(design), encoding="utf-8")
    print(f"Relatório gerado em: {output_path}")
