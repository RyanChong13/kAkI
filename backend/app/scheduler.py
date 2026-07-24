"""Background scheduler that refreshes cached course data periodically,
so page requests never call Eventbrite/SkillsFuture directly."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.database import SessionLocal
from app.services.course_service import refresh_all_sources

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _refresh_job() -> None:
    db = SessionLocal()
    try:
        results = await refresh_all_sources(db)
        for source, result in results.items():
            status = "ok" if result.available else f"unavailable ({result.notice})"
            logger.info("Course refresh: %s -> %s, %d courses", source, status, len(result.courses))
    finally:
        db.close()


def start_scheduler() -> None:
    settings = get_settings()
    scheduler.add_job(
        _refresh_job,
        "interval",
        hours=settings.course_refresh_interval_hours,
        id="refresh_courses",
        replace_existing=True,
        next_run_time=None,  # initial refresh is triggered explicitly on startup
    )
    scheduler.start()


async def initial_refresh() -> None:
    await _refresh_job()
