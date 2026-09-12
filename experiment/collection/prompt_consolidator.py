from collections import Counter
from dataclasses import dataclass

from experiment.domain.enums import Treatment
from experiment.domain.prompt_record import PromptRecord


@dataclass(frozen=True)
class ParticipantSummary:
    participant: str
    total_trials: int
    trials_with_ai: int
    trials_without_ai: int
    total_prompts: int
    avg_prompts_with_ai: float
    avg_productivity_with_ai: float
    avg_productivity_without_ai: float
    most_requested_help: str


@dataclass(frozen=True)
class ConsolidatedReport:
    total_records: int
    participants: tuple[str, ...]
    summaries: tuple[ParticipantSummary, ...]
    overall_avg_prompts: float
    most_requested_help_overall: str


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def _most_common_help(records: list[PromptRecord]) -> str:
    counter: Counter = Counter()
    for record in records:
        counter.update(record.help_types)
    return counter.most_common(1)[0][0] if counter else "N/A"


def _summarize_participant(participant: str, records: list[PromptRecord]) -> ParticipantSummary:
    with_ai = [r for r in records if r.treatment == Treatment.WITH_AI]
    without_ai = [r for r in records if r.treatment == Treatment.WITHOUT_AI]

    return ParticipantSummary(
        participant=participant,
        total_trials=len(records),
        trials_with_ai=len(with_ai),
        trials_without_ai=len(without_ai),
        total_prompts=sum(r.n_prompts for r in with_ai),
        avg_prompts_with_ai=_avg([r.n_prompts for r in with_ai]),
        avg_productivity_with_ai=_avg([r.productivity_perception for r in with_ai]),
        avg_productivity_without_ai=_avg([r.productivity_perception for r in without_ai]),
        most_requested_help=_most_common_help(with_ai),
    )


class PromptConsolidator:
    def consolidate(self, records: list[PromptRecord]) -> ConsolidatedReport:
        participants = sorted({r.participant for r in records})
        summaries = tuple(
            _summarize_participant(p, [r for r in records if r.participant == p])
            for p in participants
        )
        with_ai_records = [r for r in records if r.treatment == Treatment.WITH_AI]

        return ConsolidatedReport(
            total_records=len(records),
            participants=tuple(participants),
            summaries=summaries,
            overall_avg_prompts=_avg([r.n_prompts for r in with_ai_records]),
            most_requested_help_overall=_most_common_help(with_ai_records),
        )
