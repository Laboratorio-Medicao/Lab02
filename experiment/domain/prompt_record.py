from dataclasses import dataclass, field

from experiment.domain.enums import Treatment


@dataclass(frozen=True)
class PromptRecord:
    participant: str
    kata_id: str
    treatment: Treatment
    n_prompts: int
    help_types: tuple[str, ...]
    productivity_perception: int
    notes: str

    def __post_init__(self):
        if not 1 <= self.productivity_perception <= 5:
            raise ValueError("productivity_perception deve estar entre 1 e 5")
        if self.n_prompts < 0:
            raise ValueError("n_prompts não pode ser negativo")
