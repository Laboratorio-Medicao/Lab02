from pathlib import Path

from experiment.analysis.rq1_rq2 import (
    TIME_BOX_SECONDS,
    PairedTestResult,
    Rq1Analysis,
    Rq2Analysis,
    Summary,
)
from experiment.config.lab02_design import TREATMENTS_BY_PARTICIPANT
from experiment.domain.enums import Treatment

_TREATMENT_LABEL = {Treatment.WITH_AI: "Com IA", Treatment.WITHOUT_AI: "Sem IA"}


def _num(value: float, digits: int = 1) -> str:
    # Arredonda antes de formatar para que ruído de ponto flutuante
    # (ex.: 555.8499999999999 em vez de 555.85) não mude a última casa.
    return f"{round(value, 9):.{digits}f}".replace(".", ",")


def _p(value: float) -> str:
    return _num(value, 3)


def _summary_row(label: str, summary: Summary, digits: int = 1, extra: str = "") -> str:
    return (
        f"| {label} | {summary.n} | {_num(summary.median, digits)} | "
        f"{_num(summary.q1, digits)} – {_num(summary.q3, digits)} | {_num(summary.iqr, digits)} | "
        f"{_num(summary.minimum, digits)} – {_num(summary.maximum, digits)} |{extra}"
    )


def _summary_table(
    by_treatment: dict[Treatment, Summary], unit: str, digits: int = 1
) -> list[str]:
    return [
        f"| Tratamento | n | Mediana ({unit}) | Q1 – Q3 | IQR | Mín – Máx |",
        "|---|---:|---:|---:|---:|---:|",
        *(_summary_row(_TREATMENT_LABEL[t], s, digits) for t, s in by_treatment.items()),
        "",
    ]


def _test_lines(test: PairedTestResult, h1: str, aggregate: str = "medianas") -> list[str]:
    if not test.applicable:
        return [
            f"- **Wilcoxon pareado por participante (n = {test.n_pairs}):** não aplicável — "
            f"as {aggregate} por participante não diferem entre os tratamentos (todas as "
            "diferenças são zero). Não há p-valor a reportar.",
        ]
    dropped = test.n_pairs - test.n_nonzero
    dropped_note = f"; {dropped} diferença(s) zero descartada(s)" if dropped else ""
    return [
        f"- **Wilcoxon pareado por participante (n = {test.n_pairs}{dropped_note}), "
        f"método {test.method}:** "
        f"W = {_num(test.statistic, 1)}; p unilateral (H1: {h1}) = {_p(test.p_one_sided)}; "
        f"p bilateral = {_p(test.p_two_sided)}; α = {_num(test.alpha, 2)}.",
    ]


def _h0_conclusion(test: PairedTestResult, aggregate: str = "medianas") -> str:
    if not test.applicable:
        return (
            f"**H0 não rejeitada** — as {aggregate} por participante são iguais nos dois "
            "tratamentos; não há diferença pareada para testar."
        )
    if test.reject_h0:
        return f"**H0 rejeitada** (p unilateral = {_p(test.p_one_sided)} < α = {_num(test.alpha, 2)})."
    conclusion = (
        f"**H0 não rejeitada** (p unilateral = {_p(test.p_one_sided)} ≥ α = {_num(test.alpha, 2)})."
    )
    if not test.has_power:
        conclusion += (
            f" Com {test.n_nonzero} par(es) com diferença não nula, o menor p possível é "
            f"1/2^{test.n_nonzero} = "
            f"{_p(test.min_attainable_p)}, maior que α: o teste não tem poder para rejeitar H0 "
            "nesta amostra, por maior que seja o efeito. A não rejeição **não** é evidência de "
            "ausência de efeito."
        )
    return conclusion


def _censoring_bias_note(censored_with_ai: int) -> str:
    if censored_with_ai == 0:
        return (
            "Como o tempo real seria ao menos o time-box e não há censura no tratamento com IA, "
            "travar o tempo só pode subestimar o tempo sem IA: o tratamento é conservador quanto "
            "a H1."
        )
    return (
        f"**Atenção:** há {censored_with_ai} trial(s) censurado(s) com IA; travar esses tempos "
        "no time-box subestima o tempo com IA e, portanto, favorece H1."
    )


