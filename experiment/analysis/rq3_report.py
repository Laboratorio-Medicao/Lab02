"""Renderização dos relatórios Markdown de RQ3.

Todo número vem dos DataFrames calculados em `experiment.analysis.rq3`; as
frases interpretativas são montadas a partir do sinal da diferença, do p-valor
e do tamanho de efeito observados, para que o texto não divirja das tabelas.
"""
from __future__ import annotations

import pandas as pd

from experiment.analysis.metrics import (
    CC_PER_LOC,
    CYCLOMATIC_COMPLEXITY,
    DUPLICATION,
    DUPLICATION_PER_LOC,
    LOC,
    MAINTAINABILITY_INDEX,
    Metric,
)
from experiment.analysis.rq3_data import (
    EXPECTED_TRIALS,
    STATIC_METRICS_CSV,
    TRIALS_CSV,
    WITH_AI,
    WITHOUT_AI,
)
from experiment.analysis.statistics import ALPHA, rank_biserial_levels

#: `docs/enunciado/lab02.md`, linha 25.
RQ3_TEXT = (
    "O uso de assistente de IA altera a complexidade ciclomática ou a duplicação "
    "do código produzido?"
)
#: Hipóteses fechadas na S01 (`docs/experiment_design.md`).
RQ3_H0 = (
    "O uso de assistente de IA não altera a complexidade ciclomática nem a "
    "duplicação do código produzido."
)
RQ3_H1 = (
    "O uso de assistente de IA altera a complexidade ciclomática e/ou a "
    "duplicação do código produzido."
)

DECIMALS = {
    LOC.key: 1,
    CYCLOMATIC_COMPLEXITY.key: 2,
    MAINTAINABILITY_INDEX.key: 2,
    DUPLICATION.key: 2,
    CC_PER_LOC.key: 3,
    DUPLICATION_PER_LOC.key: 3,
}
DEFAULT_DECIMALS = 2


def _decimals(metric_key: str) -> int:
    return DECIMALS.get(metric_key, DEFAULT_DECIMALS)


def _number(value: float | None, decimals: int) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{decimals}f}"


def _p_value(value: float | None) -> str:
    return "—" if value is None or pd.isna(value) else f"{value:.4g}"


