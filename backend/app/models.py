import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ──────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    PUBLIC = "public"
    ORGANISER = "organiser"


class CourseSource(str, enum.Enum):
    SKILLSFUTURE = "skillsfuture"
    EVENTBRITE = "eventbrite"


class EventSource(str, enum.Enum):
    EVENTBRITE = "Eventbrite"
    MEETUP = "Meetup"
    LINKEDIN_EVENTS = "LinkedIn Events"
    LUMA = "Luma"
    ACE_SG = "ACE.SG"
    SGTECH = "SGTech"
    SEN = "Singapore Entrepreneurs Network"
    SBF = "Singapore Business Federation"
    ENTERPRISE_SG = "Enterprise Singapore"
    SME_CENTRE = "SME Centre"
    GDG = "Google Developer Groups"
    MS_REACTOR = "Microsoft Reactor"
    AWS_USER_GROUP = "AWS User Group"
    AZURE_COMMUNITY = "Azure Community"
    DATASCIENCE_SG = "DataScience SG"
    PRODUCTTANK = "ProductTank"
    TOASTMASTERS = "Toastmasters"
    ROTARACT = "Rotaract"
    JCI_SG = "JCI Singapore"
    ROTARY = "Rotary Clubs"
    ONEPA = "OnePA"
    KLOOK = "Klook Experiences"
    NLB = "NLB Workshops"
    RUNNING_CLUBS = "Running Clubs"
    BOARD_GAME = "Board Game Groups"
    VOLUNTEER_SG = "VolunteerSG"
    FINTECH_FESTIVAL = "Singapore FinTech Festival"
    SWITCH = "SWITCH"
    ATXSG = "ATxSG"
    TECH_WEEK = "Tech Week Singapore"
    FLA = "Franchise & Licensing Asia"
    USER_CREATED = "User Created"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ALL_LEVELS = "All Levels"


class EventCategory(str, enum.Enum):
    AI = "AI"
    SOFTWARE_ENGINEERING = "Software Engineering"
    CYBERSECURITY = "Cybersecurity"
    ENTREPRENEURSHIP = "Entrepreneurship"
    MARKETING = "Marketing"
    FINANCE = "Finance"
    DESIGN = "Design"
    LEADERSHIP = "Leadership"
    PUBLIC_SPEAKING = "Public Speaking"
    NETWORKING = "Networking"
    VOLUNTEERING = "Volunteering"
    SPORTS = "Sports"
    HOBBIES = "Hobbies"
    CAREER_DEVELOPMENT = "Career Development"


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"


