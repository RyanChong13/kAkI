import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import applications, auth, courses, grants, jobs, resume, saved
from app.scheduler import initial_refresh, start_scheduler
from app.services.job_service import refresh_jobs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        refresh_jobs(db)
    finally:
        db.close()

    await initial_refresh()
    start_scheduler()

    logger.info("SkillsSG API ready")
    yield


app = FastAPI(title="SkillsSG API", version="1.0.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
