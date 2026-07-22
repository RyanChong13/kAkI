from app.agents.base import call_agent

SYSTEM_PROMPT = """You are a resume parsing agent. Extract structured skills from the provided resume text.
Return ONLY a JSON array of skill objects. Each object must have exactly these fields:
- "skill": the skill name (string)
- "years": estimated years of experience as a number (float)
- "source": where the skill was identified (e.g., "work experience", "education", "certifications")

Return only valid JSON. No markdown, no explanation, no extra text."""


def parse_resume(raw_text: str) -> list:
    """Parse resume text into structured skills."""
    result = call_agent(SYSTEM_PROMPT, raw_text)
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "skills" in result:
        return result["skills"]
    raise ValueError("Resume parser returned unexpected format")
