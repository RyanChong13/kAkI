"""Organiser dashboard: AI listing generation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User, UserRole
from app.schemas import (
    AIListingRequest,
    AIListingResult,
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
    stats = ai_service.generate_organiser_dashboard_stats()
    return OrganiserDashboardStats(**stats)


# ── AI Listing Generation ─────────────────────────────────────────────────────

@router.post("/ai-generate", response_model=AIListingResult)
def ai_generate_listing(
    payload: AIListingRequest,
    current_user: User = Depends(get_current_user),
):
    _require_organiser(current_user)
    result = ai_service.generate_listing(payload.input_text)
    return AIListingResult(**result)
