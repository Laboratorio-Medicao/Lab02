import re
import unicodedata
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
    """Uma linha por participante × tratamento, na ordem do primeiro kata de cada grupo."""
    rows: list[str] = []
    protocol = design.protocol

    for participant in protocol.participants:
        by_treatment: dict[Treatment, list[int]] = {}
        for assignment in sorted(
            (a for a in protocol.assignments if a.participant == participant),
            key=lambda a: a.kata_index,
        ):
            by_treatment.setdefault(assignment.treatment, []).append(assignment.kata_index)

        for treatment, indexes in sorted(by_treatment.items(), key=lambda item: item[1][0]):
            rows.append(_treatment_row(design, participant, indexes, treatment))

    return rows


def _treatment_row(
    design: ExperimentDesign, participant: str, indexes: list[int], treatment: Treatment
) -> str:
    labels = [_kata_label(design, i) for i in indexes]
    contiguous = indexes == list(range(indexes[0], indexes[-1] + 1))
    if len(labels) == 1:
        label = labels[0]
    elif contiguous:
        label = f"{labels[0]} a {labels[-1]}"
    else:
        label = ", ".join(labels[:-1]) + f" e {labels[-1]}"
    treatment_label = "Com IA" if treatment == Treatment.WITH_AI else "Sem IA"
    return f"| {participant} | {label} | {treatment_label} |"


# Blocos manuais: trechos escritos à mão dentro do Markdown gerado (registro de
# desvios, status de mitigações etc.). O gerador emite um bloco vazio em cada
# ponto de ancoragem e `export` reinsere o conteúdo que já existia no arquivo,
# para que regenerar o desenho nunca apague documentação manual.
_MANUAL_BLOCK_RE = re.compile(
    r"<!-- manual:start (?P<name>[\w:-]+) -->\n(?P<body>.*?)<!-- manual:end (?P=name) -->",
    re.DOTALL,
)


def _manual_block(name: str) -> list[str]:
    return [f"<!-- manual:start {name} -->", f"<!-- manual:end {name} -->"]


def _slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


def extract_manual_blocks(markdown: str) -> dict[str, str]:
    return {m.group("name"): m.group("body") for m in _MANUAL_BLOCK_RE.finditer(markdown)}


def merge_manual_blocks(generated: str, existing: str) -> str:
    """Preenche os blocos manuais de `generated` com o conteúdo de `existing`.

    Um bloco que existia no arquivo mas não tem mais âncora no texto gerado é
    anexado ao final, em vez de descartado.
    """
    blocks = extract_manual_blocks(existing)
    used: set[str] = set()

    def fill(match: re.Match) -> str:
        name = match.group("name")
        used.add(name)
        body = blocks.get(name, match.group("body"))
        return f"<!-- manual:start {name} -->\n{body}<!-- manual:end {name} -->"

    merged = _MANUAL_BLOCK_RE.sub(fill, generated)
    orphans = [name for name in blocks if name not in used]
    if orphans:
        merged = merged.rstrip("\n") + "\n\n## Conteúdo manual sem âncora no gerador\n"
        for name in orphans:
            merged += (
                f"\n<!-- manual:start {name} -->\n{blocks[name]}<!-- manual:end {name} -->\n"
            )
    return merged


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
        "",
        *_manual_block("protocolo"),
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
            *_manual_block(f"ameaca:{_slug(threat.name)}"),
            "",
        ]
    lines += [*_manual_block("ameacas-adicionais"), ""]

    return "\n".join(lines)


class ManualContentLossError(RuntimeError):
    """Regenerar o desenho removeria linhas que existem hoje no arquivo."""


def lost_lines(existing: str, merged: str) -> list[str]:
    """Linhas não vazias de `existing` que não aparecem em `merged`."""
    kept = set(merged.splitlines())
    return [line for line in existing.splitlines() if line.strip() and line not in kept]


def export(design: ExperimentDesign, output_path: Path, force: bool = False) -> None:
    """Gera o desenho em `output_path` preservando os blocos manuais.

    Se o resultado perderia alguma linha do arquivo atual (texto manual fora de
    um bloco `<!-- manual:start ... -->`), nada é gravado e a função levanta
    `ManualContentLossError`, a menos que `force=True`.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = generate_markdown(design)
    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        markdown = merge_manual_blocks(markdown, existing)
        missing = lost_lines(existing, markdown)
        if missing and not force:
            preview = "\n".join(f"  - {line[:100]}" for line in missing[:10])
            raise ManualContentLossError(
                f"{output_path}: a regeneração removeria {len(missing)} linha(s) do "
                "arquivo atual. Mova o texto manual para um bloco "
                "<!-- manual:start ... --> ou rode com --force.\n" + preview
            )
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Relatório gerado em: {output_path}")
