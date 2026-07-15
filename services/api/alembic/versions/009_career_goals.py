"""Add career_goals and goal_events tables

Revision ID: 009_career_goals
Revises: 008_daily_briefs
Create Date: 2025-01-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "009_career_goals"
down_revision: Union[str, None] = "008_daily_briefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_goals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("target_company", sa.String(255)),
        sa.Column("target_role", sa.String(255)),
        sa.Column("deadline", sa.Date),
        sa.Column("priority", sa.String(20), server_default="medium"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("plan", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("current_step_index", sa.Integer, server_default=sa.text("0")),
        sa.Column("progress_metrics", JSONB),
        sa.Column("context_snapshot", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "goal_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("goal_id", UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_career_goals_user", "career_goals", ["user_id", "status"])
    op.create_index("ix_goal_events_goal", "goal_events", ["goal_id"])


def downgrade() -> None:
    op.drop_index("ix_goal_events_goal", table_name="goal_events")
    op.drop_index("ix_career_goals_user", table_name="career_goals")
    op.drop_table("goal_events")
    op.drop_table("career_goals")
