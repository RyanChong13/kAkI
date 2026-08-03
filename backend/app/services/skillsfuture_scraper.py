"""Live crawler for the MySkillsFuture course directory.

Scrapes the public course search results at
https://courses.myskillsfuture.gov.sg/search . That site is a Next.js app
that server-renders each results page and embeds the full course data for
that page inside its React Server Component (RSC) payload
(the `self.__next_f.push([...])` script chunks in the HTML).

Strategy:
  - The "browse all" page only returns a handful of featured courses, and
    search requires a real keyword, so we crawl a curated list of broad
    seed queries (see `Settings.skillsfuture_crawl_queries`) and paginate
    each one (`?q=<term>&page=<n>`), deduplicating by course reference number.
  - Each page embeds ~9 courses. We stop paginating a term early once a page
    yields no new courses.
  - Long text fields (description, objective) are RSC references like "$31"
    that point to separate `31:T<hexlen>,<text>` chunks; we resolve them.

Pure functions (`parse_rsc_stream`, `normalize_course`) are separated from
the network layer (`crawl`) so they can be unit-tested offline.

If anything fails, the caller (`SkillsFutureProvider`) falls back to the
seeded dataset, so the app degrades gracefully and never crashes on a flaky
third party.
"""

import asyncio
import json
import logging
import re

import httpx

from app.config import get_settings
from app.services.scheme_rules import tag_scheme_eligibility

logger = logging.getLogger(__name__)

SEARCH_URL = "https://courses.myskillsfuture.gov.sg/search"
COURSE_URL_TEMPLATE = "https://courses.myskillsfuture.gov.sg/courses/{ref}--{seo}"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Overall safety cap so a misconfiguration can't crawl forever.
TOTAL_COURSE_CAP = 2000

_PUSH_CHUNK_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')
_REF_DEF_RE = re.compile(r"(?:^|\n)(\d+):T([0-9a-f]+),")
_COURSE_REF_RE = re.compile(r'"courseRefNo"')
_json_decoder = json.JSONDecoder()


# ---------------------------------------------------------------------------
# Pure parsing (no network) - unit-testable
# ---------------------------------------------------------------------------

def _concat_rsc_stream(html: str) -> str:
    """Join and unescape all __next_f RSC string chunks in the page HTML."""
    chunks = _PUSH_CHUNK_RE.findall(html)
    parts = []
    for c in chunks:
        try:
            parts.append(json.loads('"' + c + '"'))
        except json.JSONDecodeError:
            continue
    return "".join(parts)


def _build_ref_map(stream: str) -> dict[str, str]:
    """Map RSC reference ids (e.g. "31") to their resolved text value.

    Text chunks are encoded as `<id>:T<hexlen>,<text>` where hexlen is the
    UTF-8 byte length of the text that immediately follows the comma.
    """
    ref_map: dict[str, str] = {}
    encoded = stream.encode("utf-8")
    for m in _REF_DEF_RE.finditer(stream):
        rid = m.group(1)
        length = int(m.group(2), 16)
        # Slice by byte length from the char offset just after the comma.
        byte_start = len(stream[: m.end()].encode("utf-8"))
        text = encoded[byte_start : byte_start + length].decode("utf-8", "ignore")
        ref_map[rid] = text.strip().strip('"').strip()
    return ref_map


def _resolve_ref(value, ref_map: dict[str, str]):
    if isinstance(value, str) and value.startswith("$"):
        return ref_map.get(value[1:], "")
    return value


