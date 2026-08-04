"""Role redesign service — the core MVP flow.

Given a role title (from the taxonomy or free-text), this service:
1. Calls the LLM (via ``agents.base.call_agent``) to generate 2-3
   AI-augmented redesign directions for that role — or, when the user
   specifies a target role, a transition plan from their current role
   to the target.
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
from app.models import Course, SuggestionFeedback
from app.seed_data.role_taxonomy import get_role, get_role_task_titles, search_roles
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
- Language: write in plain, warm, everyday words. The reader is worried \
about their job's future — be reassuring and practical, never alarming. \
No jargon, acronyms or buzzwords (say "learn to build dashboards", not \
"leverage BI ecosystems"). Short sentences.

Return a JSON array of 2-3 direction objects.  Return ONLY valid JSON, \
no markdown, no explanation."""


PERSONALISED_ADDENDUM = """

The user has provided their resume skills. For EACH direction, add these \
extra fields to the JSON object:
- "transferable_skills": which of the user's EXISTING skills transfer \
directly to this direction (drawn from their skill list)
- "skill_gaps": the 2-4 most important skills they would need to learn

Also prioritise "upskilling_areas" that close these skill gaps."""


TRANSITION_SYSTEM_PROMPT = """\
You are a career transition advisor specialising in the Singapore job \
market and how AI is transforming jobs.

The user currently works in one role and wants to transition to a \
specific target role.  Given both roles' core tasks (and the user's \
skills if provided), generate 2-3 concrete transition pathways that \
leverage AI — ways AI lowers the barrier to the switch, skills that \
carry over, and practical steps to close the gaps.

For each pathway, return a JSON object with EXACTLY these fields:
{
  "title": "Short catchy name for this transition pathway (e.g. 'AI-Assisted Data Pivot')",
  "description": "1-2 sentences describing how the person moves into the target role using AI",
  "why": "1-2 sentences explaining why this pathway works given both roles' tasks",
  "ai_impact": "One of: 'augment' (AI helps bridge the gap), 'automate' (AI handles the tasks they can't do yet), 'transform' (AI creates an entirely new route into the target role)",
  "upskilling_areas": ["List of 3-5 specific skills to develop, focused on the target role's gaps"],
  "estimated_timeframe": "One of: '3-6 months', '6-12 months', '1-2 years'",
  "transferable_skills": ["Current-role tasks/skills (or the user's listed skills) that transfer directly to the target role"],
  "skill_gaps": ["The 2-4 most important target-role skills they would need to learn"]
}

Guidelines:
- Be specific and practical. Reference actual tasks of both roles.
- transferable_skills must come from the current role's tasks or the user's listed skills.
- Upskilling areas should be learnable through courses and prioritise closing the skill gaps.
- Vary the pathways — don't just give variations of the same idea.
- Language: write in plain, warm, everyday words. The reader is worried \
about their job's future — be reassuring and practical, never alarming. \
No jargon, acronyms or buzzwords. Short sentences.

Return a JSON array of 2-3 pathway objects.  Return ONLY valid JSON, \
no markdown, no explanation."""


def generate_redesign_suggestions(
    role_title: str,
    core_tasks: list[str],
    user_skills: list[str] | None = None,
    feedback_addendum: str = "",
) -> list[dict]:
    """Call the LLM to generate 2-3 redesign suggestions for a role.

    When ``user_skills`` is provided (from a resume analysis), suggestions
    are personalised with transferable skills and skill gaps.
    """
    tasks_text = "\n".join(f"- {t}" for t in core_tasks) if core_tasks else "- (role tasks not specified)"

    system_prompt = SYSTEM_PROMPT
    skills_section = ""
    if user_skills:
        system_prompt = SYSTEM_PROMPT + PERSONALISED_ADDENDUM
        skills_section = "\n\nUser's current skills (from their resume):\n- " + "\n- ".join(user_skills)
    if feedback_addendum:
        system_prompt = system_prompt + feedback_addendum

    user_message = (
        f"Role: {role_title}\n\n"
        f"Core tasks:\n{tasks_text}"
        f"{skills_section}\n\n"
        f"Generate 2-3 AI-augmented redesign directions for this role. "
        f"Consider which tasks could be augmented, automated, or transformed by AI. "
        f"Focus on practical, actionable directions relevant to the Singapore job market.\n\n"
        f"Return only the JSON array."
    )

    result = call_agent(system_prompt, user_message)

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
            "transferable_skills": [x for x in s.get("transferable_skills", []) if isinstance(x, str)],
            "skill_gaps": [x for x in s.get("skill_gaps", []) if isinstance(x, str)],
        })

    return validated[:3]  # cap at 3


def generate_transition_suggestions(
    current_title: str,
    current_tasks: list[str],
    target_title: str,
    target_tasks: list[str],
    user_skills: list[str] | None = None,
    feedback_addendum: str = "",
) -> list[dict]:
    """Call the LLM to generate 2-3 transition pathways current → target role."""
    current_text = "\n".join(f"- {t}" for t in current_tasks) if current_tasks else "- (tasks not specified)"
    target_text = "\n".join(f"- {t}" for t in target_tasks) if target_tasks else "- (tasks not specified)"

    system_prompt = TRANSITION_SYSTEM_PROMPT + feedback_addendum

    skills_section = ""
    if user_skills:
        skills_section = "\n\nUser's skills (from their resume):\n- " + "\n- ".join(user_skills)

    user_message = (
        f"Current role: {current_title}\n"
        f"Current role's core tasks:\n{current_text}\n\n"
        f"Target role: {target_title}\n"
        f"Target role's core tasks:\n{target_text}"
        f"{skills_section}\n\n"
        f"Generate 2-3 transition pathways from the current role to the target role. "
        f"Consider how AI can bridge the gap. Focus on practical, actionable "
        f"pathways relevant to the Singapore job market.\n\n"
        f"Return only the JSON array."
    )

    result = call_agent(system_prompt, user_message)

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
            "transferable_skills": [x for x in s.get("transferable_skills", []) if isinstance(x, str)],
            "skill_gaps": [x for x in s.get("skill_gaps", []) if isinstance(x, str)],
        })

    return validated[:3]  # cap at 3


