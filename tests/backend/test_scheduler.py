"""Coverage for scheduler.py - never imported by any test before this file
(0% coverage: 24/24 statements missed). Covers the actual job wiring
(build_scheduler) and the signal-handling glue in main() without ever
calling the real BlockingScheduler.start(), which blocks forever.
"""
from __future__ import annotations

import signal

from apscheduler.triggers.cron import CronTrigger

from src.pipeline.jobs import scheduler


def test_build_scheduler_registers_etl_job():
    # build_scheduler() only configures the job; it is never started here,
    # so there is nothing to shut down (and shutdown() on an unstarted
    # BlockingScheduler raises SchedulerNotRunningError).
    sched = scheduler.build_scheduler()
    jobs = sched.get_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    assert job.id == "etl_daily"
    assert job.func is scheduler.run
    assert job.max_instances == 1
    assert job.coalesce is True
    assert isinstance(job.trigger, CronTrigger)


def test_main_starts_scheduler_and_wires_signal_handlers(monkeypatch):
    """main() should build the scheduler, call start(), and register SIGINT
    /SIGTERM handlers that shut the scheduler down gracefully (wait=False)
    instead of hanging on in-flight jobs."""

    class FakeScheduler:
        def __init__(self):
            self.started = False
            self.shutdown_calls = []

        def start(self):
            self.started = True

        def shutdown(self, wait=True):
            self.shutdown_calls.append(wait)

    fake = FakeScheduler()
    monkeypatch.setattr(scheduler, "build_scheduler", lambda: fake)

    registered = {}

    def fake_signal(sig, handler):
        registered[sig] = handler

    monkeypatch.setattr(signal, "signal", fake_signal)

    scheduler.main()

    assert fake.started is True
    assert signal.SIGINT in registered
    assert signal.SIGTERM in registered

    # Simulate the OS delivering SIGINT - the handler must shut the
    # scheduler down without waiting for running jobs.
    registered[signal.SIGINT](signal.SIGINT, None)
    assert fake.shutdown_calls == [False]
