import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Event, User, UserRole
from app.auth import hash_password
from app.routers import ai, applications, auth, courses, events, grants, jobs, organiser, resume, saved
from app.scheduler import initial_refresh, start_scheduler
from app.seed_data.events_seed import load_seeded_events
from app.services.job_service import refresh_jobs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Category-to-image mapping for realistic event photos
CATEGORY_IMAGES = {
    "AI": [
        "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&q=80",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&q=80",
        "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=600&q=80",
    ],
    "Software Engineering": [
        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&q=80",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&q=80",
        "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=600&q=80",
    ],
    "Cybersecurity": [
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&q=80",
        "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&q=80",
    ],
    "Entrepreneurship": [
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=80",
        "https://images.unsplash.com/photo-1556761175-4b46a572b786?w=600&q=80",
    ],
    "Marketing": [
        "https://images.unsplash.com/photo-1533750349088-cd871a92f312?w=600&q=80",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80",
    ],
    "Finance": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80",
        "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&q=80",
    ],
    "Design": [
        "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&q=80",
        "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600&q=80",
    ],
    "Leadership": [
        "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&q=80",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=600&q=80",
    ],
    "Public Speaking": [
        "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&q=80",
        "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=600&q=80",
    ],
    "Networking": [
        "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=600&q=80",
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&q=80",
    ],
    "Volunteering": [
        "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=600&q=80",
        "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=600&q=80",
    ],
    "Sports": [
        "https://images.unsplash.com/photo-1461896836934-bd45ba729a28?w=600&q=80",
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80",
    ],
    "Hobbies": [
        "https://images.unsplash.com/photo-1513379733131-47fc74b45abc?w=600&q=80",
        "https://images.unsplash.com/photo-1511376778003-df88c7455760?w=600&q=80",
    ],
    "Career Development": [
        "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&q=80",
        "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&q=80",
    ],
}

import hashlib

def _image_for(category: str, external_id: str) -> str:
    """Pick a deterministic image URL for an event based on category + ID."""
    images = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["AI"])
    idx = int(hashlib.md5(external_id.encode()).hexdigest(), 16) % len(images)
    return images[idx]


def seed_events(db):
    """Seed 120+ events if table is empty."""
    count = db.query(Event).count()
    if count == 0:
        for ev_data in load_seeded_events():
            from datetime import datetime, timezone
            date_str = ev_data.get("date")
            date_val = None
            if date_str:
                try:
                    date_val = datetime.fromisoformat(date_str)
                except ValueError:
                    pass

            event = Event(
                external_id=ev_data["external_id"],
                source=ev_data["source"],
                title=ev_data["title"],
                organiser=ev_data["organiser"],
                description=ev_data.get("description", ""),
                category=ev_data["category"],
                location=ev_data.get("location", "Singapore"),
                date=date_val,
                duration_hours=ev_data.get("duration_hours"),
                price_sgd=ev_data.get("price_sgd", 0.0),
                skills=ev_data.get("skills", ""),
                difficulty=ev_data.get("difficulty", "All Levels"),
                image_url=ev_data.get("image_url") or _image_for(ev_data["category"], ev_data["external_id"]),
                tags=ev_data.get("tags", ""),
                seo_keywords=ev_data.get("seo_keywords", ""),
                recommended_audience=ev_data.get("recommended_audience", ""),
                embedding_tags=ev_data.get("embedding_tags", ""),
                capacity=ev_data.get("capacity"),
                attendees_count=ev_data.get("attendees_count", 0),
            )
            db.add(event)
        db.commit()
        logger.info("Seeded %d events", len(load_seeded_events()))

DEMO_ACCOUNTS = [
    {"email": "demo-public@nexa.dev", "password": "DemoPublic123!", "name": "Demo Public", "role": UserRole.PUBLIC},
    {"email": "demo-organiser@nexa.dev", "password": "DemoOrganiser123!", "name": "Demo Organiser", "role": UserRole.ORGANISER},
]


def seed_demo_accounts(db):
    """Create demo login accounts if they don't already exist."""
    for acc in DEMO_ACCOUNTS:
        existing = db.query(User).filter(User.email == acc["email"]).first()
        if not existing:
            user = User(
                email=acc["email"],
                hashed_password=hash_password(acc["password"]),
                name=acc["name"],
                role=acc["role"],
            )
            db.add(user)
    db.commit()
    logger.info("Demo accounts ready")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_events(db)
        seed_demo_accounts(db)
        refresh_jobs(db)
    finally:
        db.close()

    await initial_refresh()
    start_scheduler()

    logger.info("Nexa API ready")
    yield


app = FastAPI(title="Nexa API", version="2.0.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# New routers
app.include_router(events.router)
app.include_router(ai.router)
app.include_router(organiser.router)

# Existing routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(saved.router)
app.include_router(jobs.router)
app.include_router(resume.router)
app.include_router(applications.router)
app.include_router(grants.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
