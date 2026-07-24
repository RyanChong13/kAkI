import asyncio
from datetime import datetime

from app.models import Course, CourseSource
from app.providers.eventbrite_provider import EventbriteProvider
from app.providers.skillsfuture_provider import SkillsFutureProvider
from app.seed_data.skillsfuture_courses import load_seeded_courses
from app.services.course_service import _upsert_course


def run(coro):
    return asyncio.run(coro)


class TestSkillsFutureNormalization:
    def test_returns_a_course_per_seed_entry(self):
        result = run(SkillsFutureProvider().fetch())
        assert result.available is True
        assert len(result.courses) == len(load_seeded_courses())

    def test_normalized_fields_match_source(self):
        result = run(SkillsFutureProvider().fetch())
        first = next(c for c in result.courses if c.external_id == "sf-001")
        raw = load_seeded_courses()[0]

        assert first.source == CourseSource.SKILLSFUTURE
        assert first.title == raw["title"]
        assert first.provider == raw["provider"]
        assert first.price_sgd == raw["price_sgd"]
        assert first.skillsfuture_credit_eligible == raw["skillsfuture_credit_eligible"]
        assert first.skills == raw["skills"]  # provider keeps skills as a list; DB layer joins it
        assert first.location == "Singapore"


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
