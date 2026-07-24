"""Rule-based matching ("AI will recommend jobs" / "AI will recommend courses" in the diagram).

Uses skill-overlap and keyword scoring rather than a hosted LLM, so the app
works fully offline with no external AI API key. See README for how to swap
in a real LLM-based recommender: it would take the same inputs (resume
skills / goal text, candidate list) and just needs to return the same
`(item, score, matched_skills)` shape consumed by the routers.
"""

import re

from app.models import Course, Job


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9\+\#]+", text.lower()) if len(t) > 2}


def _skill_set(comma_separated: str) -> set[str]:
    return {s.strip().lower() for s in comma_separated.split(",") if s.strip()}


def match_jobs(user_skills: list[str], jobs: list[Job], limit: int = 10) -> list[tuple[Job, float, list[str]]]:
    user_skill_set = {s.strip().lower() for s in user_skills if s.strip()}
    scored = []

    for job in jobs:
        job_skills = _skill_set(job.skills_required)
        if not job_skills:
            continue
        overlap = user_skill_set & job_skills
        score = len(overlap) / len(job_skills) if job_skills else 0.0
        if score > 0:
            matched = [s for s in job.skills_required.split(",") if s.strip().lower() in overlap]
            scored.append((job, round(score, 3), [m.strip() for m in matched]))

    scored.sort(key=lambda t: t[1], reverse=True)
    if scored:
        return scored[:limit]

    # Cold start (no resume skills matched): surface newest/general roles instead of an empty page.
    return [(job, 0.0, []) for job in jobs[:limit]]


def match_courses(
    goal_text: str,
    scope: str,
    user_skills: list[str],
    courses: list[Course],
    max_cost_sgd: float | None = None,
    limit: int = 10,
) -> list[tuple[Course, float, list[str]]]:
    goal_tokens = _tokenize(f"{goal_text} {scope}")
    user_skill_set = {s.strip().lower() for s in user_skills if s.strip()}
    scored = []

    for course in courses:
        if max_cost_sgd is not None and course.price_sgd > max_cost_sgd:
            continue

        course_skill_set = _skill_set(course.skills)
        course_tokens = _tokenize(f"{course.title} {course.category} {course.description}") | course_skill_set

        keyword_overlap = goal_tokens & course_tokens
        skill_overlap = user_skill_set & course_skill_set

        keyword_score = len(keyword_overlap) / max(len(goal_tokens), 1)
        skill_score = len(skill_overlap) / len(course_skill_set) if course_skill_set else 0.0
        score = 0.7 * keyword_score + 0.3 * skill_score

        if score > 0:
            matched = [s for s in course.skills.split(",") if s.strip().lower() in (keyword_overlap | skill_overlap)]
            scored.append((course, round(score, 3), [m.strip() for m in matched]))

    scored.sort(key=lambda t: t[1], reverse=True)
    if scored:
        return scored[:limit]

    fallback = [c for c in courses if max_cost_sgd is None or c.price_sgd <= max_cost_sgd]
    return [(c, 0.0, []) for c in fallback[:limit]]
