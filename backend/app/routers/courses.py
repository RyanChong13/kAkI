from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Course, CourseSource
from app.schemas import CourseListResponse, CourseOut
from app.services.course_service import list_courses, refresh_all_sources

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
    return CourseListResponse(
        items=[CourseOut.model_validate(c) for c in courses],
        total=len(courses),
    )


@router.get("/meta/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Course.category).distinct().order_by(Course.category).all()
    return [r[0] for r in rows]


@router.get("/meta/providers", response_model=list[str])
def get_providers(db: Session = Depends(get_db)):
    rows = db.query(Course.provider).distinct().order_by(Course.provider).all()
    return [r[0] for r in rows]


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
    return CourseListResponse(
        items=[CourseOut.model_validate(c) for c in courses],
        total=len(courses),
    )
