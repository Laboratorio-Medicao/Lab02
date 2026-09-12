import pytest

from experiment.collection.prompt_consolidator import PromptConsolidator
from experiment.domain.enums import Treatment
from experiment.domain.prompt_record import PromptRecord

WITH_AI = Treatment.WITH_AI
WITHOUT_AI = Treatment.WITHOUT_AI


def _record(participant, kata_id, treatment, n_prompts=3, productivity=4, notes=""):
    help_types = ("geração de código",) if treatment == WITH_AI else ()
    return PromptRecord(
        participant=participant,
        kata_id=kata_id,
        treatment=treatment,
        n_prompts=n_prompts,
        help_types=help_types,
        productivity_perception=productivity,
        notes=notes,
    )


@pytest.fixture
def sample_records():
    return [
        _record("Guilherme", "kata-01", WITH_AI, n_prompts=5, productivity=4),
        _record("Guilherme", "kata-02", WITHOUT_AI, n_prompts=0, productivity=3),
        _record("Arthur", "kata-01", WITHOUT_AI, n_prompts=0, productivity=2),
        _record("Arthur", "kata-02", WITH_AI, n_prompts=8, productivity=5),
        _record("Marcos", "kata-01", WITH_AI, n_prompts=3, productivity=3),
        _record("Marcos", "kata-02", WITHOUT_AI, n_prompts=0, productivity=4),
    ]


class TestPromptRecord:
    def test_invalid_productivity_raises(self):
        with pytest.raises(ValueError, match="productivity_perception"):
            PromptRecord("P", "kata-01", WITH_AI, 3, (), 6, "")

    def test_negative_prompts_raises(self):
        with pytest.raises(ValueError, match="n_prompts"):
            PromptRecord("P", "kata-01", WITH_AI, -1, (), 3, "")

    def test_valid_record_creates_successfully(self):
        record = _record("Guilherme", "kata-01", WITH_AI)
        assert record.participant == "Guilherme"
        assert record.treatment == WITH_AI


class TestPromptConsolidator:
    def test_consolidation_has_all_participants(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        assert set(report.participants) == {"Guilherme", "Arthur", "Marcos"}

    def test_total_records_count(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        assert report.total_records == 6

    def test_participant_trial_counts(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        guilherme = next(s for s in report.summaries if s.participant == "Guilherme")
        assert guilherme.trials_with_ai == 1
        assert guilherme.trials_without_ai == 1

    def test_avg_prompts_with_ai(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        guilherme = next(s for s in report.summaries if s.participant == "Guilherme")
        assert guilherme.avg_prompts_with_ai == 5.0

    def test_avg_productivity(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        guilherme = next(s for s in report.summaries if s.participant == "Guilherme")
        assert guilherme.avg_productivity_with_ai == 4.0
        assert guilherme.avg_productivity_without_ai == 3.0

    def test_overall_avg_prompts(self, sample_records):
        report = PromptConsolidator().consolidate(sample_records)
        assert report.overall_avg_prompts == round((5 + 8 + 3) / 3, 2)

    def test_empty_records_returns_empty_report(self):
        report = PromptConsolidator().consolidate([])
        assert report.total_records == 0
        assert report.participants == ()
