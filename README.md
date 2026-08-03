# Nexa — AI Career Redesign

A full-stack tool that helps Singapore workers understand how AI will reshape their role and find funded upskilling paths. The flow: **enter your role → get AI-generated redesign suggestions → browse matched SkillsFuture courses → see which government funding schemes you're eligible for**.

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + SQLite (SQLAlchemy)
- **AI:** OpenAI or Anthropic (configurable, auto-detected)
- **Course data:** Live crawl of MySkillsFuture (courses.myskillsfuture.gov.sg) + built-in seed fallback

## Project structure

```
kAkI/
  backend/
    app/
      agents/              # LLM client wrapper (OpenAI + Anthropic)
      providers/           # adapter pattern: base.py + skillsfuture_provider.py
      seed_data/           # role taxonomy (63 SG roles) + seed courses
      services/            # SkillsFuture scraper, course service, scheme rules, redesign engine
      routers/             # FastAPI route handlers (redesign, auth, courses)
      models.py            # SQLAlchemy models (User, Course with scheme fields)
      schemas.py           # Pydantic request/response schemas
      main.py              # app entrypoint, CORS, startup crawl + scheduler
    tests/                 # pytest: normalization + matching logic
  frontend/
    src/
      pages/               # Redesign (main tool), Courses, Login, Register
      components/          # Navbar
      context/AuthContext.tsx
      api/client.ts        # fetch wrapper, JWT attached automatically
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` — **required** for the redesign feature. Get one at [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/settings/keys). OpenAI takes priority if both are set.
- `JWT_SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`.

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

On startup the app creates `skillsg.db`, crawls ~400 live courses from MySkillsFuture, and tags each with SkillsFuture scheme eligibility. It re-crawls every 6 hours via APScheduler.

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. `frontend/.env` just needs `VITE_API_BASE_URL` pointing at the backend (defaults to `http://localhost:8000`).

### 3. Run tests

```bash
cd backend
pytest
```

## Features

### Role Redesign (main tool)

1. **Role input** — autocomplete from a taxonomy of 63 Singapore-relevant roles across 10 categories, each with core tasks defined.
2. **AI suggestions** — the LLM generates 2-3 redesign directions per role, each with a title, AI impact level (Augment / Transform), timeframe, description, "why this makes sense" explanation, and upskilling areas.
3. **Course matching** — each suggestion is matched against the crawled SkillsFuture course database using keyword/skill overlap scoring.
4. **Scheme eligibility** — matched courses are tagged with the government funding schemes the user qualifies for:
   - **SkillsFuture Credit** — $500, age 25+
   - **Mid-Career Credit** — $4,000, age 40+
   - **SCTP** — up to 90% subsidy for career transition courses
   - **Level-Up Programme** — monthly allowance, age 40+
5. **MySkillsFuture CTA** — each course links directly to its page on courses.myskillsfuture.gov.sg.

### Courses browser

Searchable, filterable listing of all crawled SkillsFuture courses with fee breakdowns, skill tags, and scheme eligibility badges.

## Data sources & the adapter pattern

`app/providers/base.py` defines `CourseProvider` — an abstract adapter with one method, `fetch() -> ProviderResult`, that must never raise. `app/services/course_service.py` calls every registered provider, upserts normalized results into the `courses` table, and remembers each provider's last availability/notice for the frontend.

**SkillsFuture** (`app/providers/skillsfuture_provider.py`): live crawl of the public MySkillsFuture course directory by parsing Next.js RSC payloads. Falls back to a seeded dataset (`app/seed_data/skillsfuture_courses.py`) if the crawl fails. Scheme eligibility is heuristically tagged during ingestion via `app/services/scheme_rules.py`.

## What's real vs. estimated

| Step | Implementation |
|---|---|
| Role taxonomy | Curated static dataset of 63 SG roles with core tasks |
| AI redesign suggestions | Real LLM call (OpenAI GPT-4o or Anthropic Claude) |
| Course matching | Rule-based keyword/skill overlap scoring |
| Scheme eligibility | Heuristic rules based on course fee and duration (prototype — always verify on MySkillsFuture) |
| SkillsFuture courses | Live crawl of courses.myskillsfuture.gov.sg (~400 courses) |
| Auth | JWT-based (kept for future save/share features) |

## Design

White background, purple (`#7C3AED`) primary actions/accents, 44px minimum tap targets, single-column responsive layout below 640px. Theme lives in `frontend/src/index.css` as CSS custom properties.
