from dataclasses import dataclass

from experiment.domain.enums import ResearchQuestion, VariableType


@dataclass(frozen=True)
class Variable:
    name: str
    description: str
    type: VariableType
    unit: str
    research_questions: tuple[ResearchQuestion, ...]
    notes: str = ""