# ── User ───────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.PUBLIC)
    linkedin_url: Mapped[str] = mapped_column(String(1000), default="")
    interests: Mapped[str] = mapped_column(Text, default="")
    career_goals: Mapped[str] = mapped_column(Text, default="")
    preferred_timings: Mapped[str] = mapped_column(String(255), default="Evenings, Weekends")
    availability_hours_per_week: Mapped[float] = mapped_column(Float, default=5.0)
    budget_sgd: Mapped[float] = mapped_column(Float, default=200.0)
    # Organiser-specific fields
    company_name: Mapped[str] = mapped_column(String(255), default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    website: Mapped[str] = mapped_column(String(1000), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    saved_events: Mapped[list["SavedEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    organiser_events: Mapped[list["OrganiserEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    learning_journeys: Mapped[list["LearningJourney"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    growth_plans: Mapped[list["GrowthPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    completed_events: Mapped[list["CompletedEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    event_registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    event_feedback: Mapped[list["EventFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # Legacy
    saved_courses: Mapped[list["SavedCourse"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    resume_profile: Mapped["ResumeProfile | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_feedback: Mapped[list["JobFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    grant_applications: Mapped[list["GrantApplication"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# ── Event (main listing model) ─────────────────────────────────────────────────

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(100), index=True)

    title: Mapped[str] = mapped_column(String(500))
    organiser: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), index=True)
    location: Mapped[str] = mapped_column(String(255), default="Singapore")

    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_sgd: Mapped[float] = mapped_column(Float, default=0.0)

    skills: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(50), default="All Levels")
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    tags: Mapped[str] = mapped_column(Text, default="")
    seo_keywords: Mapped[str] = mapped_column(Text, default="")
    recommended_audience: Mapped[str] = mapped_column(Text, default="")
    embedding_tags: Mapped[str] = mapped_column(Text, default="")

    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attendees_count: Mapped[int] = mapped_column(Integer, default=0)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_full: Mapped[bool] = mapped_column(Boolean, default=False)

    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# ── Saved Events ───────────────────────────────────────────────────────────────

class SavedEvent(Base):
    __tablename__ = "saved_events"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_saved_event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="saved_events")
    event: Mapped["Event"] = relationship()


# ── Completed Events ───────────────────────────────────────────────────────────

class CompletedEvent(Base):
    __tablename__ = "completed_events"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_completed_event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="completed_events")
    event: Mapped["Event"] = relationship()


# ── Event Registration ─────────────────────────────────────────────────────────

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_registration"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="event_registrations")
    event: Mapped["Event"] = relationship()


# ── Event Feedback ─────────────────────────────────────────────────────────────

class EventFeedback(Base):
    __tablename__ = "event_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    rating: Mapped[int] = mapped_column(Integer, default=5)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="event_feedback")
    event: Mapped["Event"] = relationship()


# ── Organiser Event ────────────────────────────────────────────────────────────

class OrganiserEvent(Base):
    """Events created by organisers through the platform."""
    __tablename__ = "organiser_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, published, cancelled
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="organiser_events")
    event: Mapped["Event | None"] = relationship()


# ── Learning Journey ───────────────────────────────────────────────────────────

class LearningJourney(Base):
    __tablename__ = "learning_journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    goal: Mapped[str] = mapped_column(String(500))
    roadmap_json: Mapped[str] = mapped_column(Text, default="[]")
    current_week: Mapped[int] = mapped_column(Integer, default=1)
    total_weeks: Mapped[int] = mapped_column(Integer, default=4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="learning_journeys")


# ── Growth Plan ────────────────────────────────────────────────────────────────

class GrowthPlan(Base):
    __tablename__ = "growth_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_type: Mapped[str] = mapped_column(String(20))  # 7, 14, 30 days
    plan_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="growth_plans")


# ── Legacy Models (kept for backward compat) ──────────────────────────────────

class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_course_source_external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[CourseSource] = mapped_column(Enum(CourseSource), index=True)
    title: Mapped[str] = mapped_column(String(500))
    provider: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), index=True)
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_sgd: Mapped[float] = mapped_column(Float, default=0.0)
    skillsfuture_credit_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    skillsfuture_credit_amount: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str] = mapped_column(String(255), default="Singapore")
    url: Mapped[str] = mapped_column(String(1000), default="")
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    skills: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(50), default="seeded")
    title: Mapped[str] = mapped_column(String(500))
    company: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), index=True)
    salary_min_sgd: Mapped[float] = mapped_column(Float, default=0.0)
    salary_max_sgd: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str] = mapped_column(String(255), default="Singapore")
    url: Mapped[str] = mapped_column(String(1000), default="")
    skills_required: Mapped[str] = mapped_column(Text, default="")
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class SavedCourse(Base):
    __tablename__ = "saved_courses"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_saved_course"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="saved_courses")
    course: Mapped["Course"] = relationship()


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    filename: Mapped[str] = mapped_column(String(255), default="")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    extracted_skills: Mapped[str] = mapped_column(Text, default="")
    extracted_name: Mapped[str] = mapped_column(String(255), default="")
    years_experience_guess: Mapped[float | None] = mapped_column(Float, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped["User"] = relationship(back_populates="resume_profile")


class JobFeedback(Base):
    __tablename__ = "job_feedback"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_job_feedback"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    liked: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped["User"] = relationship(back_populates="job_feedback")
    job: Mapped["Job"] = relationship()


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship()


class GrantApplication(Base):
    __tablename__ = "grant_applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    credit_amount_sgd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped["User"] = relationship(back_populates="grant_applications")
    course: Mapped["Course"] = relationship()
