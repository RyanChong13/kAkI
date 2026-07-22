from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    sector: Mapped[str] = mapped_column(String(255), nullable=True)
    income_band: Mapped[str] = mapped_column(String(50), nullable=True)
    grant_history: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    resumes = relationship("Resume", back_populates="user")
    sessions = relationship("FlowSession", back_populates="user")
    applications = relationship("Application", back_populates="user")
