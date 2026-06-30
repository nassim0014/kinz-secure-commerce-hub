"""APScheduler wiring — runs the ETL nightly at 02:00.

In production this would run inside the API container or a dedicated
worker. For local dev, run it as a script:

    python -m src.pipeline.jobs.scheduler
"""
from __future__ import annotations

import logging
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.api.utils.config import settings
from src.pipeline.jobs.run_etl import run

logger = logging.getLogger("kinz.scheduler")


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="Africa/Tunis")
    scheduler.add_job(
        run,
        CronTrigger.from_crontab(settings.ETL_CRON_SCHEDULE),
        id="etl_daily",
        max_instances=1,
        coalesce=True,
    )
    return scheduler


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    scheduler = build_scheduler()

    def shutdown(signum, _frame):
        logger.info("Signal %s received, shutting down", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Scheduler starting with cron='%s'", settings.ETL_CRON_SCHEDULE)
    scheduler.start()


if __name__ == "__main__":
    main()
