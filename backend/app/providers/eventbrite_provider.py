"""Eventbrite live event provider.

Calls the Eventbrite v3 API (https://www.eventbrite.com/platform/api) filtered
to Singapore, and normalizes results into `NormalizedCourse` objects tagged
with category "Workshop" (or Eventbrite's own category name when available).

Caveats, documented here rather than hidden:
  - Requires `EVENTBRITE_PRIVATE_TOKEN` in the environment (see .env.example).
    Without it, `fetch()` returns `available=False` with a friendly notice
    instead of raising, so the rest of the app degrades gracefully.
  - Eventbrite restricted public keyword/location search (`/v3/events/search/`)
    to select partners in 2020. If your token doesn't have search access,
    Eventbrite returns 403/404 and this provider surfaces that as an
    `available=False` notice rather than crashing the course listing page.
  - All network failures (timeout, DNS, 5xx) are caught and degrade the same
    way - a flaky third party should never take down the rest of the app.
"""

from datetime import datetime

import httpx

from app.config import get_settings
from app.models import CourseSource
from app.providers.base import CourseProvider, NormalizedCourse, ProviderResult

EVENTBRITE_SEARCH_URL = "https://www.eventbriteapi.com/v3/events/search/"


class EventbriteProvider(CourseProvider):
    source = CourseSource.EVENTBRITE

    async def fetch(self) -> ProviderResult:
        settings = get_settings()

        if not settings.eventbrite_configured:
            return ProviderResult(
                courses=[],
                available=False,
                notice=(
                    "Eventbrite integration is not configured. Add EVENTBRITE_PRIVATE_TOKEN "
                    "to backend/.env to show live Singapore workshops here."
                ),
            )

        params = {
            "location.address": "Singapore",
            "location.within": "50km",
            "expand": "venue,ticket_availability",
        }
        headers = {"Authorization": f"Bearer {settings.eventbrite_private_token}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(EVENTBRITE_SEARCH_URL, params=params, headers=headers)
        except httpx.RequestError as exc:
            return ProviderResult(
                courses=[], available=False, notice=f"Could not reach Eventbrite ({exc.__class__.__name__}). Showing SkillsFuture courses only."
            )

        if resp.status_code == 401:
            return ProviderResult(courses=[], available=False, notice="Eventbrite token is invalid or expired. Showing SkillsFuture courses only.")
        if resp.status_code in (403, 404):
            return ProviderResult(
                courses=[],
                available=False,
                notice="This Eventbrite token doesn't have access to event search. Showing SkillsFuture courses only.",
            )
        if resp.status_code >= 400:
            return ProviderResult(
                courses=[], available=False, notice=f"Eventbrite returned an error (HTTP {resp.status_code}). Showing SkillsFuture courses only."
            )

        try:
            data = resp.json()
        except ValueError:
            return ProviderResult(courses=[], available=False, notice="Eventbrite returned an unexpected response. Showing SkillsFuture courses only.")

        events = data.get("events", [])
        courses = [self._normalize(e) for e in events]
        courses = [c for c in courses if c is not None]
        return ProviderResult(courses=courses, available=True)

    @staticmethod
    def _normalize(event: dict) -> NormalizedCourse | None:
        try:
            eid = event["id"]
            name = event.get("name", {}).get("text") or "Untitled Event"
            description = event.get("summary") or (event.get("description", {}) or {}).get("text") or ""
            start = event.get("start", {}).get("local")
            date = datetime.fromisoformat(start) if start else None

            venue = event.get("venue") or {}
            venue_address = venue.get("address") or {}
            location = venue_address.get("localized_area_display") or "Singapore"

            is_free = event.get("is_free", False)
            price_sgd = 0.0
            if not is_free:
                ticket_avail = event.get("ticket_availability") or {}
                min_price = ticket_avail.get("minimum_ticket_price") or {}
                price_sgd = float(min_price.get("major_value", 0) or 0)

            category = "Workshop"

            return NormalizedCourse(
                external_id=str(eid),
                source=CourseSource.EVENTBRITE,
                title=name,
                provider="Eventbrite",
                description=description,
                category=category,
                date=date,
                duration_hours=None,
                price_sgd=price_sgd,
                skillsfuture_credit_eligible=False,
                skillsfuture_credit_amount=0.0,
                location=location,
                url=event.get("url", ""),
                image_url=(event.get("logo") or {}).get("url", "") or "",
                skills=[],
            )
        except (KeyError, TypeError, ValueError):
            return None
