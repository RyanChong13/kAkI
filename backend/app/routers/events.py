"""Events browsing, search, filter, and save endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import CompletedEvent, Event, EventRegistration, SavedEvent, User
from app.schemas import EventListResponse, EventOut, EventRegistrationOut, SavedEventOut

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=EventListResponse)
def list_events(
    search: str | None = None,
    category: str | None = None,
    source: str | None = None,
    difficulty: str | None = None,
    max_price: float | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    free_only: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Event)

    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (Event.title.ilike(like))
            | (Event.description.ilike(like))
            | (Event.skills.ilike(like))
            | (Event.tags.ilike(like))
            | (Event.organiser.ilike(like))
        )
    if category:
        stmt = stmt.where(Event.category == category)
    if source:
        stmt = stmt.where(Event.source == source)
    if difficulty:
        stmt = stmt.where(Event.difficulty == difficulty)
    if max_price is not None:
        stmt = stmt.where(Event.price_sgd <= max_price)
    if free_only:
        stmt = stmt.where(Event.price_sgd == 0)
    if date_from:
        try:
            dt = datetime.fromisoformat(date_from)
            stmt = stmt.where(Event.date >= dt)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to)
            stmt = stmt.where(Event.date <= dt)
        except ValueError:
            pass

    stmt = stmt.where(Event.is_cancelled == False).order_by(Event.date)
    items = list(db.execute(stmt).scalars().all())

    return EventListResponse(
        items=[EventOut.model_validate(e) for e in items],
        total=len(items),
    )


@router.get("/meta/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Event.category).distinct().order_by(Event.category).all()
    return [r[0] for r in rows if r[0]]


@router.get("/meta/sources", response_model=list[str])
def get_sources(db: Session = Depends(get_db)):
    rows = db.query(Event.source).distinct().order_by(Event.source).all()
    return [r[0] for r in rows if r[0]]


@router.get("/meta/difficulties", response_model=list[str])
def get_difficulties():
    return ["Beginner", "Intermediate", "Advanced", "All Levels"]


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# ── Saved Events ───────────────────────────────────────────────────────────────

@router.get("/saved/list", response_model=list[SavedEventOut])
def list_saved_events(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(SavedEvent).filter(SavedEvent.user_id == current_user.id).all()


@router.post("/saved/{event_id}", response_model=SavedEventOut, status_code=201)
def save_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = db.query(SavedEvent).filter(
        SavedEvent.user_id == current_user.id, SavedEvent.event_id == event_id
    ).first()
    if existing:
        return existing
    saved = SavedEvent(user_id=current_user.id, event_id=event_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.delete("/saved/{event_id}", status_code=204)
def unsave_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedEvent).filter(
        SavedEvent.user_id == current_user.id, SavedEvent.event_id == event_id
    ).first()
    if saved:
        db.delete(saved)
        db.commit()


# ── Completed Events ───────────────────────────────────────────────────────────

from app.models import CompletedEvent

@router.post("/complete/{event_id}", status_code=201)
def mark_completed(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = db.query(CompletedEvent).filter(
        CompletedEvent.user_id == current_user.id, CompletedEvent.event_id == event_id
    ).first()
    if existing:
        return {"status": "already_completed"}
    ce = CompletedEvent(user_id=current_user.id, event_id=event_id)
    db.add(ce)
    db.commit()
    return {"status": "completed"}


@router.get("/completed/list", response_model=list[int])
def list_completed_event(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(CompletedEvent.event_id).filter(CompletedEvent.user_id == current_user.id).all()
    return [r[0] for r in rows]


# ── Event Registration ─────────────────────────────────────────────────────

@router.post("/register/{event_id}", response_model=EventRegistrationOut, status_code=201)
def register_for_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = db.query(EventRegistration).filter(
        EventRegistration.user_id == current_user.id, EventRegistration.event_id == event_id
    ).first()
    if existing:
        return existing
    reg = EventRegistration(user_id=current_user.id, event_id=event_id)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/register/{event_id}", status_code=204)
def unregister_from_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reg = db.query(EventRegistration).filter(
        EventRegistration.user_id == current_user.id, EventRegistration.event_id == event_id
    ).first()
    if reg:
        db.delete(reg)
        db.commit()


@router.get("/registrations/list", response_model=list[EventRegistrationOut])
def list_registrations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(EventRegistration).filter(EventRegistration.user_id == current_user.id).all()
