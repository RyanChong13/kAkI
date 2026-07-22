from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.grant import GrantRecommendation
from app.schemas import GrantRecommendationResponse
from app.utils.auth import get_current_user
from app.services import flow_service
from app.agents.grant_matcher import match_grants

router = APIRouter(prefix="/grants", tags=["grants"])


@router.post("/match", response_model=List[GrantRecommendationResponse])
def get_matching_grants(
    course_name: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    user_profile = {
        "age": current_user.age,
        "sector": current_user.sector,
        "income_band": current_user.income_band,
        "grant_history": current_user.grant_history or [],
    }

    result = match_grants(db, user_profile, course_name)

    recs = []
    for grant in result["eligible_grants"]:
        gr = GrantRecommendation(
            session_id=session.id,
            grant_id=grant["grant_id"],
            course_name=course_name,
        )
        db.add(gr)
        recs.append(gr)

    db.commit()
    for r in recs:
        db.refresh(r)
    return recs


@router.get("/recommendations", response_model=List[GrantRecommendationResponse])
def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    recs = db.query(GrantRecommendation).filter(
        GrantRecommendation.session_id == session.id,
    ).all()
    return recs
