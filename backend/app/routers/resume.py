"""Resume upload and AI skill analysis endpoint."""

import re
from fastapi import APIRouter, Depends, File, UploadFile
from app.auth import get_current_user
from app.models import User
from app.schemas import ResumeAnalysisResult

router = APIRouter(prefix="/api/resume", tags=["resume"])

# Simple keyword-based skill extraction (mock AI)
_SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "TypeScript": r"\btypescript\b|\bts\b",
    "React": r"\breact\b",
    "Node.js": r"\bnode\.?js\b",
    "Java": r"\bjava\b(?!script)",
    "C++": r"\bc\+\+\b",
    "C#": r"\bc#\b|\bcsharp\b",
    "Go": r"\bgolang\b|\bgo\b",
    "Rust": r"\brust\b",
    "SQL": r"\bsql\b|\bmysql\b|\bpostgresql\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b",
    "Deep Learning": r"\bdeep learning\b|\bneural network\b",
    "Data Science": r"\bdata science\b|\bdata analys",
    "DevOps": r"\bdevops\b|\bci/cd\b|\bdocker\b|\bkubernetes\b",
    "Cloud": r"\bcloud\b|\baws\b|\bazure\b|\bgcp\b",
    "Cybersecurity": r"\bcybersecurity\b|\bsecurity\b|\bpentesting\b",
    "Project Management": r"\bproject management\b|\bpmp\b|\bscrum\b|\bagile\b",
    "UX Design": r"\bux\b|\bui design\b|\bfigma\b|\bdesign thinking\b",
    "Marketing": r"\bmarketing\b|\bseo\b|\bdigital marketing\b",
    "Leadership": r"\bleadership\b|\bteam lead\b|\bmanagement\b",
    "Public Speaking": r"\bpublic speaking\b|\bpresentation\b|\bcommunication\b",
    "Finance": r"\bfinance\b|\baccounting\b|\bfinancial\b",
    "Data Analysis": r"\bdata analysis\b|\bexcel\b|\btableau\b|\bpower bi\b",
    "Product Management": r"\bproduct management\b|\bproduct manager\b",
}

_INTEREST_PATTERNS = {
    "AI": r"\bai\b|\bartificial intelligence\b|\bmachine learning\b",
    "Software Engineering": r"\bsoftware\b|\bdevelop\b|\bprogramm\b|\bengineer\b",
    "Cybersecurity": r"\bcyber\b|\bsecur\b|\bhack\b",
    "Entrepreneurship": r"\bstartup\b|\bentrepreneur\b|\bfounder\b|\bbusiness\b",
    "Design": r"\bdesign\b|\bcreative\b|\bux\b|\bui\b",
    "Data Science": r"\bdata\b|\banalyt\b|\bstatistic\b",
    "Networking": r"\bnetwork\b|\bconnect\b|\bcommunity\b",
    "Leadership": r"\bleader\b|\bmanage\b|\bteam\b",
}


def _extract_text_from_pdf(content: bytes) -> str:
    """Basic text extraction - strips non-printable chars from raw PDF bytes."""
    # Try to decode as text first (for .txt files)
    try:
        return content.decode("utf-8", errors="ignore")
    except Exception:
        pass
    # For PDFs, extract readable ASCII sequences
    text = content.decode("latin-1", errors="ignore")
    # Remove PDF-specific noise
    text = re.sub(r"[%{}<>/\[\]\\]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _analyse_resume(text: str) -> ResumeAnalysisResult:
    """Mock AI analysis of resume text."""
    lower = text.lower()

    skills = [skill for skill, pattern in _SKILL_PATTERNS.items() if re.search(pattern, lower)]
    interests = [interest for interest, pattern in _INTEREST_PATTERNS.items() if re.search(pattern, lower)]

    # Guess experience years
    exp_match = re.search(r"(\d+)\+?\s*years?\s*(of|')?\s*(experience|exp|work)", lower)
    experience = float(exp_match.group(1)) if exp_match else None

    # Suggest event categories based on skills/interests
    categories = list(set(interests))[:6]
    if not categories:
        categories = ["AI", "Software Engineering", "Career Development"]

    # Build summary
    parts = []
    if skills:
        parts.append(f"Detected {len(skills)} skills: {', '.join(skills[:8])}")
    if experience:
        parts.append(f"Approximately {int(experience)} years of experience")
    if interests:
        parts.append(f"Interest areas: {', '.join(interests[:5])}")
    if not parts:
        parts.append("Upload a resume with more detail for better analysis")
    summary = ". ".join(parts) + "."

    return ResumeAnalysisResult(
        extracted_skills=skills,
        extracted_interests=interests,
        experience_years=experience,
        suggested_categories=categories,
        summary=summary,
    )


@router.post("/analyse", response_model=ResumeAnalysisResult)
async def analyse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    text = _extract_text_from_pdf(content)
    return _analyse_resume(text)