def _rq1_section(rq1: Rq1Analysis) -> list[str]:
    lines = [
        "## RQ1 — Tempo até green",
        "",
        "> H0: o uso de assistente de IA não reduz o tempo necessário para resolver uma tarefa "
        "de programação. H1: reduz.",
        "",
        "### Estatística descritiva por tratamento",
        "",
        *_summary_table(rq1.by_treatment, "s"),
        "**Trials censurados** (time-box de "
        f"{_num(TIME_BOX_SECONDS, 0)} s atingido): "
        + "; ".join(f"{_TREATMENT_LABEL[t]}: {n}" for t, n in rq1.censored_by_treatment.items())
        + ". Trials censurados entram na análise com o tempo travado no time-box — nunca são "
        "descartados. "
        + _censoring_bias_note(rq1.censored_by_treatment[Treatment.WITH_AI]),
        "",
    ]
    with_ai, without_ai = rq1.by_treatment[Treatment.WITH_AI], rq1.by_treatment[Treatment.WITHOUT_AI]
    if rq1.fully_separated:
        lines += [
            f"**Separação completa:** todos os tempos com IA (máx. {_num(with_ai.maximum)} s) "
            f"ficaram abaixo de todos os tempos sem IA (mín. {_num(without_ai.minimum)} s).",
            "",
        ]

    lines += [
        "### Por participante (unidade do teste pareado)",
        "",
        "Com n = 3 trials por célula, o IQR diz pouco; por isso são mostrados mínimo, mediana e "
        "máximo.",
        "",
        "| Participante | Com IA: mín / mediana / máx (s) | Sem IA: mín / mediana / máx (s) "
        "| Diferença das medianas (s) | Com IA / sem IA |",
        "|---|---:|---:|---:|---:|",
    ]
    for c in rq1.by_participant:
        ratio = f"{_num(100 * c.ratio)}%" if c.ratio is not None else "—"
        lines.append(
            f"| {c.participant} "
            f"| {_num(c.with_ai.minimum)} / {_num(c.with_ai.median)} / {_num(c.with_ai.maximum)} "
            f"| {_num(c.without_ai.minimum)} / {_num(c.without_ai.median)} / {_num(c.without_ai.maximum)} "
            f"| {_num(c.difference)} | {ratio} |"
        )
    lines += [
        "",
        f"**Tamanho de efeito:** diferença entre as medianas gerais = "
        f"{_num(with_ai.median - without_ai.median)} s. A correlação rank-biserial não é "
        + (
            "reportada: com todas as diferenças no mesmo sinal ela vale ±1 e não informa nada."
            if rq1.test.all_same_sign
            else f"reportada: com n = {rq1.test.n_pairs} pares ela assume poucos valores e "
            "pouco acrescenta às diferenças por participante acima."
        ),
        "",
        "### Teste de hipótese",
        "",
        *_test_lines(rq1.test, "com IA < sem IA"),
        f"- **Conclusão:** {_h0_conclusion(rq1.test)}",
        "",
        "### Por kata (exploratório — não pareado)",
        "",
        "Cada kata foi resolvido por participantes diferentes em cada tratamento (2 trials de um "
        "tratamento contra 1 do outro), e os katas reutilizam os mesmos 3 participantes — as "
        "observações não são pareadas nem independentes. A tabela é apenas descritiva; nenhum "
        "teste nem decisão sobre H0 é feito sobre ela.",
        "",
        "| Kata | Com IA (s) | Sem IA (s) | Mediana com IA | Mediana sem IA |",
        "|---|---|---|---:|---:|",
    ]
    for k in rq1.by_kata:
        with_cell = ", ".join(f"{p}: {_num(v)}" for p, v in k.with_ai)
        without_cell = ", ".join(f"{p}: {_num(v)}" for p, v in k.without_ai)
        lines.append(
            f"| {k.kata_id} | {with_cell} | {without_cell} | {_num(k.median_with_ai)} "
            f"| {_num(k.median_without_ai)} |"
        )

    lines += [
        "",
        "### Outliers (cercas de Tukey)",
        "",
        "Cercas Q1 − 1,5·IQR e Q3 + 1,5·IQR, calculadas sobre todos os trials de cada tratamento. "
        "Os outliers são **sinalizados e mantidos**: o teste usa a mediana de cada participante, "
        "que é pouco sensível a um valor extremo.",
        "",
        "| Tratamento | Cerca inferior (s) | Cerca superior (s) | Outliers |",
        "|---|---:|---:|---|",
    ]
    for t, result in rq1.outliers.items():
        outliers = (
            ", ".join(f"{r.participant} {r.kata_id} ({_num(r.elapsed_seconds)} s)" for r in result.outliers)
            or "nenhum"
        )
        lines.append(
            f"| {_TREATMENT_LABEL[t]} | {_num(result.lower_fence)} | {_num(result.upper_fence)} "
            f"| {outliers} |"
        )

    lines.append("")
    return lines


