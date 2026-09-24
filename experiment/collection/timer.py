"""Cronômetro de trial (time-to-green) respeitando o time-box de 35 min.

Preparado na S01 (Issue #5). A execução real dos trials é escopo da S02.

Registra também, quando o "green" é confirmado via `--kata-path` (execução
real do pytest, não autodeclaração), o nº de testes de aceitação passando e
falhando ao final do trial — variável dependente de RQ2 (taxa de sucesso /
nº de testes falhando, ver `docs/experiment_design.md`).
"""
from __future__ import annotations

import csv
import re
import select
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from experiment.config.lab02_design import TIME_BOX_MINUTES
from experiment.domain.enums import Treatment

CSV_FIELDNAMES = [
    "participant",
    "kata_id",
    "treatment",
    "elapsed_seconds",
    "censored",
    "tests_total",
    "tests_passing",
    "tests_failing",
    "success_rate_percent",
]

_PASSED_RE = re.compile(r"(\d+) passed")
_FAILED_RE = re.compile(r"(\d+) failed")

# Aceita taxas gravadas com 1 casa decimal (ex.: 83.3 para 5/6 = 83.33).
_SUCCESS_RATE_TOLERANCE = 0.05


class TimerError(Exception):
    pass


@dataclass(frozen=True)
class TimingResult:
    elapsed_seconds: float
    censored: bool


@dataclass(frozen=True)
class AcceptanceTestResult:
    """Resultado dos testes de aceitação ao final de um trial (RQ2)."""

    passing: int
    total: int

    @property
    def failing(self) -> int:
        return self.total - self.passing

    @property
    def success_rate_percent(self) -> float:
        return round(100 * self.passing / self.total, 2) if self.total else 0.0


def count_test_results(kata_path: Path) -> AcceptanceTestResult:
    """Roda `pytest` sobre `kata_path` e conta testes passando/falhando.

    Usado para preencher, com o resultado real da execução (não uma
    suposição), o nº de testes de aceitação passando ao final do time-box —
    exigido pelo enunciado para cada trial.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(kata_path), "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout
    passed_match = _PASSED_RE.search(output)
    failed_match = _FAILED_RE.search(output)
    passing = int(passed_match.group(1)) if passed_match else 0
    failing = int(failed_match.group(1)) if failed_match else 0
    return AcceptanceTestResult(passing=passing, total=passing + failing)


@dataclass(frozen=True)
class TrialRecord:
    participant: str
    kata_id: str
    treatment: Treatment
    elapsed_seconds: float
    censored: bool
    test_result: AcceptanceTestResult | None = None

    @classmethod
    def from_timing(
        cls,
        participant: str,
        kata_id: str,
        treatment: Treatment,
        timing: TimingResult,
        test_result: AcceptanceTestResult | None = None,
    ) -> "TrialRecord":
        return cls(
            participant=participant,
            kata_id=kata_id,
            treatment=treatment,
            elapsed_seconds=timing.elapsed_seconds,
            censored=timing.censored,
            test_result=test_result,
        )

    def to_row(self) -> dict[str, str]:
        row = {
            "participant": self.participant,
            "kata_id": self.kata_id,
            "treatment": self.treatment.value,
            "elapsed_seconds": f"{self.elapsed_seconds:.3f}",
            "censored": str(self.censored),
            "tests_total": "",
            "tests_passing": "",
            "tests_failing": "",
            "success_rate_percent": "",
        }
        if self.test_result is not None:
            row["tests_total"] = str(self.test_result.total)
            row["tests_passing"] = str(self.test_result.passing)
            row["tests_failing"] = str(self.test_result.failing)
            row["success_rate_percent"] = f"{self.test_result.success_rate_percent:.2f}"
        return row

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "TrialRecord":
        """Reconstrói um `TrialRecord` a partir de uma linha do CSV de trials.

        Os números são lidos como float/int, não comparados como texto: nem
        todas as linhas de `data/trials.csv` foram gravadas por `to_row`
        (há `100.0` em vez de `100.00` e tempos com 1 casa decimal).

        A consistência de `tests_failing` e `success_rate_percent` é checada
        aqui, sobre a linha bruta — `AcceptanceTestResult` só guarda
        `passing` e `total` e recalcula o resto, então depois de construído o
        registro essa checagem não seria mais possível.
        """
        censored_raw = row["censored"]
        if censored_raw not in ("True", "False"):
            raise ValueError(f"censored inválido: {censored_raw!r} (esperado 'True' ou 'False')")

        test_columns = ("tests_total", "tests_passing", "tests_failing", "success_rate_percent")
        # DictReader preenche com None as colunas ausentes em linhas curtas.
        filled = [(row[column] or "").strip() != "" for column in test_columns]
        test_result = None
        if all(filled):
            test_result = AcceptanceTestResult(
                passing=int(row["tests_passing"]), total=int(row["tests_total"])
            )
            if not 0 <= test_result.passing <= test_result.total:
                raise ValueError(
                    f"tests_passing={test_result.passing} fora de 0..tests_total={test_result.total}"
                )
            if int(row["tests_failing"]) != test_result.failing:
                raise ValueError(
                    f"tests_failing={row['tests_failing']} não confere com "
                    f"tests_total - tests_passing = {test_result.failing}"
                )
            if abs(float(row["success_rate_percent"]) - test_result.success_rate_percent) > _SUCCESS_RATE_TOLERANCE:
                raise ValueError(
                    f"success_rate_percent={row['success_rate_percent']} não confere com "
                    f"{test_result.success_rate_percent} calculado de passing/total"
                )
        elif any(filled):
            raise ValueError(
                "Colunas de teste parcialmente preenchidas: devem estar todas "
                "preenchidas ou todas em branco."
            )

        return cls(
            participant=row["participant"],
            kata_id=row["kata_id"],
            treatment=Treatment(row["treatment"]),
            elapsed_seconds=float(row["elapsed_seconds"]),
            censored=censored_raw == "True",
            test_result=test_result,
        )


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
    kata_path: Path | None = None,
    count_tests: Callable[[Path], AcceptanceTestResult] = count_test_results,
) -> TrialRecord:
    """Cronometra um trial até o participante sinalizar green ou o time-box estourar.

    Se `kata_path` for informado, roda os testes de aceitação reais sobre ele
    ao final do trial (censurado ou não) e registra o resultado (nº de testes
    passando/falhando) no `TrialRecord`, em vez de deixar esse campo vazio.
    """
    timer = TrialTimer(time_box_minutes=time_box_minutes, clock=clock)
    timer.start()
    while True:
        remaining = timer.remaining_seconds()
        if remaining <= 0:
            break
        if wait_for_input(remaining):
            break
    timing = timer.stop()
    test_result = count_tests(kata_path) if kata_path is not None else None
    return TrialRecord.from_timing(participant, kata_id, treatment, timing, test_result)


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
        kata_path=args.kata_path,
    )
    append_record(record, args.output)

    status = "CENSURADO (time-box atingido)" if record.censored else "GREEN"
    tests_info = ""
    if record.test_result is not None:
        tests_info = (
            f" | testes: {record.test_result.passing}/{record.test_result.total} passando"
        )
    print(
        f"[{status}] elapsed={record.elapsed_seconds:.1f}s{tests_info} -> "
        f"registrado em {args.output}"
    )


if __name__ == "__main__":
    _cli()
