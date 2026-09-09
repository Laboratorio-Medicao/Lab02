"""Cronômetro de trial (time-to-green) respeitando o time-box de 35 min.

Preparado na S01 (Issue #5). A execução real dos trials é escopo da S02.
"""
from __future__ import annotations

import csv
import select
import subprocess
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


def pytest_passes(kata_path: Path) -> bool:
    """Roda `pytest` de fato sobre `kata_path` e indica se todos os testes passam.

    Usado para confirmar programaticamente o "green" de um trial, em vez de
    depender apenas da autodeclaração do participante (ver `make_pytest_checker`).
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(kata_path), "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def make_pytest_checker(
    kata_path: Path,
    poll_interval_seconds: float = 5.0,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    passes: Callable[[Path], bool] = pytest_passes,
) -> Callable[[float], bool]:
    """Cria um `wait_for_input` que verifica o "green" rodando os testes de
    aceitação do kata a cada `poll_interval_seconds`, em vez de esperar ENTER.

    Compatível com a assinatura esperada por `run_trial`: bloqueia até
    `remaining` segundos, retornando True assim que `pytest` passar (código de
    saída 0) para `kata_path`, ou False se o tempo acabar antes disso.
    """

    def checker(remaining: float) -> bool:
        deadline = clock() + remaining
        while True:
            if passes(kata_path):
                return True
            time_left = deadline - clock()
            if time_left <= 0:
                return False
            sleep(min(poll_interval_seconds, time_left))

    return checker


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
    parser.add_argument(
        "--kata-path",
        type=Path,
        default=None,
        help=(
            "Diretório do kata sendo resolvido. Se informado, o 'green' é "
            "confirmado rodando 'pytest' de verdade a cada --poll-seconds, em "
            "vez de depender de o participante pressionar ENTER."
        ),
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=5.0,
        help="Intervalo entre execuções de pytest quando --kata-path é usado (padrão: 5s)",
    )
    args = parser.parse_args()

    print(
        f"Trial iniciado: participant={args.participant} kata={args.kata_id} "
        f"treatment={args.treatment} (time-box: {TIME_BOX_MINUTES} min)"
    )

    if args.kata_path is not None:
        print(
            f"Verificando automaticamente 'pytest {args.kata_path}' a cada "
            f"{args.poll_seconds:.0f}s até todos os testes passarem..."
        )
        wait_for_input = make_pytest_checker(
            args.kata_path, poll_interval_seconds=args.poll_seconds
        )
    else:
        print("Pressione ENTER quando todos os testes de aceitação passarem...")
        wait_for_input = default_wait_for_input

    record = run_trial(
        args.participant,
        args.kata_id,
        Treatment(args.treatment),
        wait_for_input=wait_for_input,
    )
    append_record(record, args.output)

    status = "CENSURADO (time-box atingido)" if record.censored else "GREEN"
    print(f"[{status}] elapsed={record.elapsed_seconds:.1f}s -> registrado em {args.output}")


if __name__ == "__main__":
    _cli()
