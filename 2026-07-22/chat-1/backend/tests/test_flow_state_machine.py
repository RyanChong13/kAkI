"""Test the flow state machine — round limits, exit state, no 3rd round."""
import pytest
from app.models.user import User
from app.models.session import FlowSession, FlowPath, FlowStatus
from app.services import flow_service
from app.utils.auth import hash_password


def _create_user(db):
    user = User(
        email="test@example.com",
        hashed_password=hash_password("test123"),
        name="Test User",
        age=30,
        sector="technology",
        income_band="medium",
        grant_history=[],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_start_flow(db):
    """Starting a flow creates an active session at round 1."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    assert session.status == FlowStatus.active
    assert session.round_number == 1
    assert session.path == FlowPath.redeployment


def test_liked_round1_proceeds_to_apply(db):
    """Liking jobs in round 1 should proceed to apply."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    result = flow_service.handle_job_feedback(db, session, liked=True)
    assert result["action"] == "proceed_to_apply"


def test_disliked_round1_redirects_to_upskilling(db):
    """Disliking round 1 jobs should redirect to upskilling (round 2)."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    result = flow_service.handle_job_feedback(db, session, liked=False)
    assert result["action"] == "redirect_to_upskilling"
    assert result["round"] == 2


def test_disliked_round2_exits(db):
    """Disliking round 2 jobs should trigger exit state — no 3rd round."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    # Dislike round 1 -> redirect to upskilling
    flow_service.handle_job_feedback(db, session, liked=False)
    db.refresh(session)
    assert session.round_number == 2
    # Dislike round 2 -> exit
    result = flow_service.handle_job_feedback(db, session, liked=False)
    assert result["action"] == "exit"
    db.refresh(session)
    assert session.status == FlowStatus.exited


def test_no_third_round_possible(db):
    """Even if somehow called again, a terminated session won't generate more rounds."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    flow_service.handle_job_feedback(db, session, liked=False)
    db.refresh(session)
    flow_service.handle_job_feedback(db, session, liked=False)
    db.refresh(session)
    assert session.status == FlowStatus.exited
    # Try to give feedback again on exited session
    result = flow_service.handle_job_feedback(db, session, liked=True)
    assert result["action"] == "error"


def test_complete_application_round1(db):
    """Completing application in round 1 sets status to applied_round_1."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    result = flow_service.complete_application(db, session)
    assert result["status"] == "applied_round_1"


def test_complete_application_round2(db):
    """Completing application in round 2 sets status to applied_round_2."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    flow_service.handle_job_feedback(db, session, liked=False)
    db.refresh(session)
    result = flow_service.complete_application(db, session)
    assert result["status"] == "applied_round_2"


def test_terminal_state_detection(db):
    """is_session_terminal returns True for ended sessions."""
    user = _create_user(db)
    session = flow_service.start_flow(db, user.id, "redeployment")
    assert not flow_service.is_session_terminal(db, session)
    flow_service.complete_application(db, session)
    assert flow_service.is_session_terminal(db, session)
