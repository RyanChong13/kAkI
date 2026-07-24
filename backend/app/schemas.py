from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ApplicationStatus, CourseSource


# ---------- Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Course ----------

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
    skillsfuture_credit_eligible: bool
    skillsfuture_credit_amount: float
    location: str
    url: str
    image_url: str
    skills: str
    fetched_at: datetime


class CourseListResponse(BaseModel):
    items: list[CourseOut]
    total: int
    eventbrite_available: bool
    eventbrite_notice: str | None = None


# ---------- Jobs ----------

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


# ---------- Resume ----------

class ResumeProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    filename: str
    extracted_name: str
    extracted_skills: str
    years_experience_guess: float | None
    uploaded_at: datetime


# ---------- Upskilling goal prompt ----------

class UpskillGoalIn(BaseModel):
    goal_text: str = Field(min_length=1, description="What the user wants to achieve")
    time_commitment: str = Field(description="e.g. '<5 hrs/week', 'full-time'")
    max_cost_sgd: float | None = None
    scope: str = Field(default="", description="Free-text scope of what they want to learn")


class CourseRecommendation(BaseModel):
    course: CourseOut
    match_score: float
    matched_skills: list[str]


# ---------- Applications / Grants ----------

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


# ---------- Saved courses ----------

class SavedCourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course: CourseOut
    created_at: datetime
