"""Role redesign service — the core MVP flow.

Given a role title (from the taxonomy or free-text), this service:
1. Calls Claude (via ``agents.base.call_agent``) to generate 2-3
   AI-augmented redesign directions for that role.
2. Matches each direction's upskilling areas against SkillsFuture
   courses using keyword/skill overlap scoring.
3. For each matched course, determines which SkillsFuture funding
   schemes apply (using ``services.scheme_rules``).

The result is a structured payload that the frontend renders as
suggestion cards with matched courses and scheme badges.
"""

import logging
import re

from sqlalchemy.orm import Session

from app.agents.base import call_agent
from app.models import Course
from app.seed_data.role_taxonomy import get_role, search_roles
from app.services.scheme_rules import get_course_schemes

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """\
You are a career redesign advisor specialising in how AI transforms jobs \
in Singapore.

Given a job role and its core tasks, generate 2-3 concrete "AI-augmented \
redesign" directions.  Each direction should describe how the person could \
evolve their role by leveraging AI — not by replacing them, but by \
augmenting their capabilities, automating repetitive tasks, or opening \
new career pathways.

For each direction, return a JSON object with EXACTLY these fields:
{
  "title": "Short catchy name for this redesign direction (e.g. 'AI-Augmented Analyst')",
  "description": "1-2 sentences describing how the role changes with AI",
  "why": "1-2 sentences explaining why this direction makes sense given the role's tasks and current AI trends",
  "ai_impact": "One of: 'augment' (AI helps do existing tasks better), 'automate' (AI replaces some routine tasks), 'transform' (role fundamentally changes to something new)",
  "upskilling_areas": ["List of 3-5 specific skills or knowledge areas to develop"],
  "estimated_timeframe": "One of: '3-6 months', '6-12 months', '1-2 years'"
}

Guidelines:
- Be specific and practical, not generic. Reference the actual tasks of the role.
- Consider the Singapore job market and SkillsFuture-relevant skills.
- Vary the directions — don't just give variations of the same idea.
- Upskilling areas should be learnable through courses (e.g. 'Python', 'Data Visualisation', 'Prompt Engineering', 'Cloud Architecture').

Return a JSON array of 2-3 direction objects.  Return ONLY valid JSON, \
no markdown, no explanation."""


def generate_redesign_suggestions(
    role_title: str,
    core_tasks: list[str],
) -> list[dict]:
    """Call the LLM to generate 2-3 redesign suggestions for a role."""
    tasks_text = "\n".join(f"- {t}" for t in core_tasks) if core_tasks else "- (role tasks not specified)"

    user_message = (
        f"Role: {role_title}\n\n"
        f"Core tasks:\n{tasks_text}\n\n"
        f"Generate 2-3 AI-augmented redesign directions for this role. "
        f"Consider which tasks could be augmented, automated, or transformed by AI. "
        f"Focus on practical, actionable directions relevant to the Singapore job market.\n\n"
        f"Return only the JSON array."
    )

    result = call_agent(SYSTEM_PROMPT, user_message)

    if not isinstance(result, list):
        raise ValueError("LLM did not return a list of suggestions")

    validated: list[dict] = []
    for s in result:
        if not isinstance(s, dict) or "title" not in s or "upskilling_areas" not in s:
            logger.warning("Skipping malformed suggestion: %s", s)
            continue
        validated.append({
            "title": s.get("title", ""),
            "description": s.get("description", ""),
            "why": s.get("why", ""),
            "ai_impact": s.get("ai_impact", "augment"),
            "upskilling_areas": s.get("upskilling_areas", []),
            "estimated_timeframe": s.get("estimated_timeframe", "3-6 months"),
        })

    return validated[:3]  # cap at 3


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9+#]+", text.lower()) if len(t) > 2}


def match_courses_for_areas(
    upskilling_areas: list[str],
    courses: list[Course],
    limit: int = 5,
) -> list[tuple[Course, float, list[str]]]:
    """Match upskilling areas against courses using keyword/skill overlap."""
    area_tokens: set[str] = set()
    for area in upskilling_areas:
        area_tokens |= _tokenize(area)

    if not area_tokens:
        return []

    scored: list[tuple[Course, float, list[str]]] = []
    for course in courses:
        course_skills = {s.strip().lower() for s in course.skills.split(",") if s.strip()}
        course_tokens = _tokenize(f"{course.title} {course.category} {course.description}") | course_skills

        overlap = area_tokens & course_tokens
        if not overlap:
            continue

        score = len(overlap) / max(len(area_tokens), 1)
        matched = [s.strip() for s in course.skills.split(",") if s.strip().lower() in overlap]
        if not matched:
            matched = [t.title() for t in list(overlap)[:5]]

        scored.append((course, round(score, 3), matched))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:limit]


def run_redesign(role_input: str, db: Session, age: int | None = None) -> dict:
    """Full redesign flow: resolve role → LLM suggestions → match courses + schemes.

    ``role_input`` can be a role ID, a role title from the taxonomy, or
    free text.  If it doesn't match the taxonomy, the LLM still generates
    suggestions based on the raw input.
    """
    # 1 — resolve role from taxonomy
    role = get_role(role_input)
    if not role:
        matches = search_roles(role_input)
        if matches:
            role = matches[0]
        else:
            role = {
                "id": "custom",
                "title": role_input.strip(),
                "category": "General",
                "core_tasks": [],
            }

    logger.info("Redesign for role: %s (category: %s)", role["title"], role["category"])

    # 2 — generate LLM suggestions
    suggestions = generate_redesign_suggestions(role["title"], role["core_tasks"])

    # 3 — match courses + schemes for each suggestion
    courses = db.query(Course).all()
    for suggestion in suggestions:
        matched = match_courses_for_areas(suggestion["upskilling_areas"], courses)
        suggestion["matched_courses"] = [
            {
                "course": course,
                "match_score": score,
                "matched_skills": skills,
                "schemes": get_course_schemes(course, age=age),
            }
            for course, score, skills in matched
        ]

    return {
        "role": role["title"],
        "role_category": role["category"],
        "role_core_tasks": role["core_tasks"],
        "suggestions": suggestions,
    }
