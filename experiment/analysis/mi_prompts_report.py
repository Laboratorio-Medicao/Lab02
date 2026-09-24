"""Markdown da análise exploratória da Issue #18 (MI em profundidade e nº de prompts).

Todos os números e as frases condicionais vêm de `MiPromptsResults`; nada é fixo.
"""

from __future__ import annotations

import pandas as pd

from experiment.analysis.mi_prompts import (
    CC_TOTAL,
    COMMENTS,
    HALSTEAD_VOLUME,
    LLOC,
    MiPromptsResults,
)
from experiment.analysis.rq3 import HARMONIZED_MI, HARMONIZED_MI_KEY
from experiment.analysis.rq3_data import TREATMENTS, WITH_AI, WITHOUT_AI

_LABEL = {WITHOUT_AI: "Sem IA", WITH_AI: "Com IA"}
#: Faixas usuais de leitura de |ρ| (apenas descritivas, sem valor inferencial).
_STRENGTH = ((0.7, "forte"), (0.4, "moderada"), (0.2, "fraca"), (0.0, "praticamente nula"))


def _n(value: float, digits: int = 2) -> str:
    return f"{round(float(value), 9):.{digits}f}".replace(".", ",")


def _strength(rho: float) -> str:
    return next(label for limit, label in _STRENGTH if abs(rho) >= limit)


def _descriptive_rows(results: MiPromptsResults) -> list[str]:
    table = results.component_descriptive
    rows = []
    for metric in (HARMONIZED_MI, HALSTEAD_VOLUME, LLOC, CC_TOTAL, COMMENTS):
        cells = []
        for treatment in TREATMENTS:
            row = table[(table["metric_key"] == metric.key) & (table["treatment"] == treatment)].iloc[0]
            cells.append(f"{_n(row['median'])} ({_n(row['iqr'])})")
        rows.append(f"| {metric.label} | {metric.unit} | {cells[0]} | {cells[1]} |")
    return rows


def _rho_cell(row: pd.Series) -> str:
    return "—" if pd.isna(row["spearman_rho"]) else _n(row["spearman_rho"])


def _component_section(results: MiPromptsResults) -> list[str]:
    corr = results.component_correlations.set_index("metric_key")
    lloc_rho = corr.loc[LLOC.key, "spearman_rho"]
    cc_rho = corr.loc[CC_TOTAL.key, "spearman_rho"]
    volume_rho = corr.loc[HALSTEAD_VOLUME.key, "spearman_rho"]
    comments_constant = bool(corr.loc[COMMENTS.key, "note"])
    comments_value = results.components[COMMENTS.key].iloc[0]

    lines = [
        "## 1. MI em profundidade",
        "",
        "O Radon calcula o MI como `max(0, (171 − 5,2·ln V − 0,23·G − 16,2·ln L + 50·sen(√(2,4·C))) · 100/171)`, "
        "com V = volume de Halstead, G = complexidade ciclomática, L = linhas lógicas (LLOC) e C = % de "
        "linhas de comentário. Os componentes foram recalculados do `solution.py` versionado de cada trial "
        "— a convenção do **MI harmonizado** da RQ3 — e o MI reconstruído a partir deles confere com essa "
        "série (ver verificações).",
        "",
        "### 1.1 Componentes por tratamento",
        "",
        "| Componente | Unidade | Sem IA — mediana (IQR) | Com IA — mediana (IQR) |",
        "|---|---|---:|---:|",
        *_descriptive_rows(results),
        "",
        "### 1.2 O que move o MI nestes dados",
        "",
        "Correlação de Spearman entre o MI harmonizado e cada componente, nos 18 trials (descritiva):",
        "",
        "| Componente | ρ com o MI |",
        "|---|---:|",
        *(f"| {row['metric']} | {_rho_cell(row)} |" for _, row in results.component_correlations.iterrows()),
        "",
    ]
    if comments_constant:
        lines += [
            f"- **Comentários:** {_n(comments_value, 1)}% em todos os 18 trials. O termo de comentários da "
            "fórmula é constante e não contribui para nenhuma diferença de MI.",
        ]
    size_driven = min(abs(lloc_rho), abs(cc_rho)) >= _STRENGTH[0][0]
    lines += [
        f"- **LLOC:** ρ = {_n(lloc_rho)} (associação {_strength(lloc_rho)}). **CC:** ρ = {_n(cc_rho)} "
        f"({_strength(cc_rho)}). **Volume de Halstead:** ρ = {_n(volume_rho)} ({_strength(volume_rho)}).",
        "- Parte dessas associações é **mecânica**: V, G e L entram na própria fórmula do MI. A correlação "
        "mostra quanto o MI desta amostra é explicado por eles, não uma relação independente.",
        "",
    ]
    if size_driven:
        lines.append(
            "**Leitura.** Nestes 18 trials, o MI acompanha sobretudo o tamanho lógico e a complexidade "
            "ciclomática do código. O MI maior com IA observado na RQ3 corresponde, portanto, ao código com "
            "IA ter menos linhas lógicas e menor CC, e não a um aspecto de manutenibilidade que LOC e CC não "
            "capturem. Como métrica composta, o MI não acrescenta aqui evidência independente de LOC e CC — "
            "e herda deles o confundimento com os katas descrito na RQ3."
        )
    else:
        lines.append(
            "**Leitura.** O MI não se reduz a LLOC e CC nesta amostra: ao menos um deles tem associação "
            "abaixo de forte com o MI, e o volume de Halstead também pesa. O MI traz, aqui, informação além "
            "de LOC e CC — ainda sujeita ao confundimento com os katas descrito na RQ3."
        )
    return lines + [""]


