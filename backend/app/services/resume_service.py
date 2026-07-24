"""Resume PDF parsing.

This is a lightweight, heuristic "AI parses the resume" step: it extracts
raw text with pypdf, then matches against a known skills taxonomy (built
from the seeded course/job skill tags) and regexes for a name and years of
experience. There's no LLM call involved - see README for how to swap this
for a real LLM-based extractor (e.g. sending `raw_text` to an LLM with a
structured-output prompt) without touching callers, since they only depend
on the `ParsedResume` shape returned by `parse_resume_pdf()`.
"""

import io
import re
from dataclasses import dataclass, field

from pypdf import PdfReader

from app.seed_data.jobs_seed import load_seeded_jobs
from app.seed_data.skillsfuture_courses import load_seeded_courses


def _build_skills_taxonomy() -> list[str]:
    skills: set[str] = set()
    for course in load_seeded_courses():
        skills.update(course.get("skills", []))
    for job in load_seeded_jobs():
        skills.update(job.get("skills_required", []))
    return sorted(skills, key=len, reverse=True)  # longest first avoids partial-match shadowing


SKILLS_TAXONOMY = _build_skills_taxonomy()

_YEARS_EXPERIENCE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience", re.IGNORECASE)


@dataclass
class ParsedResume:
    raw_text: str
    extracted_name: str = ""
    extracted_skills: list[str] = field(default_factory=list)
    years_experience_guess: float | None = None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _guess_name(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        words = stripped.split()
        if 1 < len(words) <= 4 and all(w[:1].isupper() for w in words if w[:1].isalpha()):
            return stripped
        break
    return ""


def _extract_skills(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for skill in SKILLS_TAXONOMY:
        if skill.lower() in lower and skill not in found:
            found.append(skill)
    return found


def _guess_years_experience(text: str) -> float | None:
    match = _YEARS_EXPERIENCE_RE.search(text)
    if match:
        return float(match.group(1))
    return None


def parse_resume_pdf(file_bytes: bytes) -> ParsedResume:
    text = extract_text_from_pdf(file_bytes)
    return ParsedResume(
        raw_text=text,
        extracted_name=_guess_name(text),
        extracted_skills=_extract_skills(text),
        years_experience_guess=_guess_years_experience(text),
    )
