# SkillsSG

A full-stack platform for Singapore users to discover courses/workshops and get matched to jobs or upskilling paths, following the flow: **create account → upload resume → choose Job Redeployment or Upskilling → get AI-ranked recommendations → mass apply**.

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + SQLite (SQLAlchemy)
- **Course data:** SkillsFuture (seeded dataset, adapter pattern) + Eventbrite (live API, Singapore-filtered)

## Project structure

```
skillsg-platform/
  backend/
    app/
      providers/        # adapter pattern: base.py + skillsfuture_provider.py + eventbrite_provider.py
      seed_data/         # seeded SkillsFuture courses + SG job listings
      services/          # course/job caching, resume parsing, matching (recommendation) logic
      routers/           # FastAPI route handlers
      models.py           # SQLAlchemy models (unified Course model, Job, User, etc.)
      main.py              # app entrypoint, CORS, startup refresh + scheduler
    tests/                  # pytest: normalization + matching logic
  frontend/
    src/
      pages/               # one folder per diagram branch (jobRedeployment/, upskilling/, courses/)
      components/          # Navbar, CourseCard, JobCard, ProtectedRoute
      context/AuthContext.tsx
      api/client.ts        # fetch wrapper, JWT attached automatically
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env        # Windows: copy, macOS/Linux: cp
```

Edit `backend/.env`:

- `EVENTBRITE_PRIVATE_TOKEN` — optional. Get one free at https://www.eventbrite.com/platform/api-keys (Account Settings → Developer Links → API Keys). **Leave blank and the app still works** — it falls back to SkillsFuture-only data with a visible notice instead of crashing. Note Eventbrite restricts its `/v3/events/search/` endpoint to approved partners; if your token doesn't have search access you'll see a friendly "not available" notice rather than an error.
- `JWT_SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`.

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

On startup the app creates `skillsg.db`, seeds job listings, and does an initial refresh of both course providers. It then re-refreshes every `COURSE_REFRESH_INTERVAL_HOURS` (default 6) via APScheduler — course pages always read from this SQLite cache, never hitting Eventbrite/SkillsFuture directly on page load.

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env   # or cp on macOS/Linux
npm run dev
```

Open http://localhost:5173. `frontend/.env` just needs `VITE_API_BASE_URL` pointing at the backend (defaults to `http://localhost:8000`).

### 3. Run tests

```bash
cd backend
pytest
```

Covers: SkillsFuture seed → normalized Course fields, Eventbrite raw JSON → normalized Course fields (including free events, price extraction, malformed-event handling), DB upsert (insert vs. update), and the job/course matching scoring logic.

## Data sources & the adapter pattern

`app/providers/base.py` defines `CourseProvider` — an abstract adapter with one method, `fetch() -> ProviderResult`, that must never raise. `app/services/course_service.py` calls every registered provider, upserts normalized results into the `courses` table, and remembers each provider's last availability/notice for the frontend to display.

**SkillsFuture** (`app/providers/skillsfuture_provider.py`): there's no official public API for the MySkillsFuture course directory, so this serves a realistic seeded dataset (`app/seed_data/skillsfuture_courses.py`, 25 courses across categories like Data & Analytics, Technology, Design, Finance). To plug in a real source later:
1. Implement a fetcher — an authorized SkillsFuture Singapore data feed, or a scraper of the public course directory (respecting robots.txt / ToS) — that returns the same list-of-dict shape as `load_seeded_courses()`.
2. Swap the call inside `SkillsFutureProvider.fetch()`. Nothing else changes — the DB schema, API, and frontend are already source-agnostic.

**Eventbrite** (`app/providers/eventbrite_provider.py`): calls the real Eventbrite v3 `/events/search/` endpoint filtered to `location.address=Singapore`. Handles missing token, invalid token (401), no search access (403/404), network failures, and malformed responses — all degrade to `available: false` with a human-readable notice rather than raising, so a flaky third party never takes down the course listing page.

Both sources normalize into one `Course` model: `title, provider, source, date, price_sgd, location, url, category`, plus `skills` (for matching) and SkillsFuture Credit fields.

Jobs (`app/providers/job_provider.py` + `app/seed_data/jobs_seed.py`) follow the identical pattern, standing in for MyCareersFuture, which also has no public search API.

## What's simulated vs. real

The flow diagram asked for AI resume parsing, AI job/course matching, and mass-apply for jobs and SkillsFuture grants. Some of this has no legitimate external API to call, so here's exactly what's real and what's a documented stand-in:

| Step | Implementation |
|---|---|
| Resume parsing | Real PDF text extraction (`pypdf`) + keyword matching against a skills taxonomy built from the seed data (`app/services/resume_service.py`). No LLM call — see the docstring there for how to swap in one. |
| Job/course "AI recommends" | Real rule-based scoring: skill-set overlap for jobs, keyword + skill overlap for courses (`app/services/matching_service.py`). No hosted model — this runs fully offline. |
| Mass apply (jobs) | Records application intent + resume snapshot in SQLite. There is no public MyCareersFuture submission API, so nothing is actually sent to employers. |
| Mass apply (grants) | Records SkillsFuture Credit claim intent in SQLite. Real claims are filed via the government's MySkillsFuture portal with Singpass auth, which can't be automated by a third-party app. |
| SkillsFuture courses | Seeded dataset (documented above), not scraped live. |
| Eventbrite workshops | Real live API call. |

## Design

White background, purple (`#7C3AED`) primary actions/accents, 44px minimum tap targets, single-column responsive layout below 640px. Theme lives in `frontend/src/index.css` as CSS custom properties.
