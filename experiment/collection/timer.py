"""Cronômetro de trial (time-to-green) respeitando o time-box de 35 min.

Preparado na S01 (Issue #5). A execução real dos trials é escopo da S02.
"""
from __future__ import annotations

import csv
import select
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from experiment.config.lab02_design import TIME_BOX_MINUTES
from experiment.domain.enums import Treatment

CSV_FIELDNAMES = ["participant", "kata_id", "treatment", "elapsed_seconds", "censored"]


class TimerError(Exception):
    pass


@dataclass(frozen=True)
class TimingResult:
    elapsed_seconds: float
    censored: bool


@dataclass(frozen=True)
class TrialRecord:
    participant: str
    kata_id: str
    treatment: Treatment
    elapsed_seconds: float
    censored: bool

    @classmethod
    def from_timing(
        cls, participant: str, kata_id: str, treatment: Treatment, timing: TimingResult
    ) -> "TrialRecord":
        return cls(
            participant=participant,
            kata_id=kata_id,
            treatment=treatment,
            elapsed_seconds=timing.elapsed_seconds,
            censored=timing.censored,
        )

    def to_row(self) -> dict[str, str]:
        return {
            "participant": self.participant,
            "kata_id": self.kata_id,
            "treatment": self.treatment.value,
            "elapsed_seconds": f"{self.elapsed_seconds:.3f}",
            "censored": str(self.censored),
        }


class TrialTimer:
    """Mede o tempo de um trial, respeitando o time-box.

    Um trial que atinge o time-box antes de `stop()` ser chamado é
    registrado como censurado, com o tempo travado no limite (nunca
    descartado — ver enunciado, RQ1).
    """

    def __init__(
        self,
        time_box_minutes: float = TIME_BOX_MINUTES,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._time_box_seconds = time_box_minutes * 60
        self._clock = clock
        self._start: float | None = None
        self._result: TimingResult | None = None

    @property
    def time_box_seconds(self) -> float:
        return self._time_box_seconds

    def start(self) -> None:
        if self._start is not None:
            raise TimerError("Timer já foi iniciado.")
        self._start = self._clock()

    def running_elapsed(self) -> float:
        if self._start is None:
            raise TimerError("Timer ainda não foi iniciado.")
        if self._result is not None:
            return self._result.elapsed_seconds
        return self._clock() - self._start

    def remaining_seconds(self) -> float:
        return max(0.0, self._time_box_seconds - self.running_elapsed())

    def stop(self) -> TimingResult:
        """Registra o time-to-green (ou a censura, se o time-box já estourou)."""
        if self._start is None:
            raise TimerError("Timer ainda não foi iniciado.")
        if self._result is not None:
            return self._result
        raw_elapsed = self._clock() - self._start
        censored = raw_elapsed >= self._time_box_seconds
        elapsed = min(raw_elapsed, self._time_box_seconds)
        self._result = TimingResult(elapsed_seconds=elapsed, censored=censored)
        return self._result


def default_wait_for_input(timeout: float) -> bool:
    """Bloqueia até `timeout` segundos esperando uma linha em stdin.

    Retorna True se o usuário pressionou ENTER (green) dentro do prazo,
    False se o prazo expirou primeiro.
    """
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        sys.stdin.readline()
        return True
    return False


def run_trial(
    participant: str,
    kata_id: str,
    treatment: Treatment,
    time_box_minutes: float = TIME_BOX_MINUTES,
    clock: Callable[[], float] = time.monotonic,
    wait_for_input: Callable[[float], bool] = default_wait_for_input,
) -> TrialRecord:
    """Cronometra um trial até o participante sinalizar green ou o time-box estourar."""
    timer = TrialTimer(time_box_minutes=time_box_minutes, clock=clock)
    timer.start()
    while True:
        remaining = timer.remaining_seconds()
        if remaining <= 0:
            break
        if wait_for_input(remaining):
            break
    timing = timer.stop()
    return TrialRecord.from_timing(participant, kata_id, treatment, timing)


def append_record(record: TrialRecord, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    is_new = not output.exists()
    with output.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow(record.to_row())


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Cronômetro de trial (time-to-green), respeitando o time-box de "
            f"{TIME_BOX_MINUTES} min. Pressione ENTER quando os testes de "
            "aceitação passarem."
        )
    )
    parser.add_argument("participant", help="Nome do participante")
    parser.add_argument("kata_id", help="Identificador do kata")
    parser.add_argument("treatment", choices=[t.value for t in Treatment])
    parser.add_argument(
        "--output", type=Path, default=Path("data/trials.csv"), help="CSV de saída"
    )
    args = parser.parse_args()

    print(
        f"Trial iniciado: participant={args.participant} kata={args.kata_id} "
        f"treatment={args.treatment} (time-box: {TIME_BOX_MINUTES} min)"
    )
    print("Pressione ENTER quando todos os testes de aceitação passarem...")

    record = run_trial(args.participant, args.kata_id, Treatment(args.treatment))
    append_record(record, args.output)

    status = "CENSURADO (time-box atingido)" if record.censored else "GREEN"
    print(f"[{status}] elapsed={record.elapsed_seconds:.1f}s -> registrado em {args.output}")


if __name__ == "__main__":
    _cli()
