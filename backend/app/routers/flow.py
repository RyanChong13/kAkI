from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobSuggestion, JobFeedback
from app.schemas import FlowStartRequest, FlowSessionResponse, FeedbackRequest
from app.utils.auth import get_current_user
from app.services import flow_service

router = APIRouter(prefix="/flow", tags=["flow"])


@router.post("/start", response_model=FlowSessionResponse)
def start_flow(
    data: FlowStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure user has a resume
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    if data.path not in ("redeployment", "upskilling"):
        raise HTTPException(status_code=400, detail="Path must be 'redeployment' or 'upskilling'")

    session = flow_service.start_flow(db, current_user.id, data.path)
    return session


@router.get("/session", response_model=Optional[FlowSessionResponse])
def get_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    return session


@router.post("/feedback")
def submit_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    if flow_service.is_session_terminal(db, session):
        raise HTTPException(status_code=400, detail="Session has ended")

    if data.feedback not in ("liked", "disliked"):
        raise HTTPException(status_code=400, detail="Feedback must be 'liked' or 'disliked'")

    # Update job suggestions feedback
    if data.selected_job_ids:
        jobs = db.query(JobSuggestion).filter(
            JobSuggestion.id.in_(data.selected_job_ids),
            JobSuggestion.session_id == session.id,
        ).all()
        for job in jobs:
            job.selected = True
            db.add(job)
        db.commit()

    # Set feedback on all jobs in this round
    all_jobs = db.query(JobSuggestion).filter(
        JobSuggestion.session_id == session.id,
        JobSuggestion.round_number == session.round_number,
    ).all()
    feedback_val = JobFeedback.liked if data.feedback == "liked" else JobFeedback.disliked
    for job in all_jobs:
        job.user_feedback = feedback_val
        db.add(job)
    db.commit()

    liked = data.feedback == "liked"
    result = flow_service.handle_job_feedback(db, session, liked)
    return result
