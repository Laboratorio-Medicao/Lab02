from experiment.config.counterbalancing import CounterbalancingStrategy
from experiment.config.experiment_design import ExperimentDesign
from experiment.domain.enums import ResearchQuestion
from experiment.domain.hypothesis import Hypothesis
from experiment.domain.kata import Kata
from experiment.domain.protocol import CrossoverProtocol
from experiment.domain.threat import Threat
from experiment.domain.variable import Variable


class ExperimentDesignBuilder:
    def __init__(self) -> None:
        self._goal: str = ""
        self._hypotheses: dict[ResearchQuestion, tuple[Hypothesis, Hypothesis]] = {}
        self._independent_variable: Variable | None = None
        self._dependent_variables: list[Variable] = []
        self._control_variables: list[Variable] = []
        self._threats: list[Threat] = []
        self._protocol: CrossoverProtocol | None = None
        self._katas: tuple[Kata, ...] = ()

    def with_goal(self, goal: str) -> "ExperimentDesignBuilder":
        self._goal = goal
        return self

    def add_hypothesis(self, h0: Hypothesis, h1: Hypothesis) -> "ExperimentDesignBuilder":
        if h0.rq != h1.rq:
            raise ValueError("H0 e H1 devem pertencer à mesma questão de pesquisa")
        self._hypotheses[h0.rq] = (h0, h1)
        return self

    def with_independent_variable(self, variable: Variable) -> "ExperimentDesignBuilder":
        self._independent_variable = variable
        return self

    def add_dependent_variable(self, variable: Variable) -> "ExperimentDesignBuilder":
        self._dependent_variables.append(variable)
        return self

    def add_control_variable(self, variable: Variable) -> "ExperimentDesignBuilder":
        self._control_variables.append(variable)
        return self

    def add_threat(self, threat: Threat) -> "ExperimentDesignBuilder":
        self._threats.append(threat)
        return self

    def with_katas(self, katas: tuple[Kata, ...]) -> "ExperimentDesignBuilder":
        self._katas = katas
        return self

    def with_protocol(
        self,
        participants: tuple[str, ...],
        n_katas: int,
        time_box_minutes: int,
        strategy: CounterbalancingStrategy,
    ) -> "ExperimentDesignBuilder":
        assignments = strategy.generate_assignments(participants, n_katas)
        self._protocol = CrossoverProtocol(
            n_katas=n_katas,
            participants=participants,
            time_box_minutes=time_box_minutes,
            assignments=assignments,
        )
        return self

    def build(self) -> ExperimentDesign:
        if not self._goal:
            raise ValueError("O objetivo do experimento é obrigatório")
        if self._independent_variable is None:
            raise ValueError("A variável independente é obrigatória")
        if self._protocol is None:
            raise ValueError("O protocolo é obrigatório")
        if self._katas and len(self._katas) != self._protocol.n_katas:
            raise ValueError(
                f"Número de katas ({len(self._katas)}) não corresponde a "
                f"n_katas do protocolo ({self._protocol.n_katas})"
            )

        return ExperimentDesign(
            goal=self._goal,
            hypotheses=self._hypotheses,
            independent_variable=self._independent_variable,
            dependent_variables=tuple(self._dependent_variables),
            control_variables=tuple(self._control_variables),
            protocol=self._protocol,
            threats=tuple(self._threats),
            katas=self._katas,
        )
