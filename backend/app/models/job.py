import enum
from sqlalchemy import String, Integer, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class JobFeedback(str, enum.Enum):
    liked = "liked"
    disliked = "disliked"


class JobSuggestion(Base):
    __tablename__ = "job_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("flow_sessions.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    matched_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    user_feedback: Mapped[JobFeedback] = mapped_column(Enum(JobFeedback), nullable=True)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    selected: Mapped[bool] = mapped_column(nullable=False, default=False)

    session = relationship("FlowSession", back_populates="job_suggestions")
