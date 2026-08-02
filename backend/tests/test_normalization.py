import asyncio
import json
from datetime import datetime

from app.config import get_settings
from app.models import Course, CourseSource
from app.providers.skillsfuture_provider import SkillsFutureProvider
from app.seed_data.skillsfuture_courses import load_seeded_courses
from app.services.course_service import _upsert_course
from app.services.skillsfuture_scraper import normalize_course, parse_rsc_stream


def run(coro):
    return asyncio.run(coro)


def _make_search_html(course: dict, description_text: str) -> str:
    """Build a minimal search-results HTML that embeds one course in the RSC
    payload, with its description stored as a `$31` reference chunk - mirroring
    the real courses.myskillsfuture.gov.sg markup."""
    obj = dict(course)
    obj["courseDescription"] = "$31"
    course_json = json.dumps(obj)
    desc_len = len(description_text.encode("utf-8"))
    stream = f"\n31:T{desc_len:x},{description_text}\n10:{course_json}\n"
    chunk = json.dumps(stream)  # JS string literal, incl. surrounding quotes
    return f"<html><body><script>self.__next_f.push([1,{chunk}])</script></body></html>"


SAMPLE_RAW_COURSE = {
    "courseRefNo": "TGS-2024049712",
    "courseSeoName": "Data-Science-and-AI",
    "courseTitle": "Advanced Certificate in Data Science and AI",
    "trainingProviderName": "NANYANG TECHNOLOGICAL UNIVERSITY",
    "trainingProviderAlias": "NTU",
    "areaOfTraining": ["Information and Communications"],
    "fullCostPerTrainee": 29600,
    "netCostPerTrainee": 8880,
    "courseSkills": ["Artificial Intelligence", "Data Analytics"],
}


class TestSkillsFutureScraper:
    def test_parse_rsc_stream_extracts_course_and_resolves_description(self):
        description = "Hands-on introduction to machine learning with Python."
        html = _make_search_html(SAMPLE_RAW_COURSE, description)

        parsed = parse_rsc_stream(html)

        assert len(parsed) == 1
        assert parsed[0]["courseRefNo"] == "TGS-2024049712"
        assert parsed[0]["courseTitle"] == SAMPLE_RAW_COURSE["courseTitle"]
        # The "$31" reference must be resolved to the actual description text.
        assert parsed[0]["courseDescription"] == description

    def test_parse_rsc_stream_deduplicates_by_ref(self):
        html = _make_search_html(SAMPLE_RAW_COURSE, "desc")
        # Two identical course blocks -> should be deduped to one.
        doubled = html + html
        assert len(parse_rsc_stream(doubled)) == 1

    def test_parse_rsc_stream_handles_empty_html(self):
        assert parse_rsc_stream("<html></html>") == []

    def test_normalize_course_maps_fields_and_credit(self):
        result = normalize_course(SAMPLE_RAW_COURSE)

        assert result["external_id"] == "TGS-2024049712"
        assert result["title"] == SAMPLE_RAW_COURSE["courseTitle"]
        assert result["provider"] == "NTU"  # alias preferred
        assert result["category"] == "Information and Communications"
        assert result["price_sgd"] == 8880  # estimated payable (net/subsidised) fee
        assert result["full_price_sgd"] == 29600  # full course fee before subsidy
        assert result["skillsfuture_credit_amount"] == 29600 - 8880  # subsidy amount
        assert result["skillsfuture_credit_eligible"] is True
        assert result["skills"] == ["Artificial Intelligence", "Data Analytics"]
        assert result["url"].endswith("/courses/TGS-2024049712--Data-Science-and-AI")


class TestSkillsFutureProviderFallback:
    def test_fetch_falls_back_to_seed_when_live_crawl_disabled(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("SKILLSFUTURE_LIVE_CRAWL", "false")

        result = run(SkillsFutureProvider().fetch())

        assert result.available is True
        assert len(result.courses) == len(load_seeded_courses())
        assert all(c.source == CourseSource.SKILLSFUTURE for c in result.courses)
        assert all(c.location == "Singapore" for c in result.courses)
        get_settings.cache_clear()


class TestCourseUpsert:
    def test_insert_then_update_same_external_id(self, db_session):
        from app.providers.base import NormalizedCourse

        item = NormalizedCourse(
            external_id="ev-1",
            source=CourseSource.SKILLSFUTURE,
            title="Original Title",
            provider="SkillsFuture",
            price_sgd=10.0,
            skills=["Networking"],
        )
        _upsert_course(db_session, item)
        db_session.commit()

        assert db_session.query(Course).count() == 1
        stored = db_session.query(Course).filter_by(external_id="ev-1").first()
        assert stored.title == "Original Title"
        assert stored.skills == "Networking"

        updated_item = NormalizedCourse(
            external_id="ev-1",
            source=CourseSource.SKILLSFUTURE,
            title="Updated Title",
            provider="SkillsFuture",
            price_sgd=15.0,
            skills=["Networking", "Career"],
        )
        _upsert_course(db_session, updated_item)
        db_session.commit()

        assert db_session.query(Course).count() == 1  # upsert, not duplicate insert
        stored = db_session.query(Course).filter_by(external_id="ev-1").first()
        assert stored.title == "Updated Title"
        assert stored.price_sgd == 15.0
        assert stored.skills == "Networking, Career"
