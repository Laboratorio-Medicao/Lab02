"""
Consolida os dados de prompts de todos os participantes e gera relatório markdown.
Uso: python3 consolidate_prompts.py
"""

from pathlib import Path

from experiment.collection.prompt_consolidator import PromptConsolidator
from experiment.collection.prompt_registry import PromptRegistry
from experiment.collection.prompt_report import export

OUTPUT_PATH = Path("docs/prompt_consolidation.md")


def main():
    registry = PromptRegistry()
    records = registry.load_all()

    if not records:
        print("Nenhum registro encontrado em data/prompts/prompt_records.csv.")
        return

    report = PromptConsolidator().consolidate(records)
    export(report, OUTPUT_PATH)


if __name__ == "__main__":
    main()
