from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pypdf import PdfReader
import io
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas import ResumeResponse
from app.utils.auth import get_current_user
from app.agents.resume_parser import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text() or ""

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    try:
        parsed_skills = parse_resume(raw_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

    resume = Resume(
        user_id=current_user.id,
        raw_text=raw_text,
        parsed_skills=parsed_skills,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/me", response_model=Optional[ResumeResponse])
def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    return resume
