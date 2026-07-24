"""Orchestrates course data providers, caching, and querying.

This is the single place that talks to the `courses` table on behalf of
providers. `refresh_all_sources()` is called on startup and on a schedule
(see app.scheduler) to pull from every registered provider and upsert into
SQLite, so page requests always read cached data instead of hitting
third-party APIs directly.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course, CourseSource
from app.providers.base import CourseProvider, NormalizedCourse, ProviderResult
from app.providers.eventbrite_provider import EventbriteProvider
from app.providers.skillsfuture_provider import SkillsFutureProvider

logger = logging.getLogger(__name__)

PROVIDERS: list[CourseProvider] = [
    SkillsFutureProvider(),
    EventbriteProvider(),
]

# In-memory record of the last refresh's provider availability, used to show
# the "Eventbrite unavailable" banner on the frontend without re-querying it.
_last_provider_notices: dict[str, str | None] = {}
_last_provider_availability: dict[str, bool] = {}


def _upsert_course(db: Session, item: NormalizedCourse) -> None:
    existing = db.execute(
        select(Course).where(Course.source == item.source, Course.external_id == item.external_id)
    ).scalar_one_or_none()

    skills_str = ", ".join(item.skills)

    if existing:
        existing.title = item.title
        existing.provider = item.provider
        existing.description = item.description
        existing.category = item.category
        existing.date = item.date
        existing.duration_hours = item.duration_hours
        existing.price_sgd = item.price_sgd
        existing.skillsfuture_credit_eligible = item.skillsfuture_credit_eligible
        existing.skillsfuture_credit_amount = item.skillsfuture_credit_amount
        existing.location = item.location
        existing.url = item.url
        existing.image_url = item.image_url
        existing.skills = skills_str
    else:
        db.add(
            Course(
                external_id=item.external_id,
                source=item.source,
                title=item.title,
                provider=item.provider,
                description=item.description,
                category=item.category,
                date=item.date,
                duration_hours=item.duration_hours,
                price_sgd=item.price_sgd,
                skillsfuture_credit_eligible=item.skillsfuture_credit_eligible,
                skillsfuture_credit_amount=item.skillsfuture_credit_amount,
                location=item.location,
                url=item.url,
                image_url=item.image_url,
                skills=skills_str,
            )
        )


async def refresh_all_sources(db: Session) -> dict[str, ProviderResult]:
    """Fetch from every provider and upsert into the DB. Never raises."""
    results: dict[str, ProviderResult] = {}
    for provider in PROVIDERS:
        try:
            result = await provider.fetch()
        except Exception as exc:  # a provider bug must not break refresh for others
            logger.exception("Provider %s raised unexpectedly", provider.source)
            result = ProviderResult(courses=[], available=False, notice=f"Unexpected error: {exc}")

        results[provider.source.value] = result
        _last_provider_availability[provider.source.value] = result.available
        _last_provider_notices[provider.source.value] = result.notice

        for course in result.courses:
            _upsert_course(db, course)

    db.commit()
    return results


def get_provider_status(source: str) -> tuple[bool, str | None]:
    return _last_provider_availability.get(source, False), _last_provider_notices.get(source)


def list_courses(
    db: Session,
    *,
    search: str | None = None,
    category: str | None = None,
    provider: str | None = None,
    max_price: float | None = None,
    date_from=None,
    date_to=None,
    source: CourseSource | None = None,
) -> list[Course]:
    stmt = select(Course)

    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            (Course.title.ilike(like)) | (Course.description.ilike(like)) | (Course.skills.ilike(like))
        )
    if category:
        stmt = stmt.where(Course.category == category)
    if provider:
        stmt = stmt.where(Course.provider == provider)
    if max_price is not None:
        stmt = stmt.where(Course.price_sgd <= max_price)
    if date_from is not None:
        stmt = stmt.where(Course.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Course.date <= date_to)
    if source is not None:
        stmt = stmt.where(Course.source == source)

    stmt = stmt.order_by(Course.title)
    return list(db.execute(stmt).scalars().all())
