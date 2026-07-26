"""AI-powered endpoints: recommendations, growth plans, learning journeys,
substitute finder, auto listing generator, and multilingual chatbot."""

import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import CompletedEvent, Event, GrowthPlan, LearningJourney, SavedEvent, User
from app.schemas import (
    AIListingRequest,
    AIListingResult,
    ChatMessage,
    ChatResponse,
    EventOut,
    EventRecommendation,
    GrowthPlanOut,
    GrowthPlanRequest,
    GrowthPlanDay,
    LearningJourneyOut,
    LearningJourneyRequest,
    LearningJourneyWeek,
    SubstituteRequest,
    SubstituteResult,
)
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _get_all_events(db: Session) -> list[Event]:
    return list(db.execute(select(Event).where(Event.is_cancelled == False)).scalars().all())


def _get_user_saved_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(SavedEvent.event_id).filter(SavedEvent.user_id == user_id).all()
    return {r[0] for r in rows}


def _get_user_completed_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(CompletedEvent.event_id).filter(CompletedEvent.user_id == user_id).all()
    return {r[0] for r in rows}


# ── Recommendations ────────────────────────────────────────────────────────────

@router.get("/recommendations", response_model=list[EventRecommendation])
def get_recommendations(
    limit: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    events = _get_all_events(db)
    saved_ids = _get_user_saved_ids(db, current_user.id)
    completed_ids = _get_user_completed_ids(db, current_user.id)

    recs = ai_service.recommend_events(current_user, events, saved_ids, completed_ids, limit)
    return [
        EventRecommendation(
            event=EventOut.model_validate(r["event"]),
            match_score=r["match_score"],
            matched_skills=r["matched_skills"],
            reason=r["reason"],
        )
        for r in recs
    ]


# ── Growth Plan ────────────────────────────────────────────────────────────────

@router.post("/growth-plan", response_model=GrowthPlanOut)
def generate_growth_plan(
    payload: GrowthPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    events = _get_all_events(db)
    days_data = ai_service.generate_growth_plan(current_user, events, payload.days)

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
    events = _get_all_events(db)
    roadmap = ai_service.generate_learning_journey(current_user, events, payload.goal, payload.weeks)

    # Serialize events for storage
    roadmap_data = []
    for week in roadmap:
        roadmap_data.append({
            "week": week["week"],
            "title": week["title"],
            "focus": week["focus"],
            "event_ids": [e.id for e in week["events"]],
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

    # Build response with full event objects
    weeks_out = []
    for week in roadmap:
        weeks_out.append(LearningJourneyWeek(
            week=week["week"],
            title=week["title"],
            events=[EventOut.model_validate(e) for e in week["events"]],
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
                events = []
                for eid in rd.get("event_ids", []):
                    ev = db.get(Event, eid)
                    if ev:
                        events.append(EventOut.model_validate(ev))
                weeks_out.append(LearningJourneyWeek(
                    week=rd["week"],
                    title=rd["title"],
                    events=events,
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


# ── Substitute Finder ──────────────────────────────────────────────────────────

@router.post("/substitutes", response_model=SubstituteResult)
def find_substitutes(
    payload: SubstituteRequest,
    db: Session = Depends(get_db),
):
    target = db.get(Event, payload.event_id)
    if not target:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")

    all_events = _get_all_events(db)
    alts = ai_service.find_substitutes(target, all_events)

    reason = "Event is full or cancelled" if target.is_full or target.is_cancelled else "Looking for alternatives"

    return SubstituteResult(
        original=EventOut.model_validate(target),
        alternatives=[
            EventRecommendation(
                event=EventOut.model_validate(a["event"]),
                match_score=a["match_score"],
                matched_skills=a["matched_skills"],
                reason=a["reason"],
            )
            for a in alts
        ],
        reason=reason,
    )


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
