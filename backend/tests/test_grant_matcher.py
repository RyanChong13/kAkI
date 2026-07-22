"""Test the grant matcher rules engine — deterministic eligibility matching."""
import pytest
from app.agents.grant_matcher import match_grants
from app.models.grant import Grant


def test_match_grants_eligible(db):
    """User meeting all criteria should see eligible grants."""
    grant = Grant(
        name="Test Grant",
        amount=1000.0,
        cap_remaining=100,
        eligibility_criteria={
            "min_age": 20,
            "max_age": 60,
            "sectors": ["technology"],
            "income_bands": ["low", "medium"],
            "max_prior_grants": 5,
        },
    )
    db.add(grant)
    db.commit()
    db.refresh(grant)

    user_profile = {
        "age": 35,
        "sector": "technology",
        "income_band": "medium",
        "grant_history": ["grant_a"],
    }

    result = match_grants(db, user_profile, "Test Course")
    assert "eligible_grants" in result
    assert len(result["eligible_grants"]) == 1
    assert result["eligible_grants"][0]["name"] == "Test Grant"
    assert result["eligible_grants"][0]["amount"] == 1000.0


def test_match_grants_age_ineligible(db):
    """User outside age range should not see grant."""
    grant = Grant(
        name="Age Restricted Grant",
        amount=500.0,
        cap_remaining=50,
        eligibility_criteria={"min_age": 25, "max_age": 40},
    )
    db.add(grant)
    db.commit()

    user_profile = {"age": 50, "sector": "technology", "income_band": "medium", "grant_history": []}
    result = match_grants(db, user_profile, "Any Course")
    assert len(result["eligible_grants"]) == 0


def test_match_grants_sector_ineligible(db):
    """User in wrong sector should not see grant."""
    grant = Grant(
        name="Tech Only Grant",
        amount=2000.0,
        cap_remaining=200,
        eligibility_criteria={"sectors": ["technology"]},
    )
    db.add(grant)
    db.commit()

    user_profile = {"age": 30, "sector": "retail", "income_band": "low", "grant_history": []}
    result = match_grants(db, user_profile, "Any Course")
    assert len(result["eligible_grants"]) == 0


def test_match_grants_cap_exhausted(db):
    """Grant with no remaining cap should not appear."""
    grant = Grant(
        name="Exhausted Grant",
        amount=1000.0,
        cap_remaining=0,
        eligibility_criteria={},
    )
    db.add(grant)
    db.commit()

    user_profile = {"age": 30, "sector": "technology", "income_band": "medium", "grant_history": []}
    result = match_grants(db, user_profile, "Any Course")
    assert len(result["eligible_grants"]) == 0


def test_match_grants_prior_grants_exceeded(db):
    """User who has exceeded max prior grants should not see grant."""
    grant = Grant(
        name="Limited Grant",
        amount=1500.0,
        cap_remaining=100,
        eligibility_criteria={"max_prior_grants": 2},
    )
    db.add(grant)
    db.commit()

    user_profile = {
        "age": 30,
        "sector": "technology",
        "income_band": "medium",
        "grant_history": ["g1", "g2"],
    }
    result = match_grants(db, user_profile, "Any Course")
    assert len(result["eligible_grants"]) == 0
