"""SkillsFuture course provider.

There is no official public API for the MySkillsFuture course directory, so
this adapter serves a seeded, realistic dataset (`app.seed_data.skillsfuture_courses`)
instead of calling a live endpoint.

To plug in a real integration later:
  1. Implement a fetcher that either (a) calls an authorized SkillsFuture
     Singapore data feed if/when one becomes available to your organization,
     or (b) scrapes the public course directory at
     https://www.myskillsfuture.gov.sg/content/portal/en/training-exchange/course-directory.html
     respecting robots.txt / terms of use.
  2. Have it return the same list-of-dict shape as `load_seeded_courses()`.
  3. Swap the call in `fetch()` below - `course_service` and everything
     downstream (DB, API, frontend) needs no changes.
"""

from app.providers.base import CourseProvider, NormalizedCourse, ProviderResult
from app.models import CourseSource
from app.seed_data.skillsfuture_courses import load_seeded_courses


class SkillsFutureProvider(CourseProvider):
    source = CourseSource.SKILLSFUTURE

    async def fetch(self) -> ProviderResult:
        try:
            raw_courses = load_seeded_courses()
        except Exception as exc:  # defensive: seed data should never fail to load
            return ProviderResult(courses=[], available=False, notice=f"SkillsFuture data unavailable: {exc}")

        courses = [
            NormalizedCourse(
                external_id=c["external_id"],
                source=CourseSource.SKILLSFUTURE,
                title=c["title"],
                provider=c["provider"],
                description=c.get("description", ""),
                category=c.get("category", "General"),
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
        ]
        return ProviderResult(courses=courses, available=True)
