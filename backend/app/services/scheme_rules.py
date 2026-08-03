"""SkillsFuture funding scheme rules engine.

Defines the four main SkillsFuture schemes and their eligibility rules.
Scheme rules change every Budget cycle — update the constants here when
they change.  Course-level eligibility is tagged heuristically during
data ingestion (see ``skillsfuture_scraper.normalize_course``); user-
level eligibility (age, citizenship) is applied here at query time.

Disclaimer: These are heuristic estimates for a prototype.  Real
eligibility must always be verified on MySkillsFuture.
"""

SCHEMES: list[dict] = [
    {
        "id": "base_credit",
        "name": "SkillsFuture Credit",
        "credit_amount_sgd": 500,
        "min_age": 25,
        "description": (
            "Opening credits of $500 (given in 2016) plus a $500 top-up "
            "(announced in Budget 2025).  Available to all Singapore "
            "Citizens aged 25 and above."
        ),
        "eligibility_notes": (
            "Singapore Citizens aged 25+.  No income cap.  "
            "Can be used for SSG-supported courses on MySkillsFuture."
        ),
        "official_url": "https://www.myskillsfuture.gov.sg/content/portal/en/portal-landing.html",
    },
    {
        "id": "mid_career",
        "name": "Mid-Career Credit",
        "credit_amount_sgd": 4000,
        "min_age": 40,
        "description": (
            "Additional $4,000 SkillsFuture Credit (Budget 2024) for "
            "mid-career Singaporeans to access selected courses for "
            "career transition.  Stacks on top of base Credit."
        ),
        "eligibility_notes": (
            "Singapore Citizens aged 40+.  "
            "Usable on selected courses marked Mid-Career eligible."
        ),
        "official_url": "https://www.myskillsfuture.gov.sg/content/portal/en/portal-landing.html",
    },
    {
        "id": "sctp",
        "name": "SkillsFuture Career Transition Programme (SCTP)",
        "credit_amount_sgd": None,
        "min_age": None,
        "description": (
            "Career transition programmes with higher course fee subsidies "
            "(up to 90% for those aged 40+).  Designed for mid-career "
            "switches into growth sectors."
        ),
        "eligibility_notes": (
            "Singapore Citizens and PRs.  Subsidy rates: up to 70% (under 40), "
            "up to 90% (aged 40+).  No age floor but higher subsidy for 40+."
        ),
        "official_url": "https://www.myskillsfuture.gov.sg/content/portal/en/training-exchange/sctp.html",
    },
    {
        "id": "level_up",
        "name": "SkillsFuture Level-Up Programme",
        "credit_amount_sgd": None,
        "min_age": 40,
        "description": (
            "Monthly training allowance of $3,000 (up to 24 months) for "
            "selected full-time courses, plus a $4,000 top-up credit.  "
            "For mid-career Singaporeans pursuing substantive re-skilling."
        ),
        "eligibility_notes": (
            "Singapore Citizens aged 40+.  Must enrol in a selected "
            "full-time programme.  Allowance is $3,000/month for up to 24 months."
        ),
        "official_url": "https://www.myskillsfuture.gov.sg/content/portal/en/skillsfuture-level-up.html",
    },
]

_SCHEME_FIELD_MAP = {
    "base_credit": "base_credit_eligible",
    "mid_career": "mid_career_eligible",
    "sctp": "sctp_eligible",
    "level_up": "level_up_eligible",
}


def get_course_schemes(course, age: int | None = None) -> list[dict]:
    """Return scheme eligibility for a given course.

    Uses the course's pre-tagged eligibility fields and applies age
    requirements when ``age`` is provided.  Returns a list of scheme
    dicts with an ``eligible`` flag and user-specific notes.
    """
    results: list[dict] = []
    for scheme in SCHEMES:
        course_eligible = _is_course_eligible(course, scheme["id"])
        if not course_eligible:
            continue

        age_eligible = True
        age_note = ""
        if age is not None and scheme["min_age"] is not None:
            if age < scheme["min_age"]:
                age_eligible = False
                age_note = f"Requires age {scheme['min_age']}+; you are {age}."
            else:
                age_note = f"You meet the age requirement ({scheme['min_age']}+)."
        elif scheme["min_age"] is not None:
            age_note = f"Requires age {scheme['min_age']}+."

        results.append({
            "scheme_id": scheme["id"],
            "scheme_name": scheme["name"],
            "eligible": age_eligible,
            "credit_amount_sgd": scheme["credit_amount_sgd"],
            "description": scheme["description"],
            "eligibility_notes": scheme["eligibility_notes"],
            "age_note": age_note,
            "official_url": scheme["official_url"],
        })
    return results


def _is_course_eligible(course, scheme_id: str) -> bool:
    """Check if a course is tagged as eligible for a given scheme."""
    field = _SCHEME_FIELD_MAP.get(scheme_id)
    if not field:
        return False
    return getattr(course, field, False)


def tag_scheme_eligibility(full_fee: float, duration_hours: float | None) -> dict:
    """Heuristically tag which schemes a course is likely eligible for.

    Called during data ingestion (scraper / seed data) to populate the
    four boolean fields on the Course model.  These are rough estimates
    based on course attributes; real eligibility must be verified on
    MySkillsFuture.

    Heuristics:
    - **base_credit**: all courses from MySkillsFuture are assumed
      SSG-supported and therefore base-credit eligible.
    - **mid_career**: courses with full fee >= $500 (higher-value
      courses tend to be Mid-Career eligible).
    - **sctp**: courses with duration >= 100h OR full fee >= $2,000
      (SCTP courses are typically comprehensive programmes).
    - **level_up**: cannot be determined from search results; defaults
      to False (must be checked on MySkillsFuture).
    """
    return {
        "base_credit_eligible": True,
        "mid_career_eligible": full_fee >= 500.0,
        "sctp_eligible": (duration_hours is not None and duration_hours >= 100) or full_fee >= 2000.0,
        "level_up_eligible": False,
    }
