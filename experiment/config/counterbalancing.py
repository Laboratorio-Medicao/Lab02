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


class ExplicitCounterbalancingStrategy(CounterbalancingStrategy):
    """
    Contrabalanceamento com a ordem de tratamento definida explicitamente por
    participante, em vez de derivada por paridade de índice na tupla de
    participantes (como em `BlockCounterbalancingStrategy`). Útil quando a
    ordem real seguida por cada integrante durante a execução dos trials não
    coincide com a alternância par/ímpar — por exemplo, quando dois
    participantes acabam seguindo a mesma ordem e um terceiro segue a oposta.

    `first_block_with_ai` mapeia cada participante para um booleano indicando
    se o primeiro bloco de katas (metade inicial) foi resolvido com IA.
    """

    def __init__(self, first_block_with_ai: dict[str, bool]):
        self._first_block_with_ai = first_block_with_ai

    def generate_assignments(
        self,
        participants: tuple[str, ...],
        n_katas: int,
    ) -> tuple[TrialAssignment, ...]:
        if n_katas % 2 != 0:
            raise ValueError("n_katas deve ser par para o contrabalanceamento em blocos")

        missing = [p for p in participants if p not in self._first_block_with_ai]
        if missing:
            raise ValueError(f"ordem de tratamento não definida para: {', '.join(missing)}")

        half = n_katas // 2
        assignments: list[TrialAssignment] = []

        for participant in participants:
            first_block_with_ai = self._first_block_with_ai[participant]
            for kata_idx in range(n_katas):
                in_first_block = kata_idx < half
                if in_first_block:
                    treatment = Treatment.WITH_AI if first_block_with_ai else Treatment.WITHOUT_AI
                else:
                    treatment = Treatment.WITHOUT_AI if first_block_with_ai else Treatment.WITH_AI
                assignments.append(TrialAssignment(participant, kata_idx, treatment))

        return tuple(assignments)


class ExplicitTreatmentStrategy(CounterbalancingStrategy):
    """Usa a sequência de tratamentos definida para cada participante."""

    def __init__(self, treatments_by_participant: dict[str, tuple[Treatment, ...]]):
        self._treatments_by_participant = treatments_by_participant

    def generate_assignments(
        self,
        participants: tuple[str, ...],
        n_katas: int,
    ) -> tuple[TrialAssignment, ...]:
        missing = [p for p in participants if p not in self._treatments_by_participant]
        if missing:
            raise ValueError(f"tratamento não definido para: {', '.join(missing)}")

        assignments: list[TrialAssignment] = []
        for participant in participants:
            treatments = self._treatments_by_participant[participant]
            if len(treatments) != n_katas:
                raise ValueError(
                    f"a sequência de {participant} deve conter {n_katas} tratamentos"
                )
            assignments.extend(
                TrialAssignment(participant, kata_idx, treatment)
                for kata_idx, treatment in enumerate(treatments)
            )
        return tuple(assignments)
