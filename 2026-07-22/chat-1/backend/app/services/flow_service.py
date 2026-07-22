"""Flow Orchestration Service — State machine for the user journey.
Enforces max 2 rounds, proper path transitions, and terminal exit state."""

from sqlalchemy.orm import Session
from app.models.session import FlowSession, FlowPath, FlowStatus
from app.models.user import User

MAX_ROUNDS = 2


def start_flow(db: Session, user_id: int, path: str) -> FlowSession:
    """Create a new flow session."""
    # Close any existing active sessions
    active = db.query(FlowSession).filter(
        FlowSession.user_id == user_id,
        FlowSession.status == FlowStatus.active,
    ).all()
    for s in active:
        s.status = FlowStatus.exited
        db.add(s)

    session = FlowSession(
        user_id=user_id,
        path=FlowPath(path),
        round_number=1,
        status=FlowStatus.active,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_active_session(db: Session, user_id: int) -> FlowSession | None:
    """Get the current active session for a user."""
    return db.query(FlowSession).filter(
        FlowSession.user_id == user_id,
        FlowSession.status == FlowStatus.active,
    ).first()


def handle_job_feedback(db: Session, session: FlowSession, liked: bool) -> dict:
    """Process user feedback on job suggestions and determine next step."""
    if session.status != FlowStatus.active:
        return {"action": "error", "message": "Session is not active"}

    if liked:
        # User likes the jobs -> proceed to mass-apply
        return {
            "action": "proceed_to_apply",
            "round": session.round_number,
            "message": "Select jobs to apply for.",
        }
    else:
        # User dislikes the jobs
        if session.round_number >= MAX_ROUNDS:
            # Exit state — terminal, no more rounds
            session.status = FlowStatus.exited
            db.add(session)
            db.commit()
            return {
                "action": "exit",
                "message": "You have reached the maximum number of recommendation rounds.",
                "resources": [
                    {"name": "Workforce Singapore (WSG)", "url": "https://www.wsg.gov.sg"},
                    {"name": "e2i", "url": "https://www.e2i.com.sg"},
                ],
            }
        else:
            # Move to upskilling path (round 2)
            session.round_number = 2
            session.path = FlowPath.upskilling
            db.add(session)
            db.commit()
            return {
                "action": "redirect_to_upskilling",
                "round": 2,
                "message": "Explore upskilling options to expand your opportunities.",
            }


def complete_application(db: Session, session: FlowSession) -> dict:
    """Mark session as completed after successful application."""
    if session.round_number == 1:
        session.status = FlowStatus.applied_round_1
    else:
        session.status = FlowStatus.applied_round_2
    db.add(session)
    db.commit()
    return {"status": session.status.value}


def is_session_terminal(db: Session, session: FlowSession) -> bool:
    """Check if the session is in a terminal state."""
    return session.status in (
        FlowStatus.applied_round_1,
        FlowStatus.applied_round_2,
        FlowStatus.exited,
    )
