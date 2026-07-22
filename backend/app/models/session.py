import enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FlowPath(str, enum.Enum):
    redeployment = "redeployment"
    upskilling = "upskilling"


class FlowStatus(str, enum.Enum):
    active = "active"
    applied_round_1 = "applied_round_1"
    applied_round_2 = "applied_round_2"
    exited = "exited"


class FlowSession(Base):
    __tablename__ = "flow_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    path: Mapped[FlowPath] = mapped_column(Enum(FlowPath), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[FlowStatus] = mapped_column(Enum(FlowStatus), nullable=False, default=FlowStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
    job_suggestions = relationship("JobSuggestion", back_populates="session")
    grant_recommendations = relationship("GrantRecommendation", back_populates="session")
    applications = relationship("Application", back_populates="session")
