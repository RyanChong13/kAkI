"""Role redesign endpoints — the core MVP flow.

``GET  /api/roles``            — list the role taxonomy (for the dropdown)
``POST /api/redesign``         — generate AI redesign suggestions + matched courses/schemes
``POST /api/resume/analyze``   — upload a resume PDF → skills + ranked career matches
``GET  /api/schemes/eligibility`` — user-level SkillsFuture scheme eligibility by age

No auth required — the redesign tool is open so anyone can try it.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CareerMatch,
    CourseOut,
    MatchedCourseOut,
    RedesignRequest,
    RedesignResult,
    RedesignSuggestion,
    ResumeAnalysis,
    RoleListResponse,
    RoleOut,
    SchemeInfo,
    TaskWithScore,
)
from app.seed_data.role_taxonomy import list_categories, list_roles
from app.services.redesign_service import run_redesign
from app.services.resume_service import analyze_resume
from app.services.scheme_rules import get_user_schemes

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

    Calls the LLM to produce 2-3 directions, then matches each against
    SkillsFuture courses and funding schemes.  When ``target_role`` is
    supplied, generates a transition plan to that role instead.
    No auth required.
    """
    try:
        result = run_redesign(
            payload.role,
            db,
            age=payload.age,
            user_skills=payload.user_skills,
            target_role=payload.target_role,
        )
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
            transferable_skills=s.get("transferable_skills", []),
            skill_gaps=s.get("skill_gaps", []),
            matched_courses=matched,
        ))

    core_tasks = [TaskWithScore(**t) for t in result["role_core_tasks"]]

    return RedesignResult(
        role=result["role"],
        role_category=result["role_category"],
        role_core_tasks=core_tasks,
        target_role=result.get("target_role"),
        target_role_category=result.get("target_role_category"),
        suggestions=suggestions,
    )


@router.post("/resume/analyze", response_model=ResumeAnalysis)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """Analyse an uploaded resume PDF.

    Extracts skills via the LLM, then ranks suitable careers (including
    cross-industry options) with transferable skills and gaps per career.
    No auth required. The file is parsed in memory and never stored.
    """
    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    if file.content_type and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        result = analyze_resume(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        # API key not configured
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Resume analysis failed")
        raise HTTPException(status_code=502, detail=f"Resume analysis failed: {exc}")

    return ResumeAnalysis(
        skills=result["skills"],
        current_role_guess=result["current_role_guess"],
        career_matches=[CareerMatch(**m) for m in result["career_matches"]],
    )


@router.get("/schemes/eligibility", response_model=list[SchemeInfo])
def get_schemes_eligibility(age: int | None = Query(default=None, ge=0, le=120)):
    """Return user-level SkillsFuture scheme eligibility based on age.

    Course-independent: shows which national schemes the user could
    access at their age (credits, SCTP subsidy tier, Level-Up).
    """
    return [SchemeInfo(**s) for s in get_user_schemes(age)]
