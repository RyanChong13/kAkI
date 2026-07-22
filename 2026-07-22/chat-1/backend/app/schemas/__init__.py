from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- Auth Schemas ---

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    age: Optional[int] = None
    sector: Optional[str] = None
    income_band: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    age: Optional[int] = None
    sector: Optional[str] = None
    income_band: Optional[str] = None
    grant_history: List = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Resume Schemas ---

class SkillItem(BaseModel):
    skill: str
    years: float
    source: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    parsed_skills: List[SkillItem]
    uploaded_at: datetime

    class Config:
        from_attributes = True


# --- Flow Schemas ---

class FlowStartRequest(BaseModel):
    path: str  # "redeployment" or "upskilling"


class FlowSessionResponse(BaseModel):
    id: int
    user_id: int
    path: str
    round_number: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    feedback: str  # "liked" or "disliked"
    selected_job_ids: Optional[List[int]] = None


# --- Job Schemas ---

class JobSuggestionResponse(BaseModel):
    id: int
    session_id: int
    title: str
    matched_skills: List[str]
    missing_skills: List[str]
    user_feedback: Optional[str] = None
    round_number: int
    selected: bool

    class Config:
        from_attributes = True


# --- Grant Schemas ---

class GrantResponse(BaseModel):
    id: int
    name: str
    amount: float
    cap_remaining: int

    class Config:
        from_attributes = True


class GrantRecommendationResponse(BaseModel):
    id: int
    session_id: int
    grant_id: int
    course_name: Optional[str] = None
    selected: bool
    grant: Optional[GrantResponse] = None

    class Config:
        from_attributes = True


# --- Upskilling Schemas ---

class UpskillingPlanRequest(BaseModel):
    goal: str
    time: str
    cost: str
    scope: str


class CourseSuggestion(BaseModel):
    name: str
    provider: str
    duration: str
    cost: str
    skill_gap_addressed: str


# --- Apply Schemas ---

class ApplyPreviewRequest(BaseModel):
    type: str  # "job" or "grant"
    target_ids: List[int]


class ApplyPreviewItem(BaseModel):
    target_id: int
    target_name: str
    type: str
    details: dict


class ApplyConfirmRequest(BaseModel):
    preview_id: str  # a reference to the preview
    confirmed: bool


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    type: str
    target_id: int
    target_name: str
    confirmed: bool
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
