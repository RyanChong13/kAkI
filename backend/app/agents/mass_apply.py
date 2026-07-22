"""Mass Apply Agent — Two-step review-then-apply flow.
Step 1: Assemble preview. Step 2: Confirm and submit."""

import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationType
from app.models.resume import Resume
from app.models.job import JobSuggestion
from app.models.grant import Grant, GrantRecommendation
from app.config import settings

# In-memory preview store (use Redis/DB in production)
_preview_store: dict = {}


def assemble_preview(
    db: Session,
    user_id: int,
    session_id: int,
    apply_type: str,
    target_ids: List[int],
) -> dict:
    """Step 1: Assemble a preview of what will be submitted."""
    if len(target_ids) > settings.MAX_BATCH_SIZE:
        raise ValueError(f"Batch exceeds maximum of {settings.MAX_BATCH_SIZE} items")

    resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise ValueError("No resume found for user")

    items = []
    for tid in target_ids:
        if apply_type == "job":
            job = db.query(JobSuggestion).filter(JobSuggestion.id == tid).first()
            if job:
                items.append({
                    "target_id": job.id,
                    "target_name": job.title,
                    "type": "job",
                    "details": {
                        "matched_skills": job.matched_skills,
                        "missing_skills": job.missing_skills,
                        "resume_skills": resume.parsed_skills,
                    },
                })
        elif apply_type == "grant":
            grant = db.query(Grant).filter(Grant.id == tid).first()
            if grant:
                items.append({
                    "target_id": grant.id,
                    "target_name": grant.name,
                    "type": "grant",
                    "details": {
                        "amount": float(grant.amount),
                        "resume_skills": resume.parsed_skills,
                    },
                })

    preview_id = str(uuid.uuid4())
    _preview_store[preview_id] = {
        "user_id": user_id,
        "session_id": session_id,
        "items": items,
        "type": apply_type,
        "created_at": datetime.utcnow().isoformat(),
    }

    return {"preview_id": preview_id, "items": items}


def confirm_and_submit(db: Session, preview_id: str) -> List[dict]:
    """Step 2: Confirm and submit the batch. Server-side enforcement of confirmation."""
    preview = _preview_store.pop(preview_id, None)
    if not preview:
        raise ValueError("Preview not found or expired")

    applications = []
    for item in preview["items"]:
        app_type = ApplicationType.job if item["type"] == "job" else ApplicationType.grant
        app = Application(
            user_id=preview["user_id"],
            session_id=preview["session_id"],
            type=app_type,
            target_id=item["target_id"],
            target_name=item["target_name"],
            confirmed=True,
            submitted_at=datetime.utcnow(),
            snapshot=item,
        )
        db.add(app)
        applications.append(item)

    db.commit()
    return applications