def _rq2_section(rq2: Rq2Analysis) -> list[str]:
    return [
        "## RQ2 — Defeitos (testes de aceitação falhando)",
        "",
        "> H0: o uso de assistente de IA não reduz a quantidade de defeitos (testes que falham) "
        "no código produzido. H1: reduz.",
        "",
        "### Taxa de sucesso (% de testes passando ao final do trial)",
        "",
        *_summary_table(rq2.success_rate_by_treatment, "%"),
        "### Nº de testes falhando ao final do trial",
        "",
        *_summary_table(rq2.failing_by_treatment, "testes", digits=0),
        "### Por participante (unidade do teste pareado)",
        "",
        "Na RQ2 o par de cada participante usa a **média** dos seus trials em cada "
        "tratamento, e não a mediana: com a mediana, um único trial com testes falhando "
        "não alteraria o par.",
        "",
        "| Participante | Taxa de sucesso média com IA (%) | sem IA (%) "
        "| Testes falhando (média/trial) com IA | sem IA |",
        "|---|---:|---:|---:|---:|",
        *(
            f"| {rate.participant} | {_num(rate.with_ai.mean)} | {_num(rate.without_ai.mean)} "
            f"| {_num(failing.with_ai.mean, 2)} | {_num(failing.without_ai.mean, 2)} |"
            for rate, failing in zip(rq2.success_rate_by_participant, rq2.failing_by_participant)
        ),
        "",
        "### Teste de hipótese",
        "",
        "**Taxa de sucesso:**",
        "",
        *_test_lines(rq2.success_rate_test, "com IA > sem IA", "médias"),
        f"- **Conclusão:** {_h0_conclusion(rq2.success_rate_test, 'médias')}",
        "",
        "**Testes falhando:**",
        "",
        *_test_lines(rq2.failing_test, "com IA < sem IA", "médias"),
        f"- **Conclusão:** {_h0_conclusion(rq2.failing_test, 'médias')}",
        "",
        _multiplicity_note(rq2),
        "",
        "**Efeito de teto (validade de construto):** o cronômetro encerra o trial no green, isto "
        "é, quando todos os testes passam. Uma taxa de sucesso abaixo de 100% só pode aparecer em "
        "um trial censurado, então a RQ2 não é independente da censura da RQ1. "
        + _ceiling_note(rq2),
        "",
    ]


def _multiplicity_note(rq2: Rq2Analysis) -> str:
    tested = sum(1 for t in (rq2.success_rate_test, rq2.failing_test) if t.applicable)
    if tested == 0:
        return (
            "Como nenhuma das duas métricas de RQ2 chegou a ser testada, não há correção para "
            "comparações múltiplas a aplicar."
        )
    if tested == 1:
        return "Só uma das métricas de RQ2 foi testada, então não há comparações múltiplas."
    return (
        "Nenhuma correção para comparações múltiplas foi aplicada. As duas métricas de RQ2 "
        "derivam dos mesmos testes de aceitação e são fortemente dependentes: os dois p-valores "
        "devem ser lidos como uma única evidência, não como dois testes independentes."
    )


