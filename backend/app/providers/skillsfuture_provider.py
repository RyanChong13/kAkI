"""SkillsFuture course provider.

Crawls the public MySkillsFuture course directory
(https://courses.myskillsfuture.gov.sg/search) live on each refresh via
`app.services.skillsfuture_scraper`, which paginates a curated set of search
terms and parses the course data embedded in each server-rendered results page.

If the live crawl is disabled (`SKILLSFUTURE_LIVE_CRAWL=false`) or fails/returns
nothing (network down, site markup changed, etc.), the provider falls back to
the seeded dataset in `app.seed_data.skillsfuture_courses` so the app always
starts with realistic data and never crashes on a flaky third party.
"""

import logging

from app.config import get_settings
from app.models import CourseSource
from app.providers.base import CourseProvider, NormalizedCourse, ProviderResult
from app.seed_data.skillsfuture_courses import load_seeded_courses
from app.services.skillsfuture_scraper import crawl

logger = logging.getLogger(__name__)


class SkillsFutureProvider(CourseProvider):
    source = CourseSource.SKILLSFUTURE

    async def fetch(self) -> ProviderResult:
        raw_courses, notice = await self._load_raw_courses()
        if not raw_courses:
            return ProviderResult(
                courses=[], available=False, notice=notice or "SkillsFuture data unavailable"
            )

        courses = [
            NormalizedCourse(
                external_id=c["external_id"],
                source=CourseSource.SKILLSFUTURE,
                title=c["title"],
                provider=c["provider"],
                description=c.get("description", ""),
                category=c.get("category", "SkillsFuture"),
                date=None,
                duration_hours=c.get("duration_hours"),
                price_sgd=c.get("price_sgd", 0.0),
                skillsfuture_credit_eligible=c.get("skillsfuture_credit_eligible", False),
                skillsfuture_credit_amount=c.get("skillsfuture_credit_amount", 0.0),
                location="Singapore",
                url=c.get("url", ""),
                image_url="",
                skills=c.get("skills", []),
            )
            for c in raw_courses
            if c.get("external_id") and c.get("title")
        ]
        return ProviderResult(courses=courses, available=True, notice=notice)

    async def _load_raw_courses(self) -> tuple[list[dict], str | None]:
        """Return (courses, notice). Prefers the live crawl, falls back to seed."""
        settings = get_settings()
        if settings.skillsfuture_live_crawl:
            try:
                live = await crawl()
                if live:
                    return live, None
                logger.warning("SkillsFuture live crawl returned no courses; using seed fallback")
            except Exception as exc:
                logger.warning("SkillsFuture live crawl failed (%s); using seed fallback", exc)

        try:
            return load_seeded_courses(), "Live SkillsFuture data unavailable; showing sample courses"
        except Exception as exc:
            return [], f"SkillsFuture data unavailable: {exc}"
