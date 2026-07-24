from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Application, Job, ResumeProfile, User
from app.schemas import ApplicationOut, MassApplyIn

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/mass-apply", response_model=list[ApplicationOut])
def mass_apply(payload: MassApplyIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Upload a resume before applying to jobs")

    jobs = db.query(Job).filter(Job.id.in_(payload.job_ids)).all()
    found_ids = {j.id for j in jobs}
    missing = set(payload.job_ids) - found_ids
    if missing:
        raise HTTPException(status_code=404, detail=f"Job(s) not found: {sorted(missing)}")

    created = []
    for job_id in payload.job_ids:
        existing = db.query(Application).filter(Application.user_id == current_user.id, Application.job_id == job_id).first()
        if existing:
            created.append(existing)
            continue
        application = Application(user_id=current_user.id, job_id=job_id)
        db.add(application)
        created.append(application)

    db.commit()
    for app_row in created:
        db.refresh(app_row)
    return created


@router.get("", response_model=list[ApplicationOut])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Application).filter(Application.user_id == current_user.id).all()
