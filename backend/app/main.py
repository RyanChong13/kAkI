import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.auth import hash_password
from app.routers import auth, courses, redesign
from app.scheduler import initial_refresh, start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEMO_ACCOUNTS = [
    {"email": "demo@nexa.dev", "password": "Demo12345", "name": "Demo User", "role": UserRole.PUBLIC},
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
        seed_demo_accounts(db)
    finally:
        db.close()

    await initial_refresh()
    start_scheduler()

    logger.info("Nexa API ready")
    yield


app = FastAPI(title="Nexa API", version="3.0.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(redesign.router)
app.include_router(auth.router)
app.include_router(courses.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
