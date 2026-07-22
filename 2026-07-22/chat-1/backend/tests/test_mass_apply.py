"""Test mass apply — preview assembly and confirm flow."""
import pytest
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobSuggestion
from app.models.session import FlowSession, FlowPath, FlowStatus
from app.models.grant import Grant
from app.agents.mass_apply import assemble_preview, confirm_and_submit
from app.utils.auth import hash_password


def _setup(db):
    user = User(
        email="apply@test.com", hashed_password=hash_password("pass"),
        name="Apply User", age=30, sector="technology", income_band="medium", grant_history=[],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    resume = Resume(user_id=user.id, raw_text="test", parsed_skills=[{"skill": "Python", "years": 5, "source": "work"}])
    db.add(resume)

    session = FlowSession(user_id=user.id, path=FlowPath.redeployment, round_number=1, status=FlowStatus.active)
    db.add(session)
    db.commit()
    db.refresh(session)

    job = JobSuggestion(session_id=session.id, title="Python Developer", matched_skills=["Python"], missing_skills=[], round_number=1)
    db.add(job)

    grant = Grant(name="Test Grant", amount=1000.0, cap_remaining=50, eligibility_criteria={})
    db.add(grant)
    db.commit()

    return user, session, job, grant


def test_assemble_preview_jobs(db):
    """Preview assembly for job applications."""
    user, session, job, _ = _setup(db)
    result = assemble_preview(db, user.id, session.id, "job", [job.id])
    assert "preview_id" in result
    assert len(result["items"]) == 1
    assert result["items"][0]["target_name"] == "Python Developer"


def test_assemble_preview_grants(db):
    """Preview assembly for grant applications."""
    user, session, _, grant = _setup(db)
    result = assemble_preview(db, user.id, session.id, "grant", [grant.id])
    assert "preview_id" in result
    assert len(result["items"]) == 1
    assert result["items"][0]["target_name"] == "Test Grant"


def test_confirm_and_submit(db):
    """Confirming a preview creates applications with audit snapshots."""
    user, session, job, _ = _setup(db)
    preview = assemble_preview(db, user.id, session.id, "job", [job.id])
    applications = confirm_and_submit(db, preview["preview_id"])
    assert len(applications) == 1
    assert applications[0]["target_name"] == "Python Developer"


def test_confirm_without_preview_fails(db):
    """Confirming a non-existent preview raises error."""
    with pytest.raises(ValueError, match="Preview not found"):
        confirm_and_submit(db, "nonexistent-id")


def test_batch_size_limit(db):
    """Batch exceeding max size raises error."""
    user, session, _, _ = _setup(db)
    with pytest.raises(ValueError, match="exceeds maximum"):
        assemble_preview(db, user.id, session.id, "job", list(range(100)))
