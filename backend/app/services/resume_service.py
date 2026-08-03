"""Resume analysis service — Phase 2.

Flow: upload PDF → extract text (pypdf) → LLM extracts skills and guesses
the current role → hybrid matching ranks suitable careers from the role
taxonomy, flagging transferable skills and gaps per career.

Hybrid matching:
1. **Rule layer** — token-overlap scoring of the extracted skills against
   each taxonomy role's ``task_keywords`` (+ task text) to build a bounded
   candidate pool.
2. **LLM layer** — given the candidates, the model ranks the top matches
   and reasons about transferable skills, gaps, and fit.  If the LLM call
   fails, deterministic rule-based results are returned instead.

Nothing is persisted — the resume is parsed in memory only.
"""

import io
import logging
import re

from pypdf import PdfReader

from app.agents.base import call_agent, call_agent_with_images
from app.seed_data.role_taxonomy import (
    ROLE_TAXONOMY,
    get_role,
    get_role_task_titles,
    search_roles,
)

logger = logging.getLogger(__name__)

MAX_RESUME_CHARS = 20_000  # cap text sent to the LLM
MAX_SKILLS = 25
CANDIDATE_POOL = 12
FINAL_MATCHES = 6
MAX_VISION_PAGES = 3  # scanned-PDF fallback: pages rendered to images


# ── PDF text extraction ─────────────────────────────────────────────────────