def parse_rsc_stream(html: str) -> list[dict]:
    """Extract raw course dicts from a search-results page's HTML.

    Returns the courses in document order, de-duplicated by courseRefNo,
    with description/objective references resolved to their text.
    """
    stream = _concat_rsc_stream(html)
    if not stream:
        return []
    ref_map = _build_ref_map(stream)

    courses: list[dict] = []
    seen: set[str] = set()
    for m in _COURSE_REF_RE.finditer(stream):
        start = stream.rfind("{", 0, m.start())
        if start == -1:
            continue
        try:
            obj, _ = _json_decoder.raw_decode(stream[start:])
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or "courseRefNo" not in obj:
            continue
        ref = obj["courseRefNo"]
        if not ref or ref in seen:
            continue
        seen.add(ref)
        for field in ("courseDescription", "courseObjective"):
            if field in obj:
                obj[field] = _resolve_ref(obj[field], ref_map)
        courses.append(obj)
    return courses


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_course(raw: dict) -> dict:
    """Map a raw crawled course dict into the shape the provider expects."""
    ref = str(raw.get("courseRefNo", "")).strip()
    seo = str(raw.get("courseSeoName", "")).strip()

    provider = (
        str(raw.get("trainingProviderAlias") or "").strip()
        or str(raw.get("trainingProviderName") or "").strip()
        or "SkillsFuture Training Provider"
    )

    area = raw.get("areaOfTraining")
    category = area[0] if isinstance(area, list) and area else "SkillsFuture"

    full_fee = _to_float(raw.get("fullCostPerTrainee"))
    net_fee = _to_float(raw.get("netCostPerTrainee"))
    # price_sgd = estimated payable fee (after subsidy) for display consistency
    price = net_fee if net_fee else full_fee
    subsidy = max(full_fee - net_fee, 0.0)

    skills = raw.get("courseSkills")
    skills = [s for s in skills if s] if isinstance(skills, list) else []

    description = (str(raw.get("courseDescription") or "").strip()
                  or str(raw.get("courseObjective") or "").strip())

    url = COURSE_URL_TEMPLATE.format(ref=ref, seo=seo) if ref else ""

    schemes = tag_scheme_eligibility(full_fee, None)  # duration unknown from search results

    return {
        "external_id": ref,
        "title": str(raw.get("courseTitle", "")).strip(),
        "provider": provider,
        "category": category,
        "description": description[:2000],
        "duration_hours": None,  # portal expresses duration as a band, not hours
        "price_sgd": round(price, 2),  # estimated payable after subsidy
        "full_price_sgd": round(full_fee, 2),  # full course fee before subsidy
        "skillsfuture_credit_eligible": True,
        "skillsfuture_credit_amount": round(subsidy, 2),  # subsidy amount
        **schemes,
        "skills": skills[:10],
        "url": url,
    }


# ---------------------------------------------------------------------------
# Network layer
# ---------------------------------------------------------------------------

async def _fetch_page(client: httpx.AsyncClient, query: str, page: int) -> list[dict]:
    """Fetch and parse a single search-results page."""
    resp = await client.get(SEARCH_URL, params={"q": query, "page": page})
    resp.raise_for_status()
    return parse_rsc_stream(resp.text)


async def _crawl_query(
    client: httpx.AsyncClient, query: str, max_pages: int, known_refs: set[str]
) -> list[dict]:
    """Paginate one query term, stopping early once a page adds nothing new."""
    collected: list[dict] = []
    for page in range(1, max_pages + 1):
        try:
            raw_courses = await _fetch_page(client, query, page)
        except Exception as exc:
            logger.warning("SkillsFuture crawl '%s' page %d failed: %s", query, page, exc)
            break

        new_this_page = 0
        for raw in raw_courses:
            ref = raw.get("courseRefNo")
            if not ref or ref in known_refs:
                continue
            known_refs.add(ref)
            collected.append(raw)
            new_this_page += 1

        if new_this_page == 0:
            break  # exhausted this term
    return collected


async def crawl() -> list[dict]:
    """Crawl the live course directory and return normalized course dicts."""
    settings = get_settings()
    queries = settings.skillsfuture_crawl_query_list
    max_pages = settings.skillsfuture_crawl_max_pages
    concurrency = max(1, settings.skillsfuture_crawl_concurrency)

    known_refs: set[str] = set()
    normalized: list[dict] = []
    semaphore = asyncio.Semaphore(concurrency)

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    async with httpx.AsyncClient(
        headers=headers, timeout=30.0, follow_redirects=True
    ) as client:

        async def run_query(q: str) -> list[dict]:
            async with semaphore:
                return await _crawl_query(client, q, max_pages, known_refs)

        results = await asyncio.gather(*(run_query(q) for q in queries), return_exceptions=True)

    for res in results:
        if isinstance(res, Exception):
            logger.warning("SkillsFuture crawl query task failed: %s", res)
            continue
        for raw in res:
            normalized.append(normalize_course(raw))
            if len(normalized) >= TOTAL_COURSE_CAP:
                break
        if len(normalized) >= TOTAL_COURSE_CAP:
            break

    logger.info("SkillsFuture live crawl produced %d unique courses", len(normalized))
    return normalized
