from dataclasses import dataclass

from experiment.domain.enums import Treatment


@dataclass(frozen=True)
class TrialAssignment:
    participant: str
    kata_index: int
    treatment: Treatment


@dataclass(frozen=True)
class CrossoverProtocol:
    n_katas: int
    participants: tuple[str, ...]
    time_box_minutes: int
    assignments: tuple[TrialAssignment, ...]

    def get_assignments_for_participant(self, participant: str) -> list[TrialAssignment]:
        return [a for a in self.assignments if a.participant == participant]

    def get_assignments_for_kata(self, kata_index: int) -> list[TrialAssignment]:
        return [a for a in self.assignments if a.kata_index == kata_index]

    def get_treatment(self, participant: str, kata_index: int) -> Treatment:
        for assignment in self.assignments:
            if assignment.participant == participant and assignment.kata_index == kata_index:
                return assignment.treatment
        raise ValueError(f"Nenhuma atribuição encontrada para participante={participant}, kata={kata_index}")