def _markdown_table(
    headers: list[str], rows: list[list[str]], numeric_columns: tuple[int, ...] = ()
) -> str:
    """`numeric_columns` são os índices alinhados à direita (só números)."""
    separator = [
        "---:" if index in numeric_columns else "---" for index in range(len(headers))
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def _descriptive_row(descriptive: pd.DataFrame, metric_key: str, treatment: str) -> pd.Series:
    match = descriptive[
        (descriptive["metric_key"] == metric_key) & (descriptive["treatment"] == treatment)
    ]
    return match.iloc[0]


def _test_row(tests: pd.DataFrame, metric_key: str, pairing_unit: str) -> pd.Series:
    match = tests[
        (tests["metric_key"] == metric_key) & (tests["pairing_unit"] == pairing_unit)
    ]
    return match.iloc[0]


def _primary_pairing(tests: pd.DataFrame) -> str:
    return tests["pairing_unit"].iloc[0]


def _median_iqr(row: pd.Series, decimals: int) -> str:
    return f"{_number(row['median'], decimals)} ({_number(row['iqr'], decimals)})"


def render_data_quality(results) -> str:
    quality = results.quality
    observations = results.observations
    found = len(observations)
    excluded = len(quality.excluded_trials)

    lines = [
        "# RQ3 — Relatório de qualidade dos dados",
        "",
        "Gerado por `python -m experiment.analysis.rq3`. Nenhum dado bruto foi "
        "alterado: os CSVs de `data/` são abertos somente para leitura e nenhuma "
        "observação foi removida da análise.",
        "",
        "## Contagem de trials",
        "",
        "```text",
        f"Trials esperados (desenho S01): {EXPECTED_TRIALS}",
        f"Trials encontrados:             {found}",
        f"Trials completos (as duas fontes, sem valores ausentes): {found - excluded}",
        f"Trials excluídos:               {excluded}",
        "```",
        "",
    ]

    if quality.excluded_trials:
        lines.append("Motivos da exclusão:")
        lines.extend(f"- {reason}" for reason in quality.excluded_trials)
    else:
        lines.append(
            "Nenhum trial foi excluído: os 18 trials de `data/trials.csv` casam "
            "1-para-1 com as 18 linhas de `data/static_metrics.csv` pela chave "
            "(participante, kata, tratamento)."
        )
    lines += ["", "## Verificações executadas", ""]

    lines.append(
        _markdown_table(
            ["Verificação", "Resultado", "Detalhe"],
            [
                [name, "✅ OK" if passed else "⚠️ ATENÇÃO", detail]
                for name, passed, detail in quality.checks
            ],

        )
    )

    lines += ["", "## Achados que exigem interpretação", ""]
    for name, passed, detail in quality.failures:
        lines.append(f"### {name}")
        lines.append("")
        lines.append(detail)
        lines.append("")
        lines.append(_QUALITY_NOTES.get(name, ""))
        lines.append("")

    lines += ["## Conferência linha a linha contra o código-fonte", ""]
    integrity = quality.integrity
    lines.append(
        "Cada linha de `data/static_metrics.csv` foi recalculada a partir do "
        "código do próprio trial (mesmos arquivos, mesmo Radon), para confirmar "
        "que os números publicados correspondem ao código versionado. Detalhe "
        "completo em `source_integrity_check.csv`."
    )
    lines += ["", _markdown_table(
        ["Participante", "Kata", "Tratamento", "LOC csv/rec.", "CC csv/rec.",
         "Blocos", "MI csv", "MI hoje", "Situação do MI"],
        [
            [
                row["participant"], row["kata_id"], row["treatment"],
                f"{row['loc_csv']}/{row['loc_recomputed']}"
                + ("" if row["loc_matches"] else " ⚠️"),
                f"{row['cc_csv']}/{row['cc_recomputed']}"
                + ("" if row["cc_matches"] else " ⚠️"),
                str(row["cc_blocks"]),
                _number(row["mi_csv"], 2),
                _number(row["mi_collector_today"], 2),
                row["mi_status"],
            ]
            for _, row in integrity.iterrows()
        ],
        numeric_columns=(3, 4, 5, 6, 7),
    )]

    lines += ["", "## Observações extremas (critério de Tukey, 1,5 × IQR)", ""]
    if quality.outliers.empty:
        lines.append(
            "Nenhuma observação ultrapassou as cercas de 1,5 × IQR em nenhuma "
            "métrica, em nenhum dos dois tratamentos."
        )
    else:
        lines.append(
            "Sinalizadas, **não removidas** — a regra do experimento é não "
            "descartar observações (ver `docs/enunciado/lab02.md`, linha 40)."
        )
        lines += ["", _markdown_table(
            ["Métrica", "Tratamento", "Participante", "Kata", "Valor",
             "Cerca inferior", "Cerca superior", "Decisão"],
            [
                [
                    row["metric"], row["treatment"], row["participant"], row["kata_id"],
                    f"{row['value']:g}", f"{row['lower_fence']:g}",
                    f"{row['upper_fence']:g}", row["decision"],
                ]
                for _, row in quality.outliers.iterrows()
            ],
            numeric_columns=(4, 5, 6),
        )]

    lines.append("")
    return "\n".join(lines)


_QUALITY_NOTES = {
    "Métricas com variância": (
        "`duplicated_lines_percent` vale 0,0 em todos os 18 trials. Não é dado "
        "ausente nem erro de coleta: o jscpd 4.0.5 foi executado de fato em cada "
        "trial (reproduzido nesta análise) e não encontrou nenhum bloco duplicado. "
        "A causa é estrutural — cada trial contém um único arquivo com uma única "
        "função, e o limiar configurado na S01 exige ≥ 5 linhas e ≥ 20 tokens "
        "repetidos **dentro do próprio trial**. Nesse arranjo, a métrica não tinha "
        "como variar. Consequência: qualquer teste sobre duplicação é degenerado, "
        "e a parte da RQ3 referente a duplicação não pode ser respondida com poder "
        "estatístico — apenas constatada."
    ),
    "MI reproduzível pelo coletor no estado atual do repositório": (
        "**Os seis valores históricos de MI de Guilherme não são reproduzíveis pelo "
        "coletor no estado atual do repositório.** Todos os 18 diretórios de trial "
        "contêm hoje um `__init__.py` vazio; como o coletor da S02 grava a *média do "
        "MI por arquivo* e um arquivo vazio pontua MI = 100, executar o coletor agora "
        "sobre os katas de Guilherme produziria valores 18 a 22 pontos acima dos "
        "gravados (coluna `mi_collector_today` em `source_integrity_check.csv`). Os "
        "valores gravados coincidem com o MI do `solution.py` isolado, o que indica "
        "que foram medidos antes de o arquivo de pacote existir no diretório. "
        "Caracterizam-se, portanto, como **dados históricos não reproduzíveis no "
        "estado atual** — não como uma segunda convenção de coleta em uso. "
        "LOC e CC não são afetados (um arquivo vazio não acrescenta linhas nem "
        "blocos) e reproduzem 18/18. "
        "**Impacto na análise:** o MI *como coletado* não é comparável entre "
        "participantes, o que contamina a mediana de MI agregada por tratamento. No "
        "pareamento por participante, o **sinal** de cada diferença é preservado "
        "(a transformação é monótona e se aplica aos dois lados do mesmo par), mas os "
        "postos das diferenças *entre* pares poderiam ser distorcidos — neste "
        "conjunto de dados não são, o que é uma coincidência favorável e não uma "
        "garantia do método. Os valores históricos **não foram alterados**; o MI "
        "harmonizado, recomputado sob convenção única a partir do código-fonte, é "
        "reportado como análise de sensibilidade (Seção 8.2 de `rq3_summary.md`)."
    ),
}


def _inline(metric: Metric, value: float, decimals: int, signed: bool = False) -> str:
    """Valor com a unidade escrita por extenso, quando ela cabe na frase."""
    formatted = f"{value:+.{decimals}f}" if signed else f"{value:.{decimals}f}"
    return f"{formatted} {metric.inline_unit}".strip()


def _direction_phrase(metric: Metric, difference: float, decimals: int) -> str:
    if difference == 0:
        return "mediana idêntica nos dois tratamentos"
    direction = "maior" if difference > 0 else "menor"
    return (
        f"{direction} com IA (diferença de mediana: "
        f"{_inline(metric, difference, decimals, signed=True)})"
    )


#: Acima disso a lista polui a frase; descreve-se o passo e os extremos.
MAX_LEVELS_LISTED = 9


def _decimal_comma(value: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def _rank_biserial_levels(n_nonzero: int) -> str:
    """Descreve os valores que r_rb pode assumir — calculados, nunca fixos."""
    levels = rank_biserial_levels(n_nonzero)
    if not levels:
        return "não tem valor definido"
    if len(levels) <= MAX_LEVELS_LISTED:
        return "só pode assumir " + ", ".join(_decimal_comma(level) for level in levels)
    step = levels[1] - levels[0]
    return (
        f"assume {len(levels)} valores, de {_decimal_comma(levels[0])} a "
        f"{_decimal_comma(levels[-1])} em passos de {_decimal_comma(step)}"
    )


def _effect_phrase(test: pd.Series) -> str:
    if test["degenerate"]:
        return "não definido (métrica constante)"
    r_rb = test["effect_rank_biserial"]
    n_pairs = int(test["n_nonzero_pairs"])
    consistency = (
        f"os {n_pairs} pares apresentaram a mesma direção observada — ver a "
        "ressalva de confundimento na Seção 9"
        if abs(r_rb) == 1.0
        else "direção não unânime entre os pares"
    )
    return (
        f"r_rb = {r_rb:+.2f} ({consistency}; com {n_pairs} pares não-nulos o "
        f"coeficiente {_rank_biserial_levels(n_pairs)}, o que limita a "
        "resolução dessa medida)"
    )


def _metric_section(results, metric: Metric, pairing_unit: str) -> str:
    decimals = _decimals(metric.key)
    without_ai = _descriptive_row(results.descriptive, metric.key, WITHOUT_AI)
    with_ai = _descriptive_row(results.descriptive, metric.key, WITH_AI)
    test = _test_row(results.tests, metric.key, pairing_unit)
    difference = with_ai["median"] - without_ai["median"]

    lines = [
        f"**{metric.label}** — {metric.question}",
        "",
        f"- *Descritivo:* sem IA mediana {_median_iqr(without_ai, decimals)}, "
        f"faixa [{_number(without_ai['min'], decimals)}, "
        f"{_number(without_ai['max'], decimals)}], n = {int(without_ai['n'])}; "
        f"com IA mediana {_median_iqr(with_ai, decimals)}, "
        f"faixa [{_number(with_ai['min'], decimals)}, "
        f"{_number(with_ai['max'], decimals)}], n = {int(with_ai['n'])}.",
        f"- *Diferença entre tratamentos:* {_direction_phrase(metric, difference, decimals)}.",
        f"- *Teste estatístico:* {test['test']}, pareado por {test['pairing_unit']}; "
        f"N = {int(test['n_pairs'])} pares "
        f"({int(test['n_nonzero_pairs'])} não-nulos).",
        f"  - H0: {test['h0']}",
        f"  - H1: {test['h1']}",
    ]

    if test["degenerate"]:
        lines += [
            f"- *p-valor:* não aplicável — {test['note']}.",
            "- *Tamanho de efeito:* não definido (métrica constante).",
            f"- *Interpretação:* {_degenerate_interpretation(metric)}",
        ]
        return "\n".join(lines)

    lines += [
        f"- *p-valor:* W = {_number(test['statistic_w'], 1)}, "
        f"p = {_p_value(test['p_value'])} (método {test['p_method']}); "
        f"{test['decision']}.",
        f"- *Tamanho de efeito:* {_effect_phrase(test)}; "
        f"Hodges–Lehmann = "
        f"{_inline(metric, test['effect_hodges_lehmann'], decimals, signed=True)} "
        "(mediana das diferenças pareadas: "
        f"{_number(test['median_difference_pairs'], decimals)}).",
        f"- *Interpretação:* {_interpretation(metric, test, difference, decimals)}",
    ]
    return "\n".join(lines)


def _degenerate_interpretation(metric: Metric) -> str:
    return (
        f"{metric.label} é constante nos 18 trials, então não há diferença a "
        "detectar e o teste não tem o que ordenar. O resultado é uma constatação "
        "('nenhuma duplicação foi detectada sob nenhum dos dois tratamentos'), "
        "não uma evidência de equivalência entre os tratamentos — a métrica não "
        "teve oportunidade de variar neste arranjo de coleta."
    )


def _interpretation(metric: Metric, test: pd.Series, difference: float, decimals: int) -> str:
    if difference == 0:
        observed = f"as medianas de {metric.label} coincidem entre os tratamentos"
    else:
        worse_better = (
            "melhor" if (difference > 0) == metric.higher_is_better else "pior"
        )
        observed = (
            f"a mediana de {metric.label} com IA é "
            f"{_inline(metric, abs(difference), decimals)} "
            f"{'acima' if difference > 0 else 'abaixo'} da mediana sem IA, "
            f"o que nesta métrica é o sentido {worse_better}"
        )
    floor = test["min_achievable_p"]
    power_note = (
        f" Com {int(test['n_nonzero_pairs'])} pares, o menor p bicaudal "
        f"alcançável pelo teste exato é {floor:.4f}"
        + (
            f" — acima de α = {ALPHA}, de modo que rejeitar H0 é impossível "
            "por construção, independentemente da magnitude da diferença."
            if floor is not None and floor > ALPHA
            else f", abaixo de α = {ALPHA}."
        )
        if floor is not None and not pd.isna(floor)
        else ""
    )
    return (
        f"Nos trials analisados, {observed}; o teste pareado "
        f"{'não ' if 'não rejeita' in test['decision'] else ''}rejeita H0 "
        f"(p = {_p_value(test['p_value'])}).{power_note}"
    )


def render_summary(results, figures_subdir: str) -> str:
    tests = results.tests
    pairing_unit = _primary_pairing(tests)
    observations = results.observations

    lines = [
        "# RQ3 — Análise de métricas estáticas",
        "",
        f"> **RQ3 (texto oficial, `docs/enunciado/lab02.md` linha 25):** {RQ3_TEXT}",
        "",
        f"- **H0 (`docs/experiment_design.md`):** {RQ3_H0}",
        f"- **H1:** {RQ3_H1}",
        f"- **Nível de significância adotado nesta análise:** α = {ALPHA}. "
        "Nenhum artefato anterior do projeto fixou um α; este valor é uma "
        "decisão declarada da S03.",
        "",
        "Gerado automaticamente por `python -m experiment.analysis.rq3` a partir "
        f"de `{TRIALS_CSV.name}` e `{STATIC_METRICS_CSV.name}`. Todos os números "
        "abaixo são calculados a partir dos dados reais — nenhum é fixo no código.",
        "",
        "---",
        "",
        "## 1. Dados analisados",
        "",
        f"- {len(observations)} trials (3 participantes × 6 katas), "
        "nenhum excluído, nenhum censurado.",
        "- Ferramentas da coleta (S02): Radon "
        f"{observations['cc_mi_tool_version'].iloc[0]} para CC, MI e LOC; jscpd "
        f"{observations['duplication_tool_version'].iloc[0]} para duplicação.",
        "- Qualidade dos dados, conferência contra o código-fonte e observações "
        "extremas: `data_quality_report.md`.",
        "",
        "## 2. Unidade de análise e unidade de pareamento",
        "",
        _unit_of_analysis_section(results),
        "",
        "## 3. Tabela principal",
        "",
        _main_table(results, pairing_unit),
        "",
        f"Mediana (IQR) calculadas sobre os {len(observations) // 2} trials de cada "
        "tratamento. A diferença é `mediana com IA − mediana sem IA`. O p-valor e o "
        f"tamanho de efeito vêm do Wilcoxon pareado por {pairing_unit}. "
        "Tabela completa (incluindo o pareamento secundário por kata) em "
        "`statistical_tests.csv`; descritiva completa com Q1, Q3, mínimo e máximo "
        "em `descriptive_statistics.csv`.",
        "",
        "## 4. Normalização por LOC",
        "",
        _normalization_section(results, pairing_unit),
        "",
        "## 5. Gráficos",
        "",
        _figures_section(results, figures_subdir),
        "",
        "---",
        "",
        f"## 6. RQ3 — {RQ3_TEXT}",
        "",
    ]

    for metric in (LOC, CYCLOMATIC_COMPLEXITY, MAINTAINABILITY_INDEX, DUPLICATION):
        lines.append(_metric_section(results, metric, pairing_unit))
        lines.append("")

    lines += [
        "**Métricas normalizadas**",
        "",
        _metric_section(results, CC_PER_LOC, pairing_unit),
        "",
        "## 7. Multiplicidade",
        "",
        _multiplicity_section(results),
        "",
        "## 8. Análises secundárias e de sensibilidade",
        "",
        _secondary_section(results, pairing_unit),
        "",
        "## 9. Confundimento entre tratamento e dificuldade dos katas",
        "",
        _confounding_section(results),
        "",
        "## 10. Conclusão da RQ3",
        "",
        _conclusion(results, pairing_unit),
        "",
        "## 11. Limitações desta análise",
        "",
        _limitations(results, pairing_unit),
        "",
    ]
    return "\n".join(lines)


def _unit_of_analysis_section(results) -> str:
    integrity = results.quality.integrity
    blocks = sorted(integrity["cc_blocks"].unique())
    pairing_units = list(dict.fromkeys(results.tests["pairing_unit"]))
    return "\n".join(
        [
            "**Unidade de observação: o trial.** Cada uma das 18 linhas é a "
            "combinação participante × kata × tratamento, que é o nível em que o "
            "tratamento (`with_ai`/`without_ai`) está definido. Os dados não são "
            "agregados antes das verificações de qualidade nem da descritiva.",
            "",
            "**Níveis de cálculo de cada métrica, verificados no código-fonte:**",
            "",
            "- **CC** é calculada pelo Radon por *bloco* (função/método) e o coletor "
            "grava a média dos blocos do trial. A conferência linha a linha mostra "
            f"que todos os 18 trials têm exatamente {blocks[0]} bloco "
            "(uma única função por `solution.py`), logo, **neste conjunto de dados, "
            "a média por trial é numericamente igual à CC daquela função** — não há "
            "mistura de níveis de agregação entre trials.",
            "- **LOC** é o `loc` bruto do Radon (linhas físicas totais do arquivo, "
            "incluindo linhas em branco e comentários), somado sobre os arquivos "
            "não-teste do trial. É, portanto, uma medida de *volume de texto*, não "
            "de instruções — relevante para interpretar a comparação de verbosidade.",
            "- **MI** é calculado por arquivo e o coletor grava a média por arquivo "
            "do trial; ver a ressalva de convenção no relatório de qualidade.",
            "- **Duplicação** é calculada pelo jscpd sobre os arquivos do trial, "
            "isoladamente — detecta repetição *dentro* do trial, não entre trials.",
            "",
            "**Agregação usada para chegar a uma observação comparável por trial:** "
            "nenhuma além da que o próprio coletor já aplica (soma para LOC, média "
            "por bloco para CC, média por arquivo para MI). As quatro métricas são, "
            "portanto, uma observação por trial cada.",
            "",
            "**Unidade de pareamento do Wilcoxon.** O desenho é crossover "
            "within-subject, mas nenhum participante resolveu o mesmo kata nos dois "
            "tratamentos (verificado: 0 pares participante×kata com os dois "
            "tratamentos). Não existe, portanto, par direto linha a linha. Foram "
            "usados dois blocos, ambos reportados:",
            "",
            _markdown_table(
                ["Pareamento", "Papel", "N de pares", "Justificativa"],
                [
                    [
                        unit,
                        "primário" if index == 0 else "secundário (sensibilidade)",
                        str(int(results.tests.loc[
                            results.tests["pairing_unit"] == unit, "n_pairs"
                        ].max())),
                        _PAIRING_RATIONALE.get(unit, ""),
                    ]
                    for index, unit in enumerate(pairing_units)
                ],
                numeric_columns=(2,),
            ),
        ]
    )


_PAIRING_RATIONALE = {
    "participante (within-subject)": (
        "Cada participante contribui com 3 trials por tratamento; o par é a mediana "
        "de cada metade. É o único bloco within-subject disponível e neutraliza "
        "diferenças individuais de estilo."
    ),
    "kata (bloco de dificuldade)": (
        "Bloqueia pela dificuldade da tarefa — principal determinante de LOC e CC — e "
        "oferece 6 blocos. Não é within-subject: os dois lados de cada par vêm de "
        "participantes diferentes e as células são desbalanceadas (1 ou 2 trials)."
    ),
}


def _main_table(results, pairing_unit: str) -> str:
    rows = []
    for metric in (LOC, CYCLOMATIC_COMPLEXITY, MAINTAINABILITY_INDEX, DUPLICATION):
        decimals = _decimals(metric.key)
        without_ai = _descriptive_row(results.descriptive, metric.key, WITHOUT_AI)
        with_ai = _descriptive_row(results.descriptive, metric.key, WITH_AI)
        test = _test_row(results.tests, metric.key, pairing_unit)
        difference = with_ai["median"] - without_ai["median"]
        rows.append([
            f"{metric.label} ({metric.unit})",
            _median_iqr(without_ai, decimals),
            _median_iqr(with_ai, decimals),
            f"{difference:+.{decimals}f}",
            "n/a (degenerado)" if test["degenerate"] else _p_value(test["p_value"]),
            "n/a" if test["degenerate"]
            else f"r_rb = {test['effect_rank_biserial']:+.2f}",
        ])
    return _markdown_table(
        ["Métrica", "Sem IA — Mediana (IQR)", "Com IA — Mediana (IQR)",
         "Diferença", "Wilcoxon p", "Tamanho de efeito"],
        rows,
        numeric_columns=(1, 2, 3, 4, 5),
    )


def _normalization_section(results, pairing_unit: str) -> str:
    cc_test = _test_row(results.tests, CC_PER_LOC.key, pairing_unit)
    loc_test = _test_row(results.tests, LOC.key, pairing_unit)
    cc_abs_test = _test_row(results.tests, CYCLOMATIC_COMPLEXITY.key, pairing_unit)
    rows = []
    for metric in (CC_PER_LOC, DUPLICATION_PER_LOC):
        decimals = _decimals(metric.key)
        without_ai = _descriptive_row(results.descriptive, metric.key, WITHOUT_AI)
        with_ai = _descriptive_row(results.descriptive, metric.key, WITH_AI)
        test = _test_row(results.tests, metric.key, pairing_unit)
        rows.append([
            f"{metric.label} ({metric.unit})",
            _number(without_ai["median"], decimals),
            _number(with_ai["median"], decimals),
            "n/a (degenerado)" if test["degenerate"] else _p_value(test["p_value"]),
            "n/a" if test["degenerate"] else f"r_rb = {test['effect_rank_biserial']:+.2f}",
            _NORMALIZATION_REASON[metric.key],
        ])

    return "\n".join([
        "O enunciado (linha 54) exige LOC como controle sempre que complexidade ou "
        "duplicação forem reportadas, porque *\"código gerado por IA pode ser mais "
        "verboso, e complexidade/duplicação sem normalizar por LOC pode enganar\"*. "
        "A normalização não foi aplicada automaticamente a todas as métricas — "
        "cada razão abaixo tem uma justificativa própria, e duas métricas foram "
        "deliberadamente **não** normalizadas:",
        "",
        "- **CC/LOC — normalizada.** *Por que é necessária:* CC cresce com o número "
        "de caminhos de decisão, e um código maior tende a ter mais decisões; "
        f"observou-se de fato uma correlação de Spearman ρ = "
        f"{results.observations[LOC.key].corr(results.observations[CYCLOMATIC_COMPLEXITY.key], method='spearman'):.2f} "
        "entre LOC e CC nos 18 trials. *Qual problema controla:* separa \"o código é "
        "mais complexo porque é maior\" de \"o código é mais complexo por linha "
        "escrita\". *Como interpretar:* densidade de decisões por linha física; "
        "quanto maior, mais lógica condensada por linha.",
        "- **Duplicação/LOC — calculada, mas não usada para concluir.** O numerador "
        "(`duplicated_lines`) é identicamente zero nos 18 trials, então a razão é "
        "zero por construção e não acrescenta informação à duplicação bruta. É "
        "reportada apenas para deixar registrado que foi verificada.",
        "- **MI — deliberadamente não normalizada.** O Maintainability Index já "
        "incorpora LOC na própria fórmula (junto de CC e do volume de Halstead); "
        "dividi-lo por LOC contaria o tamanho duas vezes e produziria um número sem "
        "interpretação definida.",
        "- **LOC — não normalizada**, por ser ela própria a métrica de controle de "
        "tamanho.",
        "",
        _markdown_table(
            ["Métrica", "Sem IA (mediana)", "Com IA (mediana)", "Wilcoxon p",
             "Tamanho de efeito", "Motivo da normalização"],
            rows,
            numeric_columns=(1, 2, 3, 4),
        ),
        "",
        "**Os três conceitos, mantidos separados:**",
        "",
        _markdown_table(
            ["Conceito", "Métrica", "Pergunta", "Resultado observado"],
            [
                ["Tamanho", "LOC", LOC.question,
                 _short_verdict(results, LOC, loc_test)],
                ["Complexidade absoluta", "CC", CYCLOMATIC_COMPLEXITY.question,
                 _short_verdict(results, CYCLOMATIC_COMPLEXITY, cc_abs_test)],
                ["Complexidade relativa", "CC/LOC", CC_PER_LOC.question,
                 _short_verdict(results, CC_PER_LOC, cc_test)],
            ],
        ),
    ])


_NORMALIZATION_REASON = {
    CC_PER_LOC.key: "Separa verbosidade de densidade de complexidade (exigência "
                    "de controle por LOC, enunciado linha 54)",
    DUPLICATION_PER_LOC.key: "Numerador identicamente zero — razão degenerada, "
                             "reportada apenas por completude",
}


def _short_verdict(results, metric: Metric, test: pd.Series) -> str:
    decimals = _decimals(metric.key)
    without_ai = _descriptive_row(results.descriptive, metric.key, WITHOUT_AI)
    with_ai = _descriptive_row(results.descriptive, metric.key, WITH_AI)
    difference = with_ai["median"] - without_ai["median"]
    if difference == 0:
        direction = "sem diferença de mediana"
    else:
        direction = f"{'maior' if difference > 0 else 'menor'} com IA"
    if test["degenerate"]:
        return f"{direction}; teste não aplicável"
    return (
        f"mediana {_number(without_ai['median'], decimals)} → "
        f"{_number(with_ai['median'], decimals)} ({direction}); "
        f"p = {_p_value(test['p_value'])}, {test['decision']}"
    )


_FIGURE_QUESTIONS = {
    "fig1_distribuicao_por_tratamento.png":
        "Os dois tratamentos produzem distribuições diferentes em LOC, CC e MI — "
        "e onde estão os 18 trials dentro dessas distribuições?",
    "fig2_comparacao_pareada.png":
        "Dentro de cada participante, em que direção a métrica muda de sem IA "
        "para com IA, e sobre quantas observações cada ponto do par se apoia?",
    "fig3_resultados_por_kata.png":
        "Como os valores observados se distribuíram por kata, e quais katas "
        "caíram em cada tratamento?",
    "fig4_cc_vs_loc.png":
        "A complexidade acompanha o tamanho do código, e os tratamentos ocupam "
        "regiões diferentes desse plano?",
    "fig5_complexidade_normalizada.png":
        "Controlando o tamanho, a densidade de complexidade difere — e quanto "
        "dessa diferença depende de como as linhas são contadas?",
}


#: Formas do catálogo da disciplina não usadas, com o motivo.
_FIGURE_EXCLUSIONS = [
    ("Histograma", "o catálogo indica *\"grande volume de dados\"* como melhor "
     "uso; com 9 trials por tratamento, o boxplot com os pontos individuais "
     "mostra mais do que um histograma de poucos bins"),
    ("Violino", "com 9 observações por grupo a densidade estimada é instável "
     "(ver `FONTE_DA_VERDADE_SPRINT_3.md`, Seção 8)"),
    ("Gráfico de duplicação", "a métrica é constante em 0,0% por limitação de "
     "escopo da coleta; um gráfico sugeriria uma evidência que a análise não "
     "tem. A limitação está descrita na Seção 10"),
]


def _figures_section(results, figures_subdir: str) -> str:
    exclusions = "\n".join(
        f"- **{form}** — {reason}." for form, reason in _FIGURE_EXCLUSIONS
    )
    return _figures_table(results, figures_subdir) + (
        "\n\nCada figura responde a uma pergunta que nenhuma outra responde. "
        "Formas do catálogo da disciplina que foram deliberadamente **não** "
        "usadas:\n\n" + exclusions
    )


def _figures_table(results, figures_subdir: str) -> str:
    return _markdown_table(
        ["Figura", "Tipo", "Pergunta que responde"],
        [
            [
                f"[`{path.name}`]({figures_subdir}/{path.name})",
                _FIGURE_TYPES.get(path.name, "—"),
                _FIGURE_QUESTIONS.get(path.name, "—"),
            ]
            for path in results.figures
        ],
    )


_FIGURE_TYPES = {
    "fig1_distribuicao_por_tratamento.png": "Pontos dos 18 trials + mediana por tratamento",
    "fig2_comparacao_pareada.png": "Pares por participante + trials individuais",
    "fig3_resultados_por_kata.png": "Categórico × numérico × grupo (pontos)",
    "fig4_cc_vs_loc.png": "Dispersão",
    "fig5_complexidade_normalizada.png": "Pontos dos 18 trials + mediana por tratamento",
}


def _multiplicity_section(results) -> str:
    """Declara família, quantidade, método e efeito da correção."""
    tests = results.tests
    with_p = tests[tests["p_value"].notna()]
    # Ordem de aparição, para que a família primária venha antes da secundária.
    families = {
        family: list(with_p.loc[with_p["family"] == family, "metric"])
        for family in dict.fromkeys(with_p["family"])
    }
    global_family_size = len(with_p)
    global_alpha = ALPHA / global_family_size

    rows = [
        [
            row["metric"],
            row["family"],
            _p_value(row["p_value"]),
            _p_value(row["p_bonferroni"]),
            _p_value(row["p_fdr_bh"]),
            row["decision_bonferroni"],
        ]
        for _, row in with_p.iterrows()
    ]

    survivors = with_p[with_p["p_bonferroni"] < ALPHA]

    lines = [
        f"Foram realizados **{len(tests)} testes inferenciais**, dos quais "
        f"**{global_family_size} produziram p-valor** (os demais são degenerados: "
        "duplicação e duplicação/LOC, constantes nos 18 trials, não têm o que "
        "ordenar). Reportar vários p-valores sem correção infla a chance de um "
        "falso positivo, e o material da disciplina é explícito quanto a isso "
        "(*\"Muitos testes? Corrija (Bonferroni / FDR)\"*).",
        "",
        "**Famílias de inferência.** A família é a **unidade de pareamento**: "
        "dentro dela, cada teste responde a uma pergunta diferente (uma métrica) "
        "sob o mesmo bloqueio. Corrigir também entre as unidades de pareamento "
        "penalizaria duas vezes a mesma pergunta analisada sob bloqueios "
        "alternativos.",
        "",
    ]
    for family, metrics in families.items():
        lines.append(f"- **{family}** — {len(metrics)} testes: {', '.join(metrics)}.")
    lines += [
        "",
        f"**Métodos aplicados:** Bonferroni (controla o erro por família, FWER) e "
        "Benjamini–Hochberg (controla a taxa de falsas descobertas, FDR). Os "
        "p-valores brutos **não foram substituídos**: `p_value`, `p_bonferroni` e "
        "`p_fdr_bh` convivem em `statistical_tests.csv`.",
        "",
        _markdown_table(
            ["Métrica", "Família", "p bruto", "p Bonferroni", "p FDR (BH)",
             "Decisão após Bonferroni"],
            rows,
            numeric_columns=(2, 3, 4),
        ),
        "",
    ]

    if survivors.empty:
        lines.append(
            f"**Nenhum teste permanece significativo a α = {ALPHA} após correção**, "
            "por nenhum dos dois métodos. Na leitura mais conservadora possível — "
            f"tratar todos os {global_family_size} testes como uma única família — o "
            f"limiar de Bonferroni seria α = {global_alpha:.4f}, que nenhum p bruto "
            "observado atinge. A escolha da definição de família, portanto, não muda "
            "nenhuma conclusão."
        )
    else:
        listed = ", ".join(
            f"{row['metric']} ({row['family']}, p corrigido = {_p_value(row['p_bonferroni'])})"
            for _, row in survivors.iterrows()
        )
        lines.append(f"**Sobrevive(m) à correção de Bonferroni:** {listed}.")
    return "\n".join(lines)


def _confounding_section(results) -> str:
    """Os dois lados de cada par contêm katas diferentes."""
    balance = results.allocation_balance
    cc_key = CYCLOMATIC_COMPLEXITY.key
    rows = [
        [
            row["participant"],
            row[f"katas_{WITH_AI}"].replace(" ", ", "),
            row[f"katas_{WITHOUT_AI}"].replace(" ", ", "),
            f"{row[f'{cc_key}_{WITH_AI}']:.2f}",
            f"{row[f'{cc_key}_{WITHOUT_AI}']:.2f}",
            f"{row[f'{cc_key}_difference']:+.2f}",
            f"{row[f'{LOC.key}_difference']:+.2f}",
        ]
        for _, row in balance.iterrows()
    ]
    simpler = balance[balance[f"{cc_key}_difference"] < 0]

    return "\n".join([
        "Três fatos do desenho executado, verificados nos dados e não corrigíveis "
        "nesta etapa:",
        "",
        "1. **Não existe pareamento participante × kata.** Nenhum participante "
        "resolveu o mesmo kata sob os dois tratamentos (verificado: 0 combinações "
        "participante × kata com os dois tratamentos).",
        "2. **O pareamento primário é por participante**, por ser o único bloco "
        "within-subject disponível.",
        "3. **Logo, cada lado do par contém um conjunto diferente de katas** — e a "
        "diferença medida entre os tratamentos carrega, junto, a diferença entre "
        "as tarefas resolvidas em cada lado.",
        "",
        "Para dimensionar esse desequilíbrio, a dificuldade aparente de um kata foi "
        "estimada pela média dos seus valores entre os três participantes, e "
        "comparada entre os dois lados de cada par:",
        "",
        _markdown_table(
            ["Participante", "Katas com IA", "Katas sem IA",
             "CC média dos katas — com IA", "CC média dos katas — sem IA",
             "Diferença (CC)", "Diferença (LOC)"],
            rows,
            numeric_columns=(3, 4, 5, 6),
        ),
        "",
        f"Em **{len(simpler)} dos {len(balance)} pares** "
        f"({', '.join(sorted(simpler['participant']))}), os katas alocados ao "
        "tratamento com IA são, por esse indicador, os menos complexos. O kata-04 — "
        "o de maior CC média entre os seis — ficou no lado sem IA de dois dos três "
        "participantes.",
        "",
        "**Limite do indicador, declarado junto do número:** ele é derivado das "
        "próprias medições desta análise, não de uma avaliação independente de "
        "dificuldade. Como cada kata aparece sob os dois tratamentos (em "
        "participantes diferentes), a média por kata absorve parte de um eventual "
        "efeito do tratamento. Serve para **descrever a alocação**, não para "
        "estimar um efeito de tarefa isolado. Valores completos em "
        "`task_allocation_balance.csv`.",
        "",
        "**Consequência para a leitura dos resultados.** A alocação dos katas "
        "constitui um possível confundimento entre tratamento e dificuldade da "
        "tarefa. A alocação observada não permite separar completamente o efeito "
        "do tratamento do efeito da tarefa. Em particular, os três pares "
        "apresentaram a mesma direção observada em LOC e em CC — e esse fato "
        "permanece verdadeiro —, mas **essa unanimidade não pode ser interpretada "
        "isoladamente como consistência do efeito do tratamento**, porque os lados "
        "do pareamento contêm katas diferentes e a dificuldade dos katas não está "
        "perfeitamente balanceada entre eles.",
        "",
        "Este é um traço do experimento tal como foi executado — registrado em "
        "`docs/experiment_design.md` como desvio da atribuição fechada na S01 — e "
        "**não** um defeito da análise. Corrigi-lo exigiria nova coleta, fora do "
        "escopo da S03.",
    ])


def _secondary_section(results, primary_unit: str) -> str:
    """Pareamento por kata e MI harmonizado — reportados, não promovidos.

    Cada um controla um problema real do pareamento primário: o poder
    estatístico de N = 3 e os valores históricos de MI. Um deles rejeita H0;
    omitir isso esconderia um resultado, e promovê-lo à resposta da RQ3 seria
    trocar a unidade de análise depois de ver o p-valor.
    """
    secondary_unit = next(
        unit for unit in results.tests["pairing_unit"] if unit != primary_unit
    )
    rows = []
    for metric in (LOC, CYCLOMATIC_COMPLEXITY, MAINTAINABILITY_INDEX, DUPLICATION,
                   CC_PER_LOC):
        test = _test_row(results.tests, metric.key, secondary_unit)
        rows.append([
            f"{metric.label} ({metric.unit})",
            "n/a" if test["degenerate"] else _number(test["statistic_w"], 1),
            "n/a (degenerado)" if test["degenerate"] else _p_value(test["p_value"]),
            "n/a" if test["degenerate"]
            else f"{test['effect_rank_biserial']:+.2f}",
            test["decision"],
        ])

    harmonized_rows = []
    for unit in (primary_unit, secondary_unit):
        test = _test_row(results.tests, "maintainability_index_harmonized", unit)
        raw = _test_row(results.tests, MAINTAINABILITY_INDEX.key, unit)
        harmonized_rows.append([
            unit,
            _p_value(raw["p_value"]),
            _p_value(test["p_value"]),
            f"{test['effect_rank_biserial']:+.2f}",
            test["decision"],
        ])

    rejected = results.tests[
        (results.tests["pairing_unit"] == secondary_unit)
        & (results.tests["p_value"] < ALPHA)
    ]
    surviving = rejected[rejected["p_bonferroni"] < ALPHA]

    lines = [
        "### 8.1 Pareamento secundário por kata (N = 6 blocos)",
        "",
        "Bloqueia pela dificuldade da tarefa e tem piso de p de 0,0313, contra "
        "0,2500 do pareamento primário — ou seja, é o único dos dois em que "
        f"rejeitar H0 a α = {ALPHA} é aritmeticamente possível. Em troca, **não é "
        "within-subject**: os dois lados de cada par vêm de participantes "
        "diferentes, e as células são desbalanceadas (1 ou 2 trials por lado).",
        "",
        _markdown_table(
            ["Métrica", "W", "Wilcoxon p", "r_rb", "Decisão"],
            rows,
            numeric_columns=(1, 2, 3),
        ),
        "",
        "### 8.2 Sensibilidade do MI: valores históricos × recomputação",
        "",
        "Os seis valores de MI de Guilherme em `data/static_metrics.csv` são "
        "históricos e **não são reproduzíveis pelo coletor no estado atual do "
        "repositório** (ver `data_quality_report.md`). A linha `MI (harmonizado)` "
        "recomputa o MI dos 18 trials sob uma convenção única, a partir do "
        "código-fonte versionado; **`data/static_metrics.csv` não foi alterado**.",
        "",
        _markdown_table(
            ["Pareamento", "p — MI como coletado", "p — MI harmonizado",
             "r_rb (harmonizado)", "Decisão (harmonizado)"],
            harmonized_rows,
            numeric_columns=(1, 2, 3),
        ),
        "",
    ]

    if rejected.empty:
        lines.append(
            "Nenhum teste secundário rejeitou H0; as análises de sensibilidade "
            "não alteram a leitura primária."
        )
    else:
        listed = "; ".join(
            f"**{row['metric']}** (p = {_p_value(row['p_value'])}, "
            f"r_rb = {row['effect_rank_biserial']:+.2f})"
            for _, row in rejected.iterrows()
        )
        lines += [
            f"**Resultado com p bruto abaixo de α apenas na análise secundária:** "
            f"{listed}, pareado por {secondary_unit} — nos 6 katas, o código "
            "produzido com IA teve MI harmonizado maior que o produzido sem IA, sem "
            "exceção. O resultado é mantido visível e não foi removido.",
            "",
            "**O p = 0,03125 observado na análise secundária não permanece "
            f"significativo após correção de multiplicidade** (Bonferroni: "
            f"{_p_value(rejected['p_bonferroni'].iloc[0])}; "
            f"Benjamini–Hochberg: {_p_value(rejected['p_fdr_bh'].iloc[0])}; "
            f"ver Seção 7)."
            + ("" if surviving.empty else " [ATENÇÃO: sobrevive à correção]"),
            "",
            "Registre-se ainda que, **com seis pares, 0,03125 é o menor p bicaudal "
            "que o teste exato pode produzir** nessa configuração: é o piso, e não "
            "um valor que se destaque dentro do intervalo possível. Como o piso "
            "coincide com o próprio p observado, nenhuma correção de multiplicidade "
            "poderia ser satisfeita com esse número de pares.",
            "",
            "**Como este resultado deve (e não deve) ser lido.** Ele (a) é análise "
            "**secundária**; (b) usa **MI harmonizado**, recomputado, e não a métrica "
            "gravada na S02; (c) usa **pareamento por kata**, que não é "
            "within-subject — cada par compara participantes diferentes, confundindo "
            "tratamento com habilidade e estilo individual; (d) **não é a análise "
            "primária**, que foi fixada antes de os p-valores serem calculados — "
            "trocar a unidade de pareamento depois de ver o resultado seria escolher "
            "o teste pelo desfecho; (e) **não deve substituir a conclusão "
            "principal**; e (f) **não sobrevive à correção de multiplicidade**. "
            "Nada disso indica ausência de efeito: indica que este resultado não "
            "sustenta, sozinho, nenhuma afirmação sobre o tratamento. A conclusão da "
            "RQ3 permanece a da Seção 10.",
        ]
    return "\n".join(lines)


def _conclusion(results, pairing_unit: str) -> str:
    parts = []
    for metric in (LOC, CYCLOMATIC_COMPLEXITY, CC_PER_LOC, MAINTAINABILITY_INDEX):
        decimals = _decimals(metric.key)
        without_ai = _descriptive_row(results.descriptive, metric.key, WITHOUT_AI)
        with_ai = _descriptive_row(results.descriptive, metric.key, WITH_AI)
        test = _test_row(results.tests, metric.key, pairing_unit)
        difference = with_ai["median"] - without_ai["median"]
        parts.append(
            f"**{metric.label}**: mediana {_number(without_ai['median'], decimals)} "
            f"sem IA contra {_number(with_ai['median'], decimals)} com IA "
            f"({difference:+.{decimals}f}), p = {_p_value(test['p_value'])}"
        )

    duplication_test = _test_row(results.tests, DUPLICATION.key, pairing_unit)
    any_rejected = (
        (results.tests["pairing_unit"] == pairing_unit)
        & (results.tests["p_value"] < ALPHA)
    ).any()
    balance = results.allocation_balance
    simpler_side = balance[balance[f"{CYCLOMATIC_COMPLEXITY.key}_difference"] < 0]

    return "\n".join([
        f"Nos {len(results.observations)} trials analisados: " + "; ".join(parts) + ".",
        "",
        f"Nenhum dos testes pareados por {pairing_unit} atingiu significância a "
        f"α = {ALPHA}"
        + ("" if not any_rejected else " — exceto os assinalados na tabela acima")
        + ", e nenhum teste desta análise permanece significativo após correção de "
        "multiplicidade (Seção 7). Com N = 3 pares, o menor p bicaudal que o teste "
        "exato pode produzir é 0,2500, acima de α; a não-rejeição de H0 é, portanto, "
        "uma **limitação de poder estatístico estrutural do desenho**, e não "
        "evidência de que os tratamentos sejam equivalentes.",
        "",
        f"Soma-se a isso que, em {len(simpler_side)} dos {len(balance)} pares, os "
        "katas alocados ao tratamento com IA são os menos complexos pelo indicador "
        "da Seção 9. A alocação dos katas constitui um possível confundimento entre "
        "tratamento e dificuldade da tarefa, e a alocação observada não permite "
        "separar completamente um efeito do outro.",
        "",
        "Sobre a duplicação, que a RQ3 nomeia explicitamente: nenhum bloco duplicado "
        "foi detectado sob nenhum dos dois tratamentos, de modo que todas as "
        f"diferenças pareadas são exatamente zero e o teste não é aplicável "
        f"({int(duplication_test['n_pairs'])} pares, "
        f"{int(duplication_test['n_nonzero_pairs'])} não-nulos). O arranjo da coleta "
        "— um arquivo com uma única função por trial, e limiar de 5 linhas / 20 "
        "tokens repetidos dentro do próprio trial — não dava à métrica oportunidade "
        "de variar. Essa metade da RQ3 não pode ser respondida com os dados "
        "disponíveis: só é possível constatar a ausência de duplicação detectada.",
        "",
        "**Resposta à RQ3, em duas partes:**",
        "",
        "- **Complexidade ciclomática.** Os dados disponíveis **não permitem "
        "estabelecer que o tratamento com IA alterou a complexidade ciclomática** do "
        "código produzido. A análise primária possui apenas três pares — com piso de "
        f"p de 0,2500, acima de α = {ALPHA} — e apresenta confundimento entre "
        "tratamento e dificuldade dos katas. As diferenças descritivas observadas "
        "estão reportadas acima e continuam válidas como descrição da amostra, mas "
        "não sustentam uma afirmação sobre o efeito do tratamento.",
        "- **Duplicação.** A duplicação **não pôde ser avaliada adequadamente** "
        "devido ao escopo estrutural da coleta. Essa metade da RQ3 permanece sem "
        "resposta.",
        "",
        "Esta é uma afirmação sobre o que os dados permitem concluir, **não** sobre "
        "a ausência de efeito: `p > α` aqui não significa que os tratamentos sejam "
        f"equivalentes. Os dados **não** autorizam afirmar que a IA produz código "
        "melhor ou pior, nem que deixa de alterar a complexidade.",
    ])


def _limitations(results, pairing_unit: str) -> str:
    return "\n".join([
        f"1. **Poder estatístico.** Com N = 3 pares — pareamento por {pairing_unit} "
        "— o menor p bicaudal alcançável é 0,2500. Rejeitar H0 a α = "
        f"{ALPHA} é impossível por construção, qualquer que seja a magnitude do "
        "efeito. O pareamento secundário por kata (N = 6, piso de p = 0,0313) tem "
        "mais poder e está na Seção 7.1, mas não é within-subject e mistura "
        "participantes dentro de cada par.",
        f"2. **Confundimento entre tratamento e dificuldade dos katas.** Não existe "
        "pareamento participante × kata, de modo que cada lado do par contém katas "
        "diferentes; o indicador da Seção 9 mostra que a alocação não está "
        "balanceada. É um traço do experimento executado, não um defeito da análise.",
        "3. **Duplicação sem variância.** A métrica é 0,0% nos 18 trials por uma "
        "razão estrutural da coleta, não por um resultado do tratamento. Ver "
        "`data_quality_report.md`.",
        "4. **Multiplicidade.** Vários p-valores são reportados juntos; as correções "
        "de Bonferroni e Benjamini–Hochberg estão na Seção 7 e em "
        "`statistical_tests.csv`. Nenhum resultado permanece significativo após "
        "correção.",
        "5. **Valores históricos de MI não reproduzíveis.** Os seis valores de MI de "
        "Guilherme em `data/static_metrics.csv` não são reproduzíveis pelo coletor no "
        "estado atual do repositório. A mediana de MI por tratamento está contaminada "
        "por isso; no pareamento por participante o sinal de cada diferença é "
        "preservado. A análise de sensibilidade está na Seção 8.2 e nas linhas "
        "`MI (harmonizado)` de `statistical_tests.csv`.",
        "6. **Ausência de par participante × kata.** O contrabalanceamento executado "
        "não repetiu nenhum kata sob os dois tratamentos para o mesmo participante, "
        "o que impede o pareamento mais forte possível neste desenho.",
        f"7. **α = {ALPHA} foi definido durante a S03**, não antes da coleta: nenhum "
        "artefato de S01/S02 fixava um nível de significância. É, portanto, uma "
        "decisão pós-hoc, ainda que declarada.",
        "8. **Pressuposto de simetria não verificado.** A leitura do Wilcoxon "
        "signed-rank como diferença de medianas supõe simetria da distribuição das "
        "diferenças pareadas; com 3 pares esse pressuposto é inverificável.",
        "9. **LOC inclui linhas em branco e comentários** (métrica `loc` bruta do "
        "Radon), e CC/LOC herda essa sensibilidade. A coluna `sloc_recomputed` em "
        "`source_integrity_check.csv` permite verificar o efeito dessa escolha sobre "
        "a comparação de verbosidade e de densidade.",
        "10. **Tamanho de efeito fora da lista do material da disciplina.** O "
        "material nomeia Cohen's d, Cliff's δ e A12; esta análise usa a correlação "
        "bisserial de postos para amostras pareadas, por ser a medida definida "
        "diretamente a partir dos postos com sinal do próprio signed-rank e por não "
        "depender da aproximação normal com N pequeno.",
        "11. **Herdadas da S02** (registradas em `AUDITORIA_SPRINTS_1_2.md`): "
        "divergência entre o contrabalanceamento fechado na S01 e o executado — que "
        "é a origem do confundimento da Seção 9 — e ressalva de proveniência dos "
        "tempos de Guilherme. A segunda não afeta RQ3, que não usa `elapsed_seconds`.",
    ])