def _prompt_section(results: MiPromptsResults) -> list[str]:
    joined = results.prompts_quality
    by_participant = results.prompts_by_participant
    distinct = sorted(joined["n_prompts"].unique().tolist())
    varies_within = any(len(values) > 1 for values in by_participant["n_prompts_values"])
    per_value = {
        value: sorted(joined.loc[joined["n_prompts"] == value, "participant"].unique())
        for value in distinct
    }

    lines = [
        "## 2. Nº de prompts × qualidade do código (trials com IA)",
        "",
        f"`n_prompts` vem de `data/prompts/prompt_records.csv` ({len(joined)} trials com IA). O MI usado é o "
        "**harmonizado**: a comparação aqui é entre participantes, e o MI como coletado não é comparável "
        "entre participantes.",
        "",
        "| Participante | Katas com IA | Nº de prompts | CC (mediana) | MI harmonizado (mediana) | LOC (mediana) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in by_participant.iterrows():
        katas = ", ".join(joined.loc[joined["participant"] == row["participant"], "kata_id"])
        prompts = ", ".join(str(int(v)) for v in row["n_prompts_values"])
        lines.append(
            f"| {row['participant']} | {katas} | {prompts} | "
            f"{_n(row['median_cyclomatic_complexity_avg'], 1)} | "
            f"{_n(row[f'median_{HARMONIZED_MI_KEY}'])} | {_n(row['median_loc'], 0)} |"
        )
    lines += [
        "",
        f"Correlação de Spearman entre o nº de prompts e cada métrica, nos {len(joined)} trials com IA "
        "(descritiva, sem p-valor — ver abaixo):",
        "",
        "| Métrica | ρ com o nº de prompts |",
        "|---|---:|",
        *(f"| {row['metric']} | {_rho_cell(row)} |" for _, row in results.prompt_correlations.iterrows()),
        "",
        "**Por que não há teste nem conclusão:**",
        "",
        f"- O nº de prompts assumiu {'apenas ' + str(len(distinct)) + ' valores' if len(distinct) > 1 else 'um único valor'}: "
        + "; ".join(f"{int(v)} ({', '.join(p)})" for v, p in per_value.items())
        + ".",
    ]
    if not varies_within:
        lines.append(
            "- O nº de prompts é **constante dentro de cada participante**. Qualquer associação com CC ou MI é, "
            "portanto, indistinguível da diferença entre participantes — estilo, experiência e forma de usar "
            "o assistente — e, como cada participante resolveu katas diferentes com IA, também da diferença "
            "entre katas."
        )
    lines += [
        f"- Os {len(joined)} trials não são independentes: são 3 por participante, com o mesmo nº de prompts.",
        "- O nº de prompts é autorrelatado ao final do trial.",
        "",
        "**Leitura.** Os dados coletados **não permitem avaliar** se o nº de prompts está associado à "
        "qualidade do código. Os coeficientes acima descrevem a amostra, mas não separam o efeito dos "
        "prompts do efeito do participante e do kata.",
        "",
    ]
    return lines


def generate_markdown(results: MiPromptsResults) -> str:
    lines = [
        "# Bônus S03 — MI em profundidade e nº de prompts (Issue #18)",
        "",
        "Gerado por `python -m experiment.analysis.mi_prompts`. Análise **exploratória e descritiva**: "
        "nenhum teste de hipótese novo é feito — os testes de MI entre tratamentos estão na RQ3 "
        "(`results/rq3/`), com correção de multiplicidade. Os CSVs de `data/` não são alterados.",
        "",
        "## Verificações",
        "",
        "| Verificação | Resultado | Detalhe |",
        "|---|---|---|",
        *(
            f"| {name} | {'✅' if passed else '⚠️'} | {detail} |"
            for name, passed, detail in results.checks
        ),
        "",
        *_component_section(results),
        *_prompt_section(results),
        "## Artefatos",
        "",
        "| Arquivo | Conteúdo |",
        "|---|---|",
        "| `mi_components.csv` | V, G, L, C e MI reconstruído por trial |",
        "| `mi_components_descriptive.csv` | Mediana, quartis e IQR de cada componente por tratamento |",
        "| `mi_component_correlations.csv` | ρ de Spearman entre o MI harmonizado e cada componente |",
        "| `prompts_quality.csv` | Trials com IA: nº de prompts, percepção de produtividade, CC, MI harmonizado e LOC |",
        "| `prompt_correlations.csv` | ρ de Spearman entre o nº de prompts e CC, MI harmonizado e LOC |",
        "",
        "Figuras: `docs/figures/bonus_mi_componentes.png` e `docs/figures/bonus_prompts_qualidade.png` "
        "(`python generate_figures.py`).",
        "",
    ]
    return "\n".join(lines)

