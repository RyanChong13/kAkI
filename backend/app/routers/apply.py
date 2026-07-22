from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.application import Application
from app.schemas import ApplyPreviewRequest, ApplyConfirmRequest, ApplicationResponse
from app.utils.auth import get_current_user
from app.services import flow_service
from app.agents.mass_apply import assemble_preview, confirm_and_submit

router = APIRouter(prefix="/apply", tags=["apply"])


@router.post("/preview")
def get_preview(
    data: ApplyPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    if data.type not in ("job", "grant"):
        raise HTTPException(status_code=400, detail="Type must be 'job' or 'grant'")

    try:
        result = assemble_preview(db, current_user.id, session.id, data.type, data.target_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.post("/confirm")
def confirm_batch(
    data: ApplyConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Server-side enforcement: confirmed must be True
    if not data.confirmed:
        raise HTTPException(status_code=400, detail="You must explicitly confirm the batch to submit")

    session = flow_service.get_active_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    try:
        applications = confirm_and_submit(db, data.preview_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Mark session as complete
    flow_service.complete_application(db, session)

    return {"submitted": len(applications), "status": "complete"}


@router.get("/history", response_model=List[ApplicationResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    return apps
