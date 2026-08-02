from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from app.models import ApplicationStatus, CourseSource


# ── Auth / User ────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""
    role: str = "public"  # "public" | "organiser"


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
    # Organiser-specific
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
    # Organiser-specific
    company_name: str | None = None
    bio: str | None = None
    website: str | None = None
    phone: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── AI Features ────────────────────────────────────────────────────────────────

class GrowthPlanRequest(BaseModel):
    days: int = Field(default=7, description="7, 14, or 30")
    interests: str = ""
    goals: str = ""
    availability: str = ""
    preferred_timings: str = ""
    budget_sgd: float | None = None


class GrowthPlanDay(BaseModel):
    day: int
    date_label: str
    activities: list[dict]


class GrowthPlanOut(BaseModel):
    id: int
    plan_type: str
    days: list[GrowthPlanDay]
    created_at: datetime


class LearningJourneyRequest(BaseModel):
    goal: str = Field(min_length=1)
    weeks: int = Field(default=4, ge=1, le=12)


class LearningJourneyWeek(BaseModel):
    week: int
    title: str
    events: list[dict]
    focus: str = ""


class LearningJourneyOut(BaseModel):
    id: int
    goal: str
    current_week: int
    total_weeks: int
    roadmap: list[LearningJourneyWeek]
    created_at: datetime


class AIListingRequest(BaseModel):
    input_text: str = Field(min_length=1, description="Course description or URL")


class AIListingResult(BaseModel):
    title: str
    description: str
    category: str
    tags: list[str]
    skills: list[str]
    seo_keywords: list[str]
    difficulty: str
    recommended_audience: str
    duration_hours: float | None = None
    price_suggestion_sgd: float = 0.0


class ChatMessage(BaseModel):
    message: str = Field(min_length=1)
    language: str = "en"


class ChatResponse(BaseModel):
    reply: str
    language: str


# ── Organiser ──────────────────────────────────────────────────────────────────

class OrganiserDashboardStats(BaseModel):
    total_events: int
    total_attendees: int
    avg_rating: float
    upcoming_events: int
    revenue_sgd: float
    monthly_growth: list[dict] = Field(default_factory=list)


# ─ Resume Analysis ─────────────────────────────────────────────────────────────

class ResumeAnalysisResult(BaseModel):
    extracted_skills: list[str]
    extracted_interests: list[str]
    experience_years: float | None = None
    suggested_categories: list[str]
    summary: str


# ── Legacy (kept for backward compat) ──────────────────────────────────────────

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
    price_sgd: float  # estimated payable after subsidy
    full_price_sgd: float  # full course fee before subsidy
    skillsfuture_credit_eligible: bool
    skillsfuture_credit_amount: float  # subsidy amount
    location: str
    url: str
    image_url: str
    skills: str
    fetched_at: datetime


class CourseListResponse(BaseModel):
    items: list[CourseOut]
    total: int


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str
    source: str
    title: str
    company: str
    description: str
    category: str
    salary_min_sgd: float
    salary_max_sgd: float
    location: str
    url: str
    skills_required: str
    posted_date: datetime | None


class JobRecommendation(BaseModel):
    job: JobOut
    match_score: float
    matched_skills: list[str]


class JobFeedbackIn(BaseModel):
    job_id: int
    liked: bool


class ResumeProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    filename: str
    extracted_name: str
    extracted_skills: str
    years_experience_guess: float | None
    uploaded_at: datetime


class UpskillGoalIn(BaseModel):
    goal_text: str = Field(min_length=1)
    time_commitment: str = ""
    max_cost_sgd: float | None = None
    scope: str = ""


class CourseRecommendation(BaseModel):
    course: CourseOut
    match_score: float
    matched_skills: list[str]


class MassApplyIn(BaseModel):
    job_ids: list[int]


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    status: ApplicationStatus
    created_at: datetime


class GrantMassApplyIn(BaseModel):
    course_ids: list[int]


class GrantApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    credit_amount_sgd: float
    status: ApplicationStatus
    created_at: datetime


class SavedCourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course: CourseOut
    created_at: datetime
