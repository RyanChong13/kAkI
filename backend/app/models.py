import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ──────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    PUBLIC = "public"
    ORGANISER = "organiser"


class CourseSource(str, enum.Enum):
    SKILLSFUTURE = "skillsfuture"


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


# ── Course ─────────────────────────────────────────────────────────────────────

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
    price_sgd: Mapped[float] = mapped_column(Float, default=0.0)  # estimated payable (after subsidy)
    full_price_sgd: Mapped[float] = mapped_column(Float, default=0.0)  # full course fee before subsidy
    skillsfuture_credit_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    skillsfuture_credit_amount: Mapped[float] = mapped_column(Float, default=0.0)  # subsidy amount
    # SkillsFuture scheme eligibility (heuristic — see services/scheme_rules.py)
    base_credit_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    mid_career_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    sctp_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    level_up_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[str] = mapped_column(String(255), default="Singapore")
    url: Mapped[str] = mapped_column(String(1000), default="")
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    skills: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
