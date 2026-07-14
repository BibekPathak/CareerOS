"""Add resume_matches table for per-job skill matching

Revision ID: 005_resume_matching
Revises: 004_job_intelligence
Create Date: 2025-01-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "005_resume_matching"
down_revision: Union[str, None] = "004_job_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float),
        sa.Column("skill_matches", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("strengths", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("weaknesses", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("mention_projects", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("avoid_mentioning", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("recommendation", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_resume_matches_user_job", "resume_matches", ["user_id", "job_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_resume_matches_user_job", table_name="resume_matches")
    op.drop_table("resume_matches")
