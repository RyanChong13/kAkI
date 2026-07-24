"""Adapter pattern for course/workshop data sources.

Every provider (SkillsFuture, Eventbrite, and any future source) implements
`CourseProvider.fetch()` and returns a list of `NormalizedCourse` objects.
`app.services.course_service` is the only code that talks to the database:
it calls each registered provider, normalizes results into `Course` rows,
and upserts them. This keeps providers dumb and swappable - adding a new
source means writing one class and registering it, nothing else changes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.models import CourseSource


@dataclass
class NormalizedCourse:
    external_id: str
    source: CourseSource
    title: str
    provider: str
    description: str = ""
    category: str = "General"
    date: datetime | None = None
    duration_hours: float | None = None
    price_sgd: float = 0.0
    skillsfuture_credit_eligible: bool = False
    skillsfuture_credit_amount: float = 0.0
    location: str = "Singapore"
    url: str = ""
    image_url: str = ""
    skills: list[str] = field(default_factory=list)


@dataclass
class ProviderResult:
    courses: list[NormalizedCourse]
    available: bool = True
    notice: str | None = None


class CourseProvider(ABC):
    source: CourseSource

    @abstractmethod
    async def fetch(self) -> ProviderResult:
        """Return normalized courses from this source.

        Must never raise - failures should be caught internally and
        surfaced via `ProviderResult(available=False, notice=...)` so a
        single flaky source can't take down the whole listing page.
        """
        raise NotImplementedError
