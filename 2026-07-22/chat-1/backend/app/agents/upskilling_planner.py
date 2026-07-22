import json
from app.agents.base import call_agent

SYSTEM_PROMPT = """You are an upskilling planner agent. Based on the user's goal, constraints, and current skills, recommend relevant courses.
Return ONLY a JSON object with this exact structure:
{
  "course_suggestions": [
    {
      "name": "Course name",
      "provider": "Provider name",
      "duration": "e.g. 3 months",
      "cost": "e.g. $500",
      "skill_gap_addressed": "The skill gap this course fills"
    }
  ]
}

Return only valid JSON. No markdown, no explanation, no extra text."""


def plan_upskilling(goal: str, constraints: dict, skills: list) -> dict:
    """Generate course recommendations based on goal, constraints, and skills."""
    user_msg = json.dumps({
        "goal": goal,
        "constraints": constraints,
        "current_skills": skills,
    })
    result = call_agent(SYSTEM_PROMPT, user_msg)
    if not isinstance(result, dict) or "course_suggestions" not in result:
        raise ValueError("Upskilling planner returned unexpected format")
    return result
