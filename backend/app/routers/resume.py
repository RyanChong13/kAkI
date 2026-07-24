from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ResumeProfile, User
from app.schemas import ResumeProfileOut
from app.services.resume_service import parse_resume_pdf

router = APIRouter(prefix="/api/resume", tags=["resume"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=ResumeProfileOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    try:
        parsed = parse_resume_pdf(file_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF. Please try a different file.")

    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == current_user.id).first()
    skills_str = ", ".join(parsed.extracted_skills)

    if profile:
        profile.filename = file.filename
        profile.raw_text = parsed.raw_text
        profile.extracted_skills = skills_str
        profile.extracted_name = parsed.extracted_name
        profile.years_experience_guess = parsed.years_experience_guess
    else:
        profile = ResumeProfile(
            user_id=current_user.id,
            filename=file.filename,
            raw_text=parsed.raw_text,
            extracted_skills=skills_str,
            extracted_name=parsed.extracted_name,
            years_experience_guess=parsed.years_experience_guess,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me", response_model=ResumeProfileOut)
def get_my_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")
    return profile
