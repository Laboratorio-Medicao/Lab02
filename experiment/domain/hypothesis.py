from dataclasses import dataclass

from experiment.domain.enums import HypothesisType, ResearchQuestion


@dataclass(frozen=True)
class Hypothesis:
    rq: ResearchQuestion
    type: HypothesisType
    statement: str

    def __str__(self) -> str:
        return f"{self.type.value} ({self.rq.value}): {self.statement}"
