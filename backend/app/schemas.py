from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import CourseSource


# ── Auth / User ────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""
    role: str = "public"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    role: str
    linkedin_url: str = ""
    interests: str = ""
    career_goals: str = ""
    preferred_timings: str = ""
    availability_hours_per_week: float = 5.0
    budget_sgd: float = 200.0
    company_name: str = ""
    bio: str = ""
    website: str = ""
    phone: str = ""


class UserUpdate(BaseModel):
    name: str | None = None
    linkedin_url: str | None = None
    interests: str | None = None
    career_goals: str | None = None
    preferred_timings: str | None = None
    availability_hours_per_week: float | None = None
    budget_sgd: float | None = None
    company_name: str | None = None
    bio: str | None = None
    website: str | None = None
    phone: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Course ─────────────────────────────────────────────────────────────────────

class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str
    source: CourseSource
    title: str
    provider: str
    description: str
    category: str
    date: datetime | None
    duration_hours: float | None
    price_sgd: float
    full_price_sgd: float
    skillsfuture_credit_eligible: bool
    skillsfuture_credit_amount: float
    base_credit_eligible: bool
    mid_career_eligible: bool
    sctp_eligible: bool
    level_up_eligible: bool
    location: str
    url: str
    image_url: str
    skills: str
    fetched_at: datetime


class CourseListResponse(BaseModel):
    items: list[CourseOut]
    total: int


# ── Role Taxonomy ──────────────────────────────────────────────────────────────

class RoleOut(BaseModel):
    id: str
    title: str
    category: str
    core_tasks: list[str]


class RoleListResponse(BaseModel):
    categories: list[str]
    roles: list[RoleOut]


# ── Redesign ───────────────────────────────────────────────────────────────────

class RedesignRequest(BaseModel):
    role: str = Field(min_length=1, description="Role title, ID, or free text")
    age: int | None = Field(default=None, ge=0, le=120, description="User age for scheme eligibility")


class SchemeInfo(BaseModel):
    scheme_id: str
    scheme_name: str
    eligible: bool
    credit_amount_sgd: float | None = None
    description: str
    eligibility_notes: str
    age_note: str = ""
    official_url: str


class MatchedCourseOut(BaseModel):
    course: CourseOut
    match_score: float
    matched_skills: list[str]
    schemes: list[SchemeInfo]


class RedesignSuggestion(BaseModel):
    title: str
    description: str
    why: str
    ai_impact: str  # augment | automate | transform
    upskilling_areas: list[str]
    estimated_timeframe: str
    matched_courses: list[MatchedCourseOut]


class RedesignResult(BaseModel):
    role: str
    role_category: str
    role_core_tasks: list[str]
    suggestions: list[RedesignSuggestion]
