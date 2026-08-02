from app.agents.base import call_agent

SYSTEM_PROMPT = """You are a resume parsing agent. Extract structured skills AND previous job roles from the provided resume text.
Return ONLY a JSON object with exactly these fields:
{
  "skills": [
    {
      "skill": "the skill name (string)",
      "years": "estimated years of experience as a number (float)",
      "source": "where the skill was identified (e.g., work experience, education, certifications)"
    }
  ],
  "previous_roles": ["List of previous job titles/roles held, e.g. Senior Software Engineer, Team Lead"]
}

Extract ALL distinct job titles the candidate has held from the work experience section.
Return only valid JSON. No markdown, no explanation, no extra text."""


def parse_resume(raw_text: str) -> dict:
    """Parse resume text into structured skills and previous roles.

    Returns a dict with keys 'skills' (list) and 'previous_roles' (list).
    Backward compatible: if the LLM returns just an array, treats it as skills-only.
    """
    result = call_agent(SYSTEM_PROMPT, raw_text)
    # Backward compatibility: plain array means skills only
    if isinstance(result, list):
        return {"skills": result, "previous_roles": []}
    if isinstance(result, dict):
        skills = result.get("skills", [])
        previous_roles = result.get("previous_roles", [])
        return {"skills": skills, "previous_roles": previous_roles}
    raise ValueError("Resume parser returned unexpected format")
