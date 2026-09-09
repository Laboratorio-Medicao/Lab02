from pathlib import Path

from experiment.config.experiment_design import ExperimentDesign
from experiment.domain.enums import ResearchQuestion, Treatment


def _kata_label(design: ExperimentDesign, kata_index: int) -> str:
    if kata_index < len(design.katas):
        return design.katas[kata_index].id
    return f"Kata {kata_index + 1}"


def _katas_paragraph(design: ExperimentDesign) -> list[str]:
    if not design.katas:
        return []

    names = [kata.name for kata in design.katas]
    names_text = names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" e {names[-1]}"

    return [
        f"Os objetos experimentais são os {len(design.katas)} exercícios autorais "
        "documentados em [`docs/katas.md`](katas.md): "
        f"{names_text}. Cada um possui testes automatizados de aceitação em "
        "[`katas/`](../katas/).",
        "",
    ]


def _treatment_rows(design: ExperimentDesign) -> list[str]:
    rows: list[str] = []
    protocol = design.protocol

    for participant in protocol.participants:
        assignments = sorted(
            (a for a in protocol.assignments if a.participant == participant),
            key=lambda a: a.kata_index,
        )

        run_start = run_end = None
        run_treatment = None
        for assignment in assignments:
            if (
                run_treatment is not None
                and assignment.treatment == run_treatment
                and assignment.kata_index == run_end + 1
            ):
                run_end = assignment.kata_index
                continue

            if run_treatment is not None:
                rows.append(_treatment_row(design, participant, run_start, run_end, run_treatment))
            run_start = run_end = assignment.kata_index
            run_treatment = assignment.treatment

        if run_treatment is not None:
            rows.append(_treatment_row(design, participant, run_start, run_end, run_treatment))

    return rows


def _treatment_row(
    design: ExperimentDesign, participant: str, start: int, end: int, treatment: Treatment
) -> str:
    label = (
        _kata_label(design, start)
        if start == end
        else f"{_kata_label(design, start)} a {_kata_label(design, end)}"
    )
    treatment_label = "Com IA" if treatment == Treatment.WITH_AI else "Sem IA"
    return f"| {participant} | {label} | {treatment_label} |"


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
        if var.notes:
            lines += ["", f"\t{var.notes}"]

    lines += [
        "",
        "**Variáveis de controle:**",
        "",
    ]
    for var in design.control_variables:
        rqs = ", ".join(rq.value for rq in var.research_questions)
        lines.append(f"- **{var.name}** ({var.unit}) — {var.description} `[{rqs}]`")
        if var.notes:
            lines += ["", f"\t{var.notes}"]

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
        *_katas_paragraph(design),
        "### Atribuição de tratamentos",
        "",
        "| Participante | Kata | Tratamento |",
        "|---|---|---|",
        *_treatment_rows(design),
    ]

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
