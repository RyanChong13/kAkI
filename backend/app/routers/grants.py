from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Course, GrantApplication, User
from app.schemas import CourseOut, GrantApplicationOut, GrantMassApplyIn

router = APIRouter(prefix="/api/grants", tags=["grants"])


@router.get("/available")
def get_available_grants(course_ids: list[int] = Query(...), db: Session = Depends(get_db)):
    """Given a set of selected courses, return the SkillsFuture Credit each is eligible for.

    Mirrors the diagram step "AI will recommend and show the available grants
    that they can get" - grants here are the courses' SkillsFuture Credit
    eligibility, since that's the real, well-defined SG upskilling subsidy.
    """
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
    return [
        {
            "course": CourseOut.model_validate(c),
            "credit_amount_sgd": c.skillsfuture_credit_amount if c.skillsfuture_credit_eligible else 0.0,
            "eligible": c.skillsfuture_credit_eligible,
        }
        for c in courses
    ]


@router.post("/mass-apply", response_model=list[GrantApplicationOut])
def mass_apply_grants(payload: GrantMassApplyIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.id.in_(payload.course_ids)).all()
    found_ids = {c.id for c in courses}
    missing = set(payload.course_ids) - found_ids
    if missing:
        raise HTTPException(status_code=404, detail=f"Course(s) not found: {sorted(missing)}")

    courses_by_id = {c.id: c for c in courses}
    created = []
    for course_id in payload.course_ids:
        existing = (
            db.query(GrantApplication)
            .filter(GrantApplication.user_id == current_user.id, GrantApplication.course_id == course_id)
            .first()
        )
        if existing:
            created.append(existing)
            continue
        course = courses_by_id[course_id]
        grant_app = GrantApplication(
            user_id=current_user.id,
            course_id=course_id,
            credit_amount_sgd=course.skillsfuture_credit_amount if course.skillsfuture_credit_eligible else 0.0,
        )
        db.add(grant_app)
        created.append(grant_app)

    db.commit()
    for row in created:
        db.refresh(row)
    return created


@router.get("", response_model=list[GrantApplicationOut])
def list_grant_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(GrantApplication).filter(GrantApplication.user_id == current_user.id).all()
