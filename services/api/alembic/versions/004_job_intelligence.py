"""Add job intelligence fields to jobs table

Revision ID: 004_job_intelligence
Revises: 003_relationship_graph
Create Date: 2025-01-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "004_job_intelligence"
down_revision: Union[str, None] = "003_relationship_graph"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("required_skills", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("nice_to_have_skills", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("missing_skills", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("resume_match_score", sa.Float))
    op.add_column("jobs", sa.Column("strengths", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("weaknesses", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("people_to_contact", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("projects_to_mention", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("likely_interview_topics", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("jobs", sa.Column("interview_difficulty", sa.String(50)))


def downgrade() -> None:
    op.drop_column("jobs", "interview_difficulty")
    op.drop_column("jobs", "likely_interview_topics")
    op.drop_column("jobs", "projects_to_mention")
    op.drop_column("jobs", "people_to_contact")
    op.drop_column("jobs", "weaknesses")
    op.drop_column("jobs", "strengths")
    op.drop_column("jobs", "resume_match_score")
    op.drop_column("jobs", "missing_skills")
    op.drop_column("jobs", "nice_to_have_skills")
    op.drop_column("jobs", "required_skills")
