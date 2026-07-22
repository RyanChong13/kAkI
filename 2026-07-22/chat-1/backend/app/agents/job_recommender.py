import json
from app.agents.base import call_agent

SYSTEM_PROMPT = """You are a job recommendation agent. Based on the provided skills and background, suggest relevant job opportunities.
Return ONLY a JSON object with this exact structure:
{
  "job_suggestions": [
    {
      "title": "Job title",
      "matched_skills": ["skill1", "skill2"],
      "missing_skills": ["skill3"]
    }
  ]
}

Do not include reassurance, encouragement, or motivational language. Be factual and direct.
Return only valid JSON. No markdown, no explanation, no extra text."""


def recommend_jobs(skills: list, survey_data: dict | None = None) -> dict:
    """Generate job recommendations based on parsed skills."""
    user_msg = json.dumps({"skills": skills, "survey": survey_data or {}})
    result = call_agent(SYSTEM_PROMPT, user_msg)
    if not isinstance(result, dict) or "job_suggestions" not in result:
        raise ValueError("Job recommender returned unexpected format")
    return result
