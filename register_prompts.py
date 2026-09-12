"""
Script interativo para registrar os dados de prompts ao final de cada trial.
Uso: python3 register_prompts.py
"""

from experiment.collection.prompt_registry import PromptRegistry
from experiment.domain.enums import HelpType, Treatment
from experiment.domain.prompt_record import PromptRecord


def _ask(prompt: str, valid: list[str] | None = None) -> str:
    while True:
        value = input(prompt).strip()
        if valid is None or value in valid:
            return value
        print(f"  Opções válidas: {', '.join(valid)}")


def _ask_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if min_val <= value <= max_val:
                return value
            print(f"  Digite um número entre {min_val} e {max_val}.")
        except ValueError:
            print("  Valor inválido.")


def _ask_help_types() -> tuple[str, ...]:
    options = {str(i + 1): h for i, h in enumerate(HelpType)}
    print("\n  Tipos de ajuda solicitada (separe por vírgula, ex: 1,3):")
    for key, help_type in options.items():
        print(f"    {key}. {help_type.value}")
    while True:
        raw = input("  Escolha: ").strip()
        chosen = [options[k.strip()].value for k in raw.split(",") if k.strip() in options]
        if chosen:
            return tuple(chosen)
        print("  Selecione ao menos uma opção válida.")


def main():
    print("=== Registro de Trial — Prompts e Dados Qualitativos ===\n")

    participant = input("Participante: ").strip()
    kata_id = input("Kata ID (ex: kata-01): ").strip()

    treatment_input = _ask(
        "Tratamento [with_ai / without_ai]: ",
        valid=[t.value for t in Treatment],
    )
    treatment = Treatment(treatment_input)

    n_prompts = 0
    help_types: tuple[str, ...] = ()

    if treatment == Treatment.WITH_AI:
        n_prompts = _ask_int("Número de prompts utilizados: ", min_val=0, max_val=999)
        help_types = _ask_help_types()

    productivity = _ask_int(
        "\nPercepção de produtividade (1 = muito baixa, 5 = muito alta): ",
        min_val=1,
        max_val=5,
    )
    notes = input("Anotações / dificuldades encontradas (opcional): ").strip()

    record = PromptRecord(
        participant=participant,
        kata_id=kata_id,
        treatment=treatment,
        n_prompts=n_prompts,
        help_types=help_types,
        productivity_perception=productivity,
        notes=notes,
    )

    registry = PromptRegistry()
    registry.save(record)
    print(f"\nRegistro salvo com sucesso.")


if __name__ == "__main__":
    main()
