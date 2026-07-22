from sqlalchemy import String, Integer, Boolean, Numeric, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Grant(Base):
    __tablename__ = "grants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cap_remaining: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    eligibility_criteria: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class GrantRecommendation(Base):
    __tablename__ = "grant_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("flow_sessions.id"), nullable=False)
    grant_id: Mapped[int] = mapped_column(Integer, ForeignKey("grants.id"), nullable=False)
    course_name: Mapped[str] = mapped_column(String(255), nullable=True)
    selected: Mapped[bool] = mapped_column(nullable=False, default=False)

    session = relationship("FlowSession", back_populates="grant_recommendations")
    grant = relationship("Grant")
