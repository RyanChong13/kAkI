import enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, Enum, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ApplicationType(str, enum.Enum):
    job = "job"
    grant = "grant"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("flow_sessions.id"), nullable=False)
    type: Mapped[ApplicationType] = mapped_column(Enum(ApplicationType), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    target_name: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="applications")
    session = relationship("FlowSession", back_populates="applications")
