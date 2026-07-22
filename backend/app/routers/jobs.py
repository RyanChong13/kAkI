from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobSuggestion
from app.schemas import JobSuggestionResponse
from app.utils.auth import get_current_user
from app.services import flow_service
from app.agents.job_recommender import recommend_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/recommend", response_model=List[JobSuggestionResponse])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session. Start a flow first.")

    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No resume found")

    try:
        result = recommend_jobs(resume.parsed_skills)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {str(e)}")

    suggestions = []
    for job in result["job_suggestions"]:
        js = JobSuggestion(
            session_id=session.id,
            title=job["title"],
            matched_skills=job["matched_skills"],
            missing_skills=job["missing_skills"],
            round_number=session.round_number,
        )
        db.add(js)
        suggestions.append(js)

    db.commit()
    for s in suggestions:
        db.refresh(s)
    return suggestions


@router.get("/suggestions", response_model=List[JobSuggestionResponse])
def list_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    jobs = db.query(JobSuggestion).filter(
        JobSuggestion.session_id == session.id,
        JobSuggestion.round_number == session.round_number,
    ).all()
    return jobs
