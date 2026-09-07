from dataclasses import dataclass

from experiment.domain.enums import ThreatCategory


@dataclass(frozen=True)
class Threat:
    category: ThreatCategory
    name: str
    description: str
    mitigation: str
