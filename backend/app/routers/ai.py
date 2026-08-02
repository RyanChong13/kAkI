"""AI-powered endpoints: growth plans, learning journeys, auto listing generator, and multilingual chatbot."""

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import GrowthPlan, LearningJourney, User
from app.schemas import (
    AIListingRequest,
    AIListingResult,
    ChatMessage,
    ChatResponse,
    GrowthPlanOut,
    GrowthPlanRequest,
    GrowthPlanDay,
    LearningJourneyOut,
    LearningJourneyRequest,
    LearningJourneyWeek,
)
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ── Growth Plan ────────────────────────────────────────────────────────────────

@router.post("/growth-plan", response_model=GrowthPlanOut)
def generate_growth_plan(
    payload: GrowthPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    days_data = ai_service.generate_growth_plan(current_user, payload.days)

    plan = GrowthPlan(
        user_id=current_user.id,
        plan_type=str(payload.days),
        plan_json=json.dumps(days_data),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return GrowthPlanOut(
        id=plan.id,
        plan_type=plan.plan_type,
        days=[GrowthPlanDay(**d) for d in days_data],
        created_at=plan.created_at,
    )


@router.get("/growth-plans", response_model=list[GrowthPlanOut])
def list_growth_plans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plans = db.query(GrowthPlan).filter(GrowthPlan.user_id == current_user.id).order_by(GrowthPlan.created_at.desc()).all()
    result = []
    for p in plans:
        try:
            days_data = json.loads(p.plan_json)
            result.append(GrowthPlanOut(
                id=p.id,
                plan_type=p.plan_type,
                days=[GrowthPlanDay(**d) for d in days_data],
                created_at=p.created_at,
            ))
        except (json.JSONDecodeError, Exception):
            continue
    return result


# ── Learning Journey ───────────────────────────────────────────────────────────

@router.post("/learning-journey", response_model=LearningJourneyOut)
def generate_learning_journey(
    payload: LearningJourneyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = ai_service.generate_learning_journey(current_user, payload.goal, payload.weeks)

    # Serialize roadmap for storage
    roadmap_data = []
    for week in roadmap:
        roadmap_data.append({
            "week": week["week"],
            "title": week["title"],
            "focus": week["focus"],
        })

    journey = LearningJourney(
        user_id=current_user.id,
        goal=payload.goal,
        roadmap_json=json.dumps(roadmap_data),
        total_weeks=payload.weeks,
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)

    # Build response
    weeks_out = []
    for week in roadmap:
        weeks_out.append(LearningJourneyWeek(
            week=week["week"],
            title=week["title"],
            events=[],
            focus=week["focus"],
        ))

    return LearningJourneyOut(
        id=journey.id,
        goal=journey.goal,
        current_week=journey.current_week,
        total_weeks=journey.total_weeks,
        roadmap=weeks_out,
        created_at=journey.created_at,
    )


@router.get("/learning-journeys", response_model=list[LearningJourneyOut])
def list_learning_journeys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    journeys = db.query(LearningJourney).filter(LearningJourney.user_id == current_user.id).order_by(LearningJourney.created_at.desc()).all()
    result = []
    for j in journeys:
        try:
            roadmap_data = json.loads(j.roadmap_json)
            weeks_out = []
            for rd in roadmap_data:
                weeks_out.append(LearningJourneyWeek(
                    week=rd["week"],
                    title=rd["title"],
                    events=[],
                    focus=rd.get("focus", ""),
                ))
            result.append(LearningJourneyOut(
                id=j.id,
                goal=j.goal,
                current_week=j.current_week,
                total_weeks=j.total_weeks,
                roadmap=weeks_out,
                created_at=j.created_at,
            ))
        except (json.JSONDecodeError, Exception):
            continue
    return result


# ── AI Auto Listing Generator ──────────────────────────────────────────────────

@router.post("/generate-listing", response_model=AIListingResult)
def generate_listing(payload: AIListingRequest):
    result = ai_service.generate_listing(payload.input_text)
    return AIListingResult(**result)


# ── AI Chatbot ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatMessage,
    current_user: User = Depends(get_current_user),
):
    result = ai_service.chat_response(payload.message, payload.language, current_user)
    return ChatResponse(**result)
