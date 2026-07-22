"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sector", sa.String(255), nullable=True),
        sa.Column("income_band", sa.String(50), nullable=True),
        sa.Column("grant_history", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- resumes ---
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parsed_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- flow_sessions ---
    flow_path_enum = sa.Enum("redeployment", "upskilling", name="flowpath")
    flow_status_enum = sa.Enum("active", "applied_round_1", "applied_round_2", "exited", name="flowstatus")
    flow_path_enum.create(op.get_bind(), checkfirst=True)
    flow_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "flow_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("path", flow_path_enum, nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", flow_status_enum, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- job_suggestions ---
    job_feedback_enum = sa.Enum("liked", "disliked", name="jobfeedback")
    job_feedback_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "job_suggestions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("flow_sessions.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("missing_skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("user_feedback", job_feedback_enum, nullable=True),
        sa.Column("round_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )

    # --- grants ---
    op.create_table(
        "grants",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("cap_remaining", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("eligibility_criteria", sa.JSON(), nullable=False, server_default="{}"),
    )

    # --- grant_recommendations ---
    op.create_table(
        "grant_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("flow_sessions.id"), nullable=False),
        sa.Column("grant_id", sa.Integer(), sa.ForeignKey("grants.id"), nullable=False),
        sa.Column("course_name", sa.String(255), nullable=True),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )

    # --- applications ---
    application_type_enum = sa.Enum("job", "grant", name="applicationtype")
    application_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("flow_sessions.id"), nullable=False),
        sa.Column("type", application_type_enum, nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("target_name", sa.String(255), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("grant_recommendations")
    op.drop_table("grants")
    op.drop_table("job_suggestions")
    op.drop_table("flow_sessions")
    op.drop_table("resumes")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS applicationtype")
    op.execute("DROP TYPE IF EXISTS jobfeedback")
    op.execute("DROP TYPE IF EXISTS flowstatus")
    op.execute("DROP TYPE IF EXISTS flowpath")
