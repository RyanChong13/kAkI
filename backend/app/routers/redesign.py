"""Role redesign endpoints — the core MVP flow.

``GET  /api/roles``          — list the role taxonomy (for the dropdown)
``POST /api/redesign``       — generate AI redesign suggestions + matched courses/schemes

No auth required — the redesign tool is open so anyone can try it.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CourseOut,
    MatchedCourseOut,
    RedesignRequest,
    RedesignResult,
    RedesignSuggestion,
    RoleListResponse,
    RoleOut,
    SchemeInfo,
)
from app.seed_data.role_taxonomy import list_categories, list_roles
from app.services.redesign_service import run_redesign

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["redesign"])


@router.get("/roles", response_model=RoleListResponse)
def get_roles():
    """Return the full role taxonomy grouped by category."""
    roles = [RoleOut(**r) for r in list_roles()]
    return RoleListResponse(categories=list_categories(), roles=roles)


@router.post("/redesign", response_model=RedesignResult)
def redesign(payload: RedesignRequest, db: Session = Depends(get_db)):
    """Generate AI-augmented redesign suggestions for a role.

    Calls Claude to produce 2-3 directions, then matches each against
    SkillsFuture courses and funding schemes.  No auth required.
    """
    try:
        result = run_redesign(payload.role, db, age=payload.age)
    except RuntimeError as exc:
        # API key not configured
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Redesign failed for role '%s'", payload.role)
        raise HTTPException(status_code=502, detail=f"Redesign generation failed: {exc}")

    # Convert raw dicts → response models (Course objects → CourseOut)
    suggestions = []
    for s in result["suggestions"]:
        matched = []
        for mc in s.get("matched_courses", []):
            course = mc["course"]
            matched.append(MatchedCourseOut(
                course=CourseOut.model_validate(course),
                match_score=mc["match_score"],
                matched_skills=mc["matched_skills"],
                schemes=[SchemeInfo(**sch) for sch in mc["schemes"]],
            ))
        suggestions.append(RedesignSuggestion(
            title=s["title"],
            description=s["description"],
            why=s["why"],
            ai_impact=s["ai_impact"],
            upskilling_areas=s["upskilling_areas"],
            estimated_timeframe=s["estimated_timeframe"],
            matched_courses=matched,
        ))

    return RedesignResult(
        role=result["role"],
        role_category=result["role_category"],
        role_core_tasks=result["role_core_tasks"],
        suggestions=suggestions,
    )