def get_feedback_addendum(db: Session, role_title: str) -> str:
    """Build a prompt addendum from recent negative user feedback.

    Prioritises feedback for the same role, then falls back to recent
    global feedback.  Returns "" when there is no negative feedback yet.
    """
    same_role = (
        db.query(SuggestionFeedback)
        .filter(SuggestionFeedback.rating == "not_right", SuggestionFeedback.role == role_title)
        .order_by(SuggestionFeedback.created_at.desc())
        .limit(6)
        .all()
    )
    rows = same_role
    if len(rows) < 6:
        global_rows = (
            db.query(SuggestionFeedback)
            .filter(SuggestionFeedback.rating == "not_right")
            .order_by(SuggestionFeedback.created_at.desc())
            .limit(6)
            .all()
        )
        seen = {r.id for r in rows}
        rows = rows + [r for r in global_rows if r.id not in seen]

    if not rows:
        return ""

    lines = []
    for r in rows[:6]:
        note = r.comment.strip() if r.comment else "users said it didn't feel right for their role"
        lines.append(f"- \"{r.suggestion_title}\" ({r.role}): {note}")

    return (
        "\n\nPast user feedback — users felt these earlier suggestions missed "
        "the mark. Avoid similar directions:\n" + "\n".join(lines)
    )


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9+#]+", text.lower()) if len(t) > 2}


def match_courses_for_areas(
    upskilling_areas: list[str],
    courses: list[Course],
    limit: int = 5,
) -> list[tuple[Course, float, list[str]]]:
    """Match upskilling areas against courses using keyword/skill overlap.

    Returns (course, score, matched_areas) where *matched_areas* are the
    full upskilling-area phrases whose tokens overlap with the course.
    """
    # Tokenise each area individually so we can trace back which area matched
    area_token_maps: list[tuple[str, set[str]]] = []
    area_tokens_all: set[str] = set()
    for area in upskilling_areas:
        tokens = _tokenize(area)
        if tokens:
            area_token_maps.append((area, tokens))
            area_tokens_all |= tokens

    if not area_tokens_all:
        return []

    scored: list[tuple[Course, float, list[str]]] = []
    for course in courses:
        course_skills = {s.strip().lower() for s in course.skills.split(",") if s.strip()}
        course_tokens = _tokenize(f"{course.title} {course.category} {course.description}") | course_skills

        overlap = area_tokens_all & course_tokens
        if not overlap:
            continue

        score = len(overlap) / max(len(area_tokens_all), 1)

        # Show the full upskilling-area phrases that matched this course
        matched: list[str] = [
            area for area, area_tokens in area_token_maps
            if area_tokens & course_tokens
        ]

        scored.append((course, round(score, 3), matched[:5]))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:limit]


def _resolve_role(role_input: str) -> dict:
    """Resolve a role from the taxonomy by ID/title, else return a custom stub."""
    role = get_role(role_input)
    if role:
        return role
    matches = search_roles(role_input)
    if matches:
        return matches[0]
    return {
        "id": "custom",
        "title": role_input.strip(),
        "category": "General",
        "core_tasks": [],
    }


def run_redesign(
    role_input: str,
    db: Session,
    age: int | None = None,
    user_skills: list[str] | None = None,
    target_role: str | None = None,
) -> dict:
    """Full redesign flow: resolve role → LLM suggestions → match courses + schemes.

    ``role_input`` can be a role ID, a role title from the taxonomy, or
    free text.  If it doesn't match the taxonomy, the LLM still generates
    suggestions based on the raw input.

    When ``target_role`` is provided, the LLM generates a transition plan
    from the current role to the target instead of a redesign of the
    current role.

    When ``user_skills`` is provided (from resume analysis), suggestions are
    personalised with transferable skills and skill gaps.
    """
    # 1 — resolve roles from taxonomy
    role = _resolve_role(role_input)

    target = _resolve_role(target_role) if target_role and target_role.strip() else None
    if target and target["title"].lower() == role["title"].lower():
        target = None  # same role — fall back to a normal redesign

    logger.info(
        "Redesign for role: %s%s",
        role["title"],
        f" → target: {target['title']}" if target else "",
    )

    # 2 — generate LLM suggestions (transition plan or redesign)
    feedback_addendum = get_feedback_addendum(db, role["title"])
    if target:
        suggestions = generate_transition_suggestions(
            role["title"],
            get_role_task_titles(role),
            target["title"],
            get_role_task_titles(target),
            user_skills=user_skills,
            feedback_addendum=feedback_addendum,
        )
        core_tasks_out = target["core_tasks"]
    else:
        suggestions = generate_redesign_suggestions(
            role["title"],
            get_role_task_titles(role),
            user_skills=user_skills,
            feedback_addendum=feedback_addendum,
        )
        core_tasks_out = role["core_tasks"]

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
        "role_core_tasks": core_tasks_out,
        "target_role": target["title"] if target else None,
        "target_role_category": target["category"] if target else None,
        "suggestions": suggestions,
    }
