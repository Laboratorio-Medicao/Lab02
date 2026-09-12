import csv
from pathlib import Path

from experiment.domain.enums import Treatment
from experiment.domain.prompt_record import PromptRecord

CSV_FIELDNAMES = [
    "participant",
    "kata_id",
    "treatment",
    "n_prompts",
    "help_types",
    "productivity_perception",
    "notes",
]

HELP_TYPES_SEPARATOR = "|"

DEFAULT_REGISTRY_PATH = Path("data/prompts/prompt_records.csv")


def _record_to_row(record: PromptRecord) -> dict:
    return {
        "participant": record.participant,
        "kata_id": record.kata_id,
        "treatment": record.treatment.value,
        "n_prompts": record.n_prompts,
        "help_types": HELP_TYPES_SEPARATOR.join(record.help_types),
        "productivity_perception": record.productivity_perception,
        "notes": record.notes,
    }


def _row_to_record(row: dict) -> PromptRecord:
    help_types = tuple(
        h for h in row["help_types"].split(HELP_TYPES_SEPARATOR) if h
    )
    return PromptRecord(
        participant=row["participant"],
        kata_id=row["kata_id"],
        treatment=Treatment(row["treatment"]),
        n_prompts=int(row["n_prompts"]),
        help_types=help_types,
        productivity_perception=int(row["productivity_perception"]),
        notes=row["notes"],
    )


class PromptRegistry:
    def __init__(self, registry_path: Path = DEFAULT_REGISTRY_PATH):
        self._path = registry_path

    def save(self, record: PromptRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self._path.exists()

        with self._path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(_record_to_row(record))

    def load_all(self) -> list[PromptRecord]:
        if not self._path.exists():
            return []

        with self._path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [_row_to_record(row) for row in reader]

    def load_by_participant(self, participant: str) -> list[PromptRecord]:
        return [r for r in self.load_all() if r.participant == participant]
