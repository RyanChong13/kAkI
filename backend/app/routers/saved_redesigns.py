"""Saved redesign plans — per-user persistence (Phase 5)."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import SavedRedesign, User
from app.schemas import SavedRedesignCreate, SavedRedesignOut

router = APIRouter(prefix="/api/saved-redesigns", tags=["saved-redesigns"])


@router.get("", response_model=list[SavedRedesignOut])
def list_saved(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all saved redesigns for the logged-in user, newest first."""
    rows = (
        db.query(SavedRedesign)
        .filter(SavedRedesign.user_id == current_user.id)
        .order_by(SavedRedesign.created_at.desc())
        .all()
    )
    return [_row_to_out(r) for r in rows]


@router.post("", response_model=SavedRedesignOut, status_code=status.HTTP_201_CREATED)
def create_saved(
    payload: SavedRedesignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a redesign result to the user's account."""
    row = SavedRedesign(
        user_id=current_user.id,
        client_id=payload.client_id,
        role=payload.role,
        target_role=payload.target_role,
        age=payload.age,
        user_skills=json.dumps(payload.user_skills),
        result_json=json.dumps(payload.result),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_out(row)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saved redesign. Only the owner can delete their own plans."""
    row = db.get(SavedRedesign, plan_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Saved plan not found")
    db.delete(row)
    db.commit()


# ── helpers ────────────────────────────────────────────────────────────────────

def _row_to_out(row: SavedRedesign) -> SavedRedesignOut:
    """Convert a SavedRedesign DB row to a SavedRedesignOut schema instance."""
    return SavedRedesignOut(
        id=row.id,
        client_id=row.client_id,
        role=row.role,
        target_role=row.target_role,
        age=row.age,
        user_skills=json.loads(row.user_skills) if row.user_skills else [],
        result=json.loads(row.result_json),
        created_at=row.created_at,
    )
