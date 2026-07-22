from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas import UpskillingPlanRequest, CourseSuggestion
from app.utils.auth import get_current_user
from app.services import flow_service
from app.agents.upskilling_planner import plan_upskilling

router = APIRouter(prefix="/upskilling", tags=["upskilling"])


@router.post("/plan")
def get_upskilling_plan(
    data: UpskillingPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No resume found")

    constraints = {
        "time": data.time,
        "cost": data.cost,
        "scope": data.scope,
    }

    try:
        result = plan_upskilling(data.goal, constraints, resume.parsed_skills)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Upskilling planning failed: {str(e)}")

    return result
