from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Course, SavedCourse, User
from app.schemas import SavedCourseOut

router = APIRouter(prefix="/api/saved-courses", tags=["saved-courses"])


@router.get("", response_model=list[SavedCourseOut])
def list_saved(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(SavedCourse).filter(SavedCourse.user_id == current_user.id).all()


@router.post("/{course_id}", response_model=SavedCourseOut, status_code=201)
def save_course(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(SavedCourse)
        .filter(SavedCourse.user_id == current_user.id, SavedCourse.course_id == course_id)
        .first()
    )
    if existing:
        return existing

    saved = SavedCourse(user_id=current_user.id, course_id=course_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.delete("/{course_id}", status_code=204)
def unsave_course(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = (
        db.query(SavedCourse)
        .filter(SavedCourse.user_id == current_user.id, SavedCourse.course_id == course_id)
        .first()
    )
    if saved:
        db.delete(saved)
        db.commit()
    return None
