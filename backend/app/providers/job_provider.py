"""Job listing provider (adapter pattern, mirrors app.providers.skillsfuture_provider).

MyCareersFuture has no public search API, so this serves a seeded dataset.
To integrate a real source later, implement a fetcher returning the same
list-of-dict shape as `load_seeded_jobs()` and swap the call below.
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.seed_data.jobs_seed import load_seeded_jobs


@dataclass
class NormalizedJob:
    external_id: str
    source: str
    title: str
    company: str
    description: str = ""
    category: str = "General"
    salary_min_sgd: float = 0.0
    salary_max_sgd: float = 0.0
    location: str = "Singapore"
    url: str = ""
    skills_required: list[str] = field(default_factory=list)
    posted_date: datetime | None = None


class SeededJobProvider:
    source = "seeded"

    def fetch(self) -> list[NormalizedJob]:
        raw_jobs = load_seeded_jobs()
        return [
            NormalizedJob(
                external_id=j["external_id"],
                source="seeded",
                title=j["title"],
                company=j["company"],
                description=j.get("description", ""),
                category=j.get("category", "General"),
                salary_min_sgd=j.get("salary_min_sgd", 0.0),
                salary_max_sgd=j.get("salary_max_sgd", 0.0),
                location="Singapore",
                url=j.get("url", ""),
                skills_required=j.get("skills_required", []),
                posted_date=None,
            )
            for j in raw_jobs
        ]
