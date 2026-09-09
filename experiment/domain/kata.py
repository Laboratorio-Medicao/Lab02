from dataclasses import dataclass


@dataclass(frozen=True)
class Kata:
    id: str
    name: str