def extract_text(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes. Raises ValueError for bad files.

    Multi-page PDFs are supported (all pages are concatenated).  If the
    PDF has no selectable text (e.g. a scan), falls back to a vision-LLM
    transcription of the rendered pages.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:
        raise ValueError("Could not read this file. Please upload a valid PDF resume.") from exc

    pages = [(page.extract_text() or "") for page in reader.pages]
    text = re.sub(r"\s+", " ", "\n".join(pages)).strip()

    if len(text) < 40:
        # Likely a scanned/image-only PDF — try vision transcription
        text = _transcribe_scanned_pdf(pdf_bytes)

    return text[:MAX_RESUME_CHARS]


TRANSCRIBE_SYSTEM_PROMPT = """\
You are transcribing an image of a person's resume.

Return a JSON object with EXACTLY this field:
{
  "text": "the full transcribed text of the resume, preserving sections and bullet points"
}

Transcribe everything visible: name, contact details, summary, work
experience, education, skills, certifications.  If the image is not a
resume or is unreadable, return {"text": ""}.
"""


def _transcribe_scanned_pdf(pdf_bytes: bytes) -> str:
    """Render the first few pages of a scanned PDF to images and transcribe them.

    Raises ValueError with a friendly message if transcription is not
    possible or yields nothing.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ValueError(
            "This PDF appears to be a scanned image. "
            "Please upload a resume with selectable text."
        )

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[bytes] = []
        for page in doc[:MAX_VISION_PAGES]:
            pix = page.get_pixmap(dpi=150)
            images.append(pix.tobytes("png"))
        doc.close()
    except Exception as exc:
        raise ValueError(
            "Could not read this file. Please upload a valid PDF resume."
        ) from exc

    if not images:
        raise ValueError(
            "This PDF appears to be empty. Please upload a resume with your details."
        )

    logger.info("Scanned PDF detected — transcribing %d page image(s) via vision LLM", len(images))
    try:
        result = call_agent_with_images(
            TRANSCRIBE_SYSTEM_PROMPT,
            "Transcribe the text of this resume.",
            images,
        )
    except RuntimeError:
        raise  # No OpenAI key — surfaced as 503 by the router
    except Exception as exc:
        logger.warning("Vision transcription failed: %s", exc)
        raise ValueError(
            "This PDF appears to be a scanned image and could not be read. "
            "Please upload a resume with selectable text."
        ) from exc

    text = re.sub(r"\s+", " ", str(result.get("text", ""))).strip() if isinstance(result, dict) else ""
    if len(text) < 40:
        raise ValueError(
            "This PDF appears to be a scanned image and no resume text could "
            "be found. Please upload a resume with selectable text."
        )
    return text


# ── LLM skill extraction ────────────────────────────────────────────────────

SKILL_SYSTEM_PROMPT = """\
You are a resume analyst for the Singapore job market.

Given the raw text of a resume, extract:
1. The person's skills — hard and soft skills, tools, and domain knowledge.
2. Their most likely current (or most recent) job title.

Return a JSON object with EXACTLY these fields:
{
  "skills": ["skill 1", "skill 2", ...],
  "current_role_guess": "Most likely current job title"
}

Guidelines:
- Extract between 8 and 20 skills, prioritising specific, resume-worthy skills
  (e.g. "Python", "Financial Reporting", "Project Management", "Customer Service").
- Normalise skills to common short phrases (no long sentences).
- Include both technical and soft skills, but prioritise technical/domain skills.
- If the resume has no clear job title, guess from the experience described.

Return ONLY valid JSON, no markdown, no explanation."""


def extract_skills(resume_text: str) -> dict:
    """LLM call: resume text → skills list + current role guess."""
    result = call_agent(
        SKILL_SYSTEM_PROMPT,
        f"Resume text:\n\n{resume_text}",
    )

    if isinstance(result, list):
        result = {"skills": result, "current_role_guess": ""}
    if not isinstance(result, dict):
        raise ValueError("Skill extraction returned an unexpected format")

    skills = [s.strip() for s in result.get("skills", []) if isinstance(s, str) and s.strip()]
    return {
        "skills": skills[:MAX_SKILLS],
        "current_role_guess": str(result.get("current_role_guess", "")).strip(),
    }


# ── Rule layer: skill → role overlap scoring ────────────────────────────────

def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9+#/.]+", text.lower()) if len(t) > 2}


def _skill_tokens(skills: list[str]) -> set[str]:
    tokens: set[str] = set()
    for s in skills:
        tokens |= _tokenize(s)
    return tokens


def score_roles_by_skills(skills: list[str]) -> list[tuple[dict, float, list[str]]]:
    """Score every taxonomy role against the user's skills.

    Returns ``[(role, score, matched_keywords)]`` sorted by score desc,
    where score = fraction of the user's skill tokens the role uses.
    """
    user_tokens = _skill_tokens(skills)
    if not user_tokens:
        return []

    scored: list[tuple[dict, float, list[str]]] = []
    for role in ROLE_TAXONOMY:
        keyword_text = " ".join(role.get("task_keywords", []))
        task_text = " ".join(get_role_task_titles(role))
        role_tokens = _tokenize(keyword_text) | _tokenize(task_text)

        overlap = user_tokens & role_tokens
        if not overlap:
            continue

        score = len(overlap) / len(user_tokens)
        matched = [kw for kw in role.get("task_keywords", [])
                   if _tokenize(kw) & overlap]
        scored.append((role, round(score, 3), matched))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored


# ── LLM layer: career matching with transferable-skill reasoning ────────────

MATCH_SYSTEM_PROMPT = """\
You are a career transition advisor for the Singapore job market.

A user has uploaded their resume. You are given their extracted skills and a
shortlist of candidate careers (each with its core tasks). Rank the careers
that best suit this person — including careers in DIFFERENT industries where
their skills would transfer well.

For each recommended career, return a JSON object with EXACTLY these fields:
{
  "role_id": "the candidate's role_id",
  "fit_score": integer 0-100 (how well the user's skills fit this career),
  "reason": "1-2 sentences explaining why this career suits them",
  "transferable_skills": ["which of the user's EXISTING skills transfer directly to this career"],
  "skill_gaps": ["key skills the user would need to learn for this career"]
}

Guidelines:
- Return between 4 and 6 careers, best fit first.
- transferable_skills MUST be drawn from the user's skill list (same or lightly rephrased).
- skill_gaps should reference the candidate career's core tasks (2-4 gaps).
- Prefer a mix: at least one same-industry option and at least one cross-industry
  option when the skills plausibly transfer.
- Be realistic — a fit_score above 85 should only be given to very strong matches.

Return ONLY a JSON array, no markdown, no explanation."""


def _current_category(skills: list[str], current_role_guess: str) -> str:
    """Best-effort guess of the user's current industry category."""
    if current_role_guess:
        role = get_role(current_role_guess)
        if not role:
            matches = search_roles(current_role_guess, limit=1)
            if matches:
                role = matches[0]
        if role:
            return role["category"]
    # Fallback: category of the top rule-scored role
    scored = score_roles_by_skills(skills)
    if scored:
        return scored[0][0]["category"]
    return ""


def match_careers(skills: list[str], current_role_guess: str) -> list[dict]:
    """Hybrid career matching: rule-based candidates → LLM ranking."""
    scored = score_roles_by_skills(skills)
    current_category = _current_category(skills, current_role_guess)

    if not scored:
        return []

    candidates = [role for role, _, _ in scored[:CANDIDATE_POOL]]
    rule_score_by_id = {role["id"]: score for role, score, _ in scored}
    rule_matched_by_id = {role["id"]: matched for role, _, matched in scored}

    try:
        matches = _llm_rank_candidates(skills, candidates)
    except (RuntimeError, ValueError) as exc:
        # RuntimeError = no API key; ValueError = bad LLM output.
        # Fall back to pure rule-based matches so the feature still works.
        if isinstance(exc, RuntimeError):
            raise  # surface missing-key error to the caller
        logger.warning("LLM career matching failed, using rule-based fallback: %s", exc)
        matches = _rule_based_matches(skills, scored)

    # Enrich + cap, compute industry_switch deterministically
    enriched: list[dict] = []
    for m in matches[:FINAL_MATCHES]:
        role = get_role(m.get("role_id", ""))
        if not role:
            continue
        enriched.append({
            "role_id": role["id"],
            "role_title": role["title"],
            "category": role["category"],
            "fit_score": int(m.get("fit_score", 0)),
            "reason": str(m.get("reason", "")),
            "transferable_skills": list(m.get("transferable_skills", [])),
            "skill_gaps": list(m.get("skill_gaps", [])),
            "industry_switch": bool(current_category) and role["category"] != current_category,
        })

    if not enriched:
        enriched = _rule_based_matches(skills, scored)[:FINAL_MATCHES]
        for m in enriched:
            m["industry_switch"] = bool(current_category) and m["category"] != current_category

    return enriched


def _llm_rank_candidates(skills: list[str], candidates: list[dict]) -> list[dict]:
    """Send the candidate pool to the LLM for ranking + reasoning."""
    candidate_blocks = []
    for role in candidates:
        tasks = "\n".join(f"  - {t}" for t in get_role_task_titles(role))
        candidate_blocks.append(
            f"role_id: {role['id']}\n"
            f"title: {role['title']} ({role['category']})\n"
            f"core tasks:\n{tasks}"
        )

    user_message = (
        f"User's skills:\n- " + "\n- ".join(skills) + "\n\n"
        f"Candidate careers:\n\n" + "\n\n".join(candidate_blocks) + "\n\n"
        f"Rank the best 4-6 careers for this user. Return only the JSON array."
    )

    result = call_agent(MATCH_SYSTEM_PROMPT, user_message)
    if not isinstance(result, list) or not result:
        raise ValueError("Career matching LLM returned no matches")

    validated: list[dict] = []
    for m in result:
        if not isinstance(m, dict) or not m.get("role_id"):
            continue
        validated.append({
            "role_id": str(m["role_id"]),
            "fit_score": max(0, min(100, int(m.get("fit_score", 50)))),
            "reason": str(m.get("reason", "")),
            "transferable_skills": [s for s in m.get("transferable_skills", []) if isinstance(s, str)],
            "skill_gaps": [s for s in m.get("skill_gaps", []) if isinstance(s, str)],
        })
    if not validated:
        raise ValueError("Career matching LLM returned no valid matches")

    validated.sort(key=lambda m: m["fit_score"], reverse=True)
    return validated


def _rule_based_matches(skills: list[str], scored: list[tuple[dict, float, list[str]]]) -> list[dict]:
    """Deterministic fallback when the LLM ranking is unavailable."""
    user_tokens = _skill_tokens(skills)
    matches: list[dict] = []
    for role, score, matched_keywords in scored[:FINAL_MATCHES]:
        transferable = [s for s in skills if _tokenize(s) & _tokenize(" ".join(role.get("task_keywords", [])))] or matched_keywords
        gaps = [kw for kw in role.get("task_keywords", []) if not (_tokenize(kw) & user_tokens)][:4]
        fit = min(95, 30 + round(score * 100))
        matches.append({
            "role_id": role["id"],
            "role_title": role["title"],
            "category": role["category"],
            "fit_score": fit,
            "reason": f"Your skills overlap with the core work of a {role['title']} "
                      f"({', '.join(matched_keywords[:4])}).",
            "transferable_skills": transferable[:6],
            "skill_gaps": gaps,
            "industry_switch": False,  # enriched by caller
        })
    return matches


# ── Top-level entrypoint ────────────────────────────────────────────────────

def analyze_resume(pdf_bytes: bytes) -> dict:
    """Full resume analysis: text → skills → career matches."""
    text = extract_text(pdf_bytes)
    logger.info("Resume text extracted — %d chars", len(text))

    info = extract_skills(text)
    logger.info("Extracted %d skills; current role guess: %s",
                len(info["skills"]), info["current_role_guess"] or "(none)")

    matches = match_careers(info["skills"], info["current_role_guess"])
    logger.info("Career matching produced %d matches", len(matches))

    return {
        "skills": info["skills"],
        "current_role_guess": info["current_role_guess"],
        "career_matches": matches,
    }
