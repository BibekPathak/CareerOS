"""Add company intelligence fields to company_profiles

Revision ID: 002_company_intelligence
Revises: 001_initial
Create Date: 2025-01-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "002_company_intelligence"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("company_profiles", sa.Column("hiring_velocity", JSONB))
    op.add_column("company_profiles", sa.Column("backend_team_size", sa.Integer))
    op.add_column("company_profiles", sa.Column("languages_used", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("hiring_manager_name", sa.String(255)))
    op.add_column("company_profiles", sa.Column("recruiters", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("interns", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("ex_interns", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("recent_promotions", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("conference_talks", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("interview_difficulty", sa.String(100)))
    op.add_column("company_profiles", sa.Column("likely_interview_topics", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("interesting_github_repos", JSONB, server_default=sa.text("'[]'::jsonb")))
    op.add_column("company_profiles", sa.Column("org_chart_summary", sa.Text))


def downgrade() -> None:
    op.drop_column("company_profiles", "org_chart_summary")
    op.drop_column("company_profiles", "interesting_github_repos")
    op.drop_column("company_profiles", "likely_interview_topics")
    op.drop_column("company_profiles", "interview_difficulty")
    op.drop_column("company_profiles", "conference_talks")
    op.drop_column("company_profiles", "recent_promotions")
    op.drop_column("company_profiles", "ex_interns")
    op.drop_column("company_profiles", "interns")
    op.drop_column("company_profiles", "recruiters")
    op.drop_column("company_profiles", "hiring_manager_name")
    op.drop_column("company_profiles", "languages_used")
    op.drop_column("company_profiles", "backend_team_size")
    op.drop_column("company_profiles", "hiring_velocity")