def _ceiling_note(rq2: Rq2Analysis) -> str:
    if rq2.censored_count == 0:
        return "Como nenhum trial foi censurado, a RQ2 não tem variação possível nesta coleta."
    return (
        f"Houve {rq2.censored_count} trial(s) censurado(s) e {rq2.trials_with_failures} "
        "trial(s) com testes falhando ao final."
    )


def _join_names(names: list[str]) -> str:
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} e {names[-1]}"


def _block_participants() -> list[str]:
    """Participantes cuja ordem de tratamentos muda uma única vez (blocos)."""
    return [
        participant
        for participant, treatments in TREATMENTS_BY_PARTICIPANT.items()
        if sum(1 for a, b in zip(treatments, treatments[1:]) if a != b) == 1
    ]


def _caveats_section(rq1: Rq1Analysis) -> list[str]:
    with_ai = rq1.by_treatment[Treatment.WITH_AI]
    leave_out_times = rq1.leave_out_with_ai_times
    blocks = _block_participants()
    lines = [
        "## Ressalvas",
        "",
        "- **Desvio de contrabalanceamento:** Arthur e Marcos executaram uma ordem de tratamentos "
        "diferente da fechada na S01 (ver `docs/experiment_design.md`, \"Registro de desvio de "
        "protocolo\").",
        "- **Resolução do cronômetro:** com `--kata-path`, o green é verificado a cada 5 s "
        "(padrão), uma resolução próxima da escala dos tempos com IA "
        f"({_num(with_ai.minimum, 0)}–{_num(with_ai.maximum, 0)} s).",
    ]
    if leave_out_times:
        lines.insert(
            3,
            f"- **Tempos com IA de {rq1.leave_out_participant}** "
            f"({' / '.join(_num(t, 3) for t in leave_out_times)} s, amplitude de "
            f"{_num(max(leave_out_times) - min(leave_out_times), 3)} s): confirmados apenas por "
            "autorrelato, sem log independente.",
        )
    if blocks:
        lines.append(
            f"- **Confusão tratamento × kata × ordem:** {_join_names(blocks)} fizeram os tratamentos "
            "em blocos, então para eles tratamento, kata e ordem de execução andam juntos."
        )
    lines += [
        "- **Leitura do CSV:** os valores de `data/trials.csv` são lidos numericamente, não como "
        "texto, porque nem todas as linhas precisam seguir o formato exato de "
        "`TrialRecord.to_row` (número de casas decimais).",
    ]
    if not rq1.test.has_power:
        lines.append(
            f"- **Tamanho amostral:** com {rq1.test.n_pairs} participantes, o teste pareado não "
            f"tem poder para rejeitar H0 a α = {_num(rq1.test.alpha, 2)}; os resultados devem ser "
            "lidos principalmente pela estatística descritiva."
        )
    return lines + [
        "",
    ]


def generate_markdown(rq1: Rq1Analysis, rq2: Rq2Analysis) -> str:
    lines = [
        "# Análise Estatística — RQ1 e RQ2 — Lab02",
        "",
        "Gerado por `python analyze_rq1_rq2.py` a partir de `data/trials.csv` (Issue #15).",
        "",
        "**Método:** mediana e IQR por tratamento; quartis por "
        "`statistics.quantiles(method=\"inclusive\")` (interpolação linear, igual ao padrão do "
        "numpy/pandas). Teste confirmatório: Wilcoxon signed-rank pareado por participante "
        "(um valor com IA contra um sem IA de cada integrante: a mediana dos tempos na RQ1 e a "
        "média dos trials na RQ2), unilateral porque as H1 são direcionais, com α = 0,05. "
        "W é a soma dos postos das diferenças positivas (com IA − sem IA), a estatística "
        "retornada pelo scipy no teste unilateral.",
        "",
        *_rq1_section(rq1),
        *_rq2_section(rq2),
        *_caveats_section(rq1),
    ]
    return "\n".join(lines)


def export(rq1: Rq1Analysis, rq2: Rq2Analysis, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_markdown(rq1, rq2), encoding="utf-8")
    print(f"Relatório gerado em: {output_path}")
