from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, resume, flow, jobs, grants, upskilling, apply

app = FastAPI(title="Redeployment / Upskilling Platform", version="1.0.0")

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


@app.get("/")
def root():
    return {"message": "Redeployment / Upskilling Platform API", "version": "1.0.0"}
