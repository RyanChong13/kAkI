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


class CourseSource(str, enum.Enum):
    SKILLSFUTURE = "skillsfuture"
    EVENTBRITE = "eventbrite"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    saved_courses: Mapped[list["SavedCourse"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    resume_profile: Mapped["ResumeProfile | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_feedback: Mapped[list["JobFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    grant_applications: Mapped[list["GrantApplication"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    """Unified course/workshop model, normalized from multiple provider sources."""

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

    skills: Mapped[str] = mapped_column(Text, default="")  # comma-separated tags used for matching

    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Job(Base):
    """Seeded Singapore job listings (adapter pattern, see providers/job_provider.py)."""

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

    skills_required: Mapped[str] = mapped_column(Text, default="")  # comma-separated
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
    """Parsed output of the user's uploaded resume PDF."""

    __tablename__ = "resume_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    filename: Mapped[str] = mapped_column(String(255), default="")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    extracted_skills: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    extracted_name: Mapped[str] = mapped_column(String(255), default="")
    years_experience_guess: Mapped[float | None] = mapped_column(Float, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="resume_profile")


class JobFeedback(Base):
    """Tracks the diagram's 'users like/do not like the jobs' step."""

    __tablename__ = "job_feedback"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_job_feedback"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    liked: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="job_feedback")
    job: Mapped["Job"] = relationship()


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"


class Application(Base):
    """Records a (simulated) mass-apply action for a job.

    NOTE: there is no public Singapore job-board submission API (MyCareersFuture
    does not expose one), so this records the user's application intent and
    resume snapshot rather than actually transmitting anything to a third
    party. See README for what a real integration would require.
    """

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship()


class GrantApplication(Base):
    """Records a (simulated) SkillsFuture Credit claim / grant application for a course.

    NOTE: SkillsFuture Credit claims are actually filed via the government's
    MySkillsFuture portal with Singpass auth, which cannot be automated by a
    third-party app. This records intent so the UI flow matches the diagram;
    see README for the real claim process.
    """

    __tablename__ = "grant_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    credit_amount_sgd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="grant_applications")
    course: Mapped["Course"] = relationship()
