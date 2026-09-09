import csv
from pathlib import Path

import pytest

from experiment.collection.timer import (
    TimerError,
    TrialRecord,
    TrialTimer,
    append_record,
    make_pytest_checker,
    pytest_passes,
    run_trial,
)
from experiment.domain.enums import Treatment

SAMPLE_KATA = Path(__file__).parent / "fixtures" / "sample_kata"


class FakeClock:
    def __init__(self, values):
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)


class TestTrialTimer:
    def test_stop_before_time_box_is_not_censored(self):
        timer = TrialTimer(time_box_minutes=35, clock=FakeClock([0.0, 10.0]))
        timer.start()

        result = timer.stop()

        assert result.censored is False
        assert result.elapsed_seconds == 10.0

    def test_stop_after_time_box_is_censored_and_capped(self):
        time_box_seconds = 35 * 60
        timer = TrialTimer(time_box_minutes=35, clock=FakeClock([0.0, time_box_seconds + 120]))
        timer.start()

        result = timer.stop()

        assert result.censored is True
        assert result.elapsed_seconds == time_box_seconds

    def test_stop_is_idempotent(self):
        timer = TrialTimer(time_box_minutes=35, clock=FakeClock([0.0, 5.0, 999.0]))
        timer.start()

        first = timer.stop()
        second = timer.stop()

        assert first == second

    def test_double_start_raises(self):
        timer = TrialTimer(clock=FakeClock([0.0]))
        timer.start()

        with pytest.raises(TimerError):
            timer.start()

    def test_stop_without_start_raises(self):
        timer = TrialTimer(clock=FakeClock([]))

        with pytest.raises(TimerError):
            timer.stop()

    def test_remaining_seconds_never_goes_negative(self):
        time_box_seconds = 35 * 60
        timer = TrialTimer(time_box_minutes=35, clock=FakeClock([0.0, time_box_seconds + 500]))
        timer.start()

        assert timer.remaining_seconds() == 0.0


class TestRunTrial:
    def test_records_green_before_time_box(self):
        clock = FakeClock([0.0, 0.0, 12.0])

        record = run_trial(
            participant="Marcos",
            kata_id="kata-01",
            treatment=Treatment.WITH_AI,
            time_box_minutes=35,
            clock=clock,
            wait_for_input=lambda remaining: True,
        )

        assert record.elapsed_seconds == 12.0
        assert record.censored is False
        assert record.participant == "Marcos"
        assert record.treatment is Treatment.WITH_AI

    def test_records_censored_when_wait_never_succeeds(self):
        time_box_seconds = 35 * 60
        clock = FakeClock([0.0, 0.0, time_box_seconds + 1, time_box_seconds + 1])

        record = run_trial(
            participant="Arthur",
            kata_id="kata-02",
            treatment=Treatment.WITHOUT_AI,
            time_box_minutes=35,
            clock=clock,
            wait_for_input=lambda remaining: False,
        )

        assert record.censored is True
        assert record.elapsed_seconds == time_box_seconds


class TestPytestPasses:
    def test_true_for_a_real_passing_suite(self):
        assert pytest_passes(SAMPLE_KATA) is True

    def test_false_for_a_real_failing_suite(self, tmp_path):
        (tmp_path / "test_broken.py").write_text(
            "def test_this_fails():\n    assert 1 == 2\n", encoding="utf-8"
        )

        assert pytest_passes(tmp_path) is False


class TestMakePytestChecker:
    def test_returns_true_once_passes_reports_green(self):
        clock = FakeClock([0.0, 1.0])
        sleeps: list[float] = []
        passes_sequence = iter([False, True])

        checker = make_pytest_checker(
            Path("irrelevant"),
            poll_interval_seconds=5.0,
            clock=clock,
            sleep=sleeps.append,
            passes=lambda _path: next(passes_sequence),
        )

        assert checker(30.0) is True
        assert sleeps == [5.0]

    def test_returns_false_when_time_runs_out_before_passing(self):
        clock = FakeClock([0.0, 40.0])
        sleeps: list[float] = []

        checker = make_pytest_checker(
            Path("irrelevant"),
            poll_interval_seconds=5.0,
            clock=clock,
            sleep=sleeps.append,
            passes=lambda _path: False,
        )

        assert checker(30.0) is False
        assert sleeps == []

    def test_integrates_with_run_trial_using_a_real_kata(self):
        clock = FakeClock([0.0, 0.0, 0.0, 3.0])

        checker = make_pytest_checker(
            SAMPLE_KATA,
            poll_interval_seconds=5.0,
            clock=clock,
            sleep=lambda _seconds: None,
        )
        record = run_trial(
            participant="Marcos",
            kata_id="sample",
            treatment=Treatment.WITH_AI,
            time_box_minutes=35,
            clock=clock,
            wait_for_input=checker,
        )

        assert record.censored is False
        assert record.elapsed_seconds == 3.0


class TestAppendRecord:
    def test_writes_header_once_and_appends_rows(self, tmp_path):
        output = tmp_path / "trials.csv"
        record_1 = TrialRecord("Marcos", "kata-01", Treatment.WITH_AI, 12.5, False)
        record_2 = TrialRecord("Arthur", "kata-02", Treatment.WITHOUT_AI, 2100.0, True)

        append_record(record_1, output)
        append_record(record_2, output)

        with output.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 2
        assert rows[0]["participant"] == "Marcos"
        assert rows[0]["censored"] == "False"
        assert rows[1]["kata_id"] == "kata-02"
        assert rows[1]["censored"] == "True"
