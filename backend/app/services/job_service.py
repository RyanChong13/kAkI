from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job
from app.providers.job_provider import SeededJobProvider


def refresh_jobs(db: Session) -> int:
    provider = SeededJobProvider()
    jobs = provider.fetch()

    for item in jobs:
        existing = db.execute(
            select(Job).where(Job.source == item.source, Job.external_id == item.external_id)
        ).scalar_one_or_none()

        skills_str = ", ".join(item.skills_required)

        if existing:
            existing.title = item.title
            existing.company = item.company
            existing.description = item.description
            existing.category = item.category
            existing.salary_min_sgd = item.salary_min_sgd
            existing.salary_max_sgd = item.salary_max_sgd
            existing.location = item.location
            existing.url = item.url
            existing.skills_required = skills_str
        else:
            db.add(
                Job(
                    external_id=item.external_id,
                    source=item.source,
                    title=item.title,
                    company=item.company,
                    description=item.description,
                    category=item.category,
                    salary_min_sgd=item.salary_min_sgd,
                    salary_max_sgd=item.salary_max_sgd,
                    location=item.location,
                    url=item.url,
                    skills_required=skills_str,
                )
            )

    db.commit()
    return len(jobs)


def list_jobs(db: Session, *, category: str | None = None, exclude_ids: list[int] | None = None) -> list[Job]:
    stmt = select(Job)
    if category:
        stmt = stmt.where(Job.category == category)
    if exclude_ids:
        stmt = stmt.where(Job.id.notin_(exclude_ids))
    return list(db.execute(stmt.order_by(Job.title)).scalars().all())
