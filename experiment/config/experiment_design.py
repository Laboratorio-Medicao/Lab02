from dataclasses import dataclass

from experiment.domain.enums import ResearchQuestion
from experiment.domain.hypothesis import Hypothesis
from experiment.domain.kata import Kata
from experiment.domain.protocol import CrossoverProtocol
from experiment.domain.threat import Threat
from experiment.domain.variable import Variable


@dataclass(frozen=True)
class ExperimentDesign:
    goal: str
    hypotheses: dict[ResearchQuestion, tuple[Hypothesis, Hypothesis]]
    independent_variable: Variable
    dependent_variables: tuple[Variable, ...]
    control_variables: tuple[Variable, ...]
    protocol: CrossoverProtocol
    threats: tuple[Threat, ...]
    katas: tuple[Kata, ...] = ()

    def get_hypotheses(self, rq: ResearchQuestion) -> tuple[Hypothesis, Hypothesis]:
        return self.hypotheses[rq]

    def summary(self) -> str:
        deps = ", ".join(v.name for v in self.dependent_variables)
        controls = ", ".join(v.name for v in self.control_variables)
        lines = [
            f"Goal: {self.goal}",
            f"Independent variable: {self.independent_variable.name}",
            f"Dependent variables: {deps}",
            f"Control variables: {controls}",
            f"Protocol: {len(self.protocol.participants)} participants, "
            f"{self.protocol.n_katas} katas, {self.protocol.time_box_minutes} min/trial",
            f"Threats identified: {len(self.threats)}",
        ]
        return "\n".join(lines)
