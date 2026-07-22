from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import Base, engine
from app.models import *  # noqa — register all models
from app.routers import auth, resume, flow, jobs, grants, upskilling, apply

# Path to frontend build output
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)

    # Seed grants if table is empty
    from app.database import SessionLocal
    from app.models.grant import Grant
    import json, os
    db = SessionLocal()
    try:
        if db.query(Grant).count() == 0:
            seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed", "grants.json")
            if os.path.exists(seed_path):
                with open(seed_path) as f:
                    for g in json.load(f):
                        db.add(Grant(
                            name=g["name"], amount=g["amount"],
                            cap_remaining=g["cap_remaining"],
                            eligibility_criteria=g["eligibility_criteria"],
                        ))
                db.commit()
    finally:
        db.close()

    yield


app = FastAPI(title="Redeployment / Upskilling Platform", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(flow.router)
app.include_router(jobs.router)
app.include_router(grants.router)
app.include_router(upskilling.router)
app.include_router(apply.router)


@app.get("/api")
def root():
    return {"message": "Redeployment / Upskilling Platform API", "version": "1.0.0"}


# Serve frontend static files if build exists
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve static files or fall back to index.html for SPA routing."""
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
