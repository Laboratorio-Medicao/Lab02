from abc import ABC, abstractmethod

from experiment.domain.enums import Treatment
from experiment.domain.protocol import TrialAssignment


class CounterbalancingStrategy(ABC):
    @abstractmethod
    def generate_assignments(
        self,
        participants: tuple[str, ...],
        n_katas: int,
    ) -> tuple[TrialAssignment, ...]:
        ...


class BlockCounterbalancingStrategy(CounterbalancingStrategy):
    """
    Divide os katas em dois blocos iguais. Participantes de índice par fazem o
    primeiro bloco com WITH_AI e o segundo com WITHOUT_AI; participantes de
    índice ímpar fazem o oposto. Garante que cada participante realize exatamente
    metade dos katas sob cada tratamento e que cada kata seja coberto pelos dois
    tratamentos entre os participantes.
    """

    def generate_assignments(
        self,
        participants: tuple[str, ...],
        n_katas: int,
    ) -> tuple[TrialAssignment, ...]:
        if n_katas % 2 != 0:
            raise ValueError("n_katas deve ser par para o contrabalanceamento em blocos")

        half = n_katas // 2
        assignments: list[TrialAssignment] = []

        for i, participant in enumerate(participants):
            for kata_idx in range(n_katas):
                in_first_block = kata_idx < half
                if i % 2 == 0:
                    treatment = Treatment.WITH_AI if in_first_block else Treatment.WITHOUT_AI
                else:
                    treatment = Treatment.WITHOUT_AI if in_first_block else Treatment.WITH_AI
                assignments.append(TrialAssignment(participant, kata_idx, treatment))

        return tuple(assignments)
