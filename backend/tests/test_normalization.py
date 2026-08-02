import asyncio
import json
from datetime import datetime

from app.config import get_settings
from app.models import Course, CourseSource
from app.providers.eventbrite_provider import EventbriteProvider
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
        assert result["price_sgd"] == 8880  # net (subsidised) fee
        assert result["skillsfuture_credit_amount"] == 29600 - 8880
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


class TestEventbriteNormalization:
    def test_normalize_paid_event_extracts_price_and_location(self):
        event = {
            "id": "123456",
            "name": {"text": "Intro to Product Management Workshop"},
            "summary": "A hands-on workshop for aspiring PMs.",
            "start": {"local": "2026-08-15T09:00:00"},
            "venue": {"address": {"localized_area_display": "Downtown Core, Singapore"}},
            "is_free": False,
            "ticket_availability": {"minimum_ticket_price": {"major_value": "45.00", "currency": "SGD"}},
            "url": "https://www.eventbrite.sg/e/123456",
            "logo": {"url": "https://img.evbuc.com/example.jpg"},
        }

        normalized = EventbriteProvider._normalize(event)

        assert normalized is not None
        assert normalized.external_id == "123456"
        assert normalized.source == CourseSource.EVENTBRITE
        assert normalized.title == "Intro to Product Management Workshop"
        assert normalized.price_sgd == 45.0
        assert normalized.location == "Downtown Core, Singapore"
        assert normalized.date == datetime.fromisoformat("2026-08-15T09:00:00")
        assert normalized.category == "Workshop"
        assert normalized.provider == "Eventbrite"

    def test_normalize_free_event_has_zero_price(self):
        event = {
            "id": "999",
            "name": {"text": "Free Networking Mixer"},
            "is_free": True,
            "url": "https://www.eventbrite.sg/e/999",
        }

        normalized = EventbriteProvider._normalize(event)

        assert normalized is not None
        assert normalized.price_sgd == 0.0
        assert normalized.location == "Singapore"  # falls back when no venue given

    def test_normalize_malformed_event_returns_none_instead_of_raising(self):
        # Missing required "id" key should be handled gracefully, not crash the batch.
        event = {"name": {"text": "Broken Event"}}
        assert EventbriteProvider._normalize(event) is None

    def test_fetch_without_token_returns_unavailable_with_notice(self, monkeypatch):
        from app.config import get_settings

        get_settings.cache_clear()
        monkeypatch.setenv("EVENTBRITE_PRIVATE_TOKEN", "")

        result = run(EventbriteProvider().fetch())

        assert result.available is False
        assert result.courses == []
        assert result.notice is not None
        get_settings.cache_clear()


class TestCourseUpsert:
    def test_insert_then_update_same_external_id(self, db_session):
        from app.providers.base import NormalizedCourse

        item = NormalizedCourse(
            external_id="ev-1",
            source=CourseSource.EVENTBRITE,
            title="Original Title",
            provider="Eventbrite",
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
            source=CourseSource.EVENTBRITE,
            title="Updated Title",
            provider="Eventbrite",
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
