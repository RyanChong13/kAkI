from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Job, JobFeedback, ResumeProfile, User
from app.schemas import JobFeedbackIn, JobOut, JobRecommendation
from app.services.job_service import list_jobs
from app.services.matching_service import match_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def get_jobs(category: str | None = None, db: Session = Depends(get_db)):
    return list_jobs(db, category=category)


@router.get("/recommendations", response_model=list[JobRecommendation])
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == current_user.id).first()
    user_skills = [s.strip() for s in profile.extracted_skills.split(",")] if profile and profile.extracted_skills else []

    disliked_ids = [
        fb.job_id for fb in db.query(JobFeedback).filter(JobFeedback.user_id == current_user.id, JobFeedback.liked.is_(False)).all()
    ]

    jobs = list_jobs(db, exclude_ids=disliked_ids)
    ranked = match_jobs(user_skills, jobs)
    return [JobRecommendation(job=JobOut.model_validate(job), match_score=score, matched_skills=skills) for job, score, skills in ranked]


@router.post("/feedback", status_code=204)
def submit_feedback(payload: JobFeedbackIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = (
        db.query(JobFeedback)
        .filter(JobFeedback.user_id == current_user.id, JobFeedback.job_id == payload.job_id)
        .first()
    )
    if existing:
        existing.liked = payload.liked
    else:
        db.add(JobFeedback(user_id=current_user.id, job_id=payload.job_id, liked=payload.liked))
    db.commit()
    return None


@router.get("/liked", response_model=list[JobOut])
def get_liked_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    liked_ids = [
        fb.job_id for fb in db.query(JobFeedback).filter(JobFeedback.user_id == current_user.id, JobFeedback.liked.is_(True)).all()
    ]
    if not liked_ids:
        return []
    return db.query(Job).filter(Job.id.in_(liked_ids)).all()
