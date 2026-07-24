from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Course, CourseSource, ResumeProfile, User
from app.schemas import CourseListResponse, CourseOut, CourseRecommendation, UpskillGoalIn
from app.services.course_service import get_provider_status, list_courses, refresh_all_sources
from app.services.matching_service import match_courses

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=CourseListResponse)
def get_courses(
    search: str | None = None,
    category: str | None = None,
    provider: str | None = None,
    max_price: float | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    source: CourseSource | None = None,
    db: Session = Depends(get_db),
):
    courses = list_courses(
        db,
        search=search,
        category=category,
        provider=provider,
        max_price=max_price,
        date_from=date_from,
        date_to=date_to,
        source=source,
    )
    eventbrite_available, eventbrite_notice = get_provider_status(CourseSource.EVENTBRITE.value)

    return CourseListResponse(
        items=[CourseOut.model_validate(c) for c in courses],
        total=len(courses),
        eventbrite_available=eventbrite_available,
        eventbrite_notice=eventbrite_notice,
    )


@router.get("/meta/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Course.category).distinct().order_by(Course.category).all()
    return [r[0] for r in rows]


@router.get("/meta/providers", response_model=list[str])
def get_providers(db: Session = Depends(get_db)):
    rows = db.query(Course.provider).distinct().order_by(Course.provider).all()
    return [r[0] for r in rows]


@router.post("/recommendations", response_model=list[CourseRecommendation])
def get_course_recommendations(
    payload: UpskillGoalIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Diagram step: user prompts AI with goal/time/cost/scope, AI recommends courses to choose from."""
    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == current_user.id).first()
    user_skills = [s.strip() for s in profile.extracted_skills.split(",")] if profile and profile.extracted_skills else []

    courses = list_courses(db)
    ranked = match_courses(payload.goal_text, payload.scope, user_skills, courses, max_cost_sgd=payload.max_cost_sgd)
    return [
        CourseRecommendation(course=CourseOut.model_validate(course), match_score=score, matched_skills=skills)
        for course, score, skills in ranked
    ]


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/refresh", response_model=CourseListResponse)
async def refresh_courses(db: Session = Depends(get_db)):
    """Manually trigger a refresh from all providers (also runs on a schedule)."""
    await refresh_all_sources(db)
    courses = list_courses(db)
    eventbrite_available, eventbrite_notice = get_provider_status(CourseSource.EVENTBRITE.value)
    return CourseListResponse(
        items=[CourseOut.model_validate(c) for c in courses],
        total=len(courses),
        eventbrite_available=eventbrite_available,
        eventbrite_notice=eventbrite_notice,
    )
