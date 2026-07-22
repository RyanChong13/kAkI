"""Grant Matcher — Rules/filter engine, NOT an LLM agent.
Deterministic eligibility matching based on user profile and grant criteria."""

from sqlalchemy.orm import Session
from app.models.grant import Grant


def match_grants(db: Session, user_profile: dict, course_name: str) -> dict:
    """Match user to eligible grants based on deterministic criteria filtering."""
    grants = db.query(Grant).all()
    eligible = []

    for grant in grants:
        criteria = grant.eligibility_criteria or {}

        # Age check
        if "min_age" in criteria and user_profile.get("age") is not None:
            if user_profile["age"] < criteria["min_age"]:
                continue
        if "max_age" in criteria and user_profile.get("age") is not None:
            if user_profile["age"] > criteria["max_age"]:
                continue

        # Sector check
        if "sectors" in criteria and user_profile.get("sector"):
            if user_profile["sector"] not in criteria["sectors"]:
                continue

        # Income band check
        if "income_bands" in criteria and user_profile.get("income_band"):
            if user_profile["income_band"] not in criteria["income_bands"]:
                continue

        # Prior grant usage check
        if "max_prior_grants" in criteria:
            prior_count = len(user_profile.get("grant_history", []))
            if prior_count >= criteria["max_prior_grants"]:
                continue

        # Cap remaining check
        if grant.cap_remaining <= 0:
            continue

        eligible.append({
            "grant_id": grant.id,
            "name": grant.name,
            "amount": float(grant.amount),
            "cap_remaining": grant.cap_remaining,
        })

    return {"eligible_grants": eligible}
