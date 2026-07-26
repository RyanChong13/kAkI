"""Organiser dashboard: CRUD events, analytics, AI listing generation."""

import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Event, OrganiserEvent, User, UserRole
from app.schemas import (
    AIListingRequest,
    AIListingResult,
    EventAnalytics,
    EventCreate,
    EventOut,
    EventUpdate,
    OrganiserDashboardStats,
)
from app.services import ai_service

router = APIRouter(prefix="/api/organiser", tags=["organiser"])


def _require_organiser(user: User):
    if user.role != UserRole.ORGANISER and user.role != "organiser":
        raise HTTPException(status_code=403, detail="Organiser access required")
    return user


# ── Dashboard Stats ────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=OrganiserDashboardStats)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)
    events = list(db.execute(
        select(Event).where(Event.created_by == current_user.id)
    ).scalars().all())
    stats = ai_service.generate_organiser_dashboard_stats(events)
    return OrganiserDashboardStats(**stats)


# ── CRUD Events ────────────────────────────────────────────────────────────────

@router.get("/events", response_model=list[EventOut])
def list_my_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)
    events = list(db.execute(
        select(Event).where(Event.created_by == current_user.id).order_by(Event.date)
    ).scalars().all())
    return [EventOut.model_validate(e) for e in events]


@router.post("/events", response_model=EventOut, status_code=201)
def create_event(
    payload: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)

    date_val = None
    if payload.date:
        try:
            date_val = datetime.fromisoformat(payload.date)
        except ValueError:
            pass

    event = Event(
        external_id=f"org-{current_user.id}-{int(datetime.now(timezone.utc).timestamp())}",
        source="User Created",
        title=payload.title,
        organiser=payload.organiser or current_user.name or "Organiser",
        description=payload.description,
        category=payload.category,
        location=payload.location,
        date=date_val,
        duration_hours=payload.duration_hours,
        price_sgd=payload.price_sgd,
        skills=payload.skills,
        difficulty=payload.difficulty,
        image_url=payload.image_url,
        tags=payload.tags,
        seo_keywords=payload.seo_keywords,
        recommended_audience=payload.recommended_audience,
        capacity=payload.capacity,
        created_by=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Also create OrganiserEvent link
    oe = OrganiserEvent(user_id=current_user.id, event_id=event.id, status="published")
    db.add(oe)
    db.commit()

    return event


@router.put("/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)
    event = db.get(Event, event_id)
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "date" and value:
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                continue
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)
    event = db.get(Event, event_id)
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    # Soft cancel
    event.is_cancelled = True
    db.commit()


# ── Analytics ──────────────────────────────────────────────────────────────────

@router.get("/events/{event_id}/analytics", response_model=EventAnalytics)
def get_event_analytics(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_organiser(current_user)
    event = db.get(Event, event_id)
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    analytics = ai_service.generate_mock_analytics(event)
    return EventAnalytics(**analytics)


# ── AI Listing Generation ─────────────────────────────────────────────────────

@router.post("/ai-generate", response_model=AIListingResult)
def ai_generate_listing(
    payload: AIListingRequest,
    current_user: User = Depends(get_current_user),
):
    _require_organiser(current_user)
    result = ai_service.generate_listing(payload.input_text)
    return AIListingResult(**result)
