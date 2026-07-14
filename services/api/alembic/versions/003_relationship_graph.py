"""Add relationship graph: org_teams, org_relationships, extend people

Revision ID: 003_relationship_graph
Revises: 002_company_intelligence
Create Date: 2025-01-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "003_relationship_graph"
down_revision: Union[str, None] = "002_company_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "org_teams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("parent_team_id", UUID(as_uuid=True)),
        sa.Column("description", sa.Text),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "org_relationships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("related_person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.Enum(
            "reports_to", "works_with", "same_team", "same_project",
            "mentors", "peer", "manager", "intern", "recruiter", "hiring_manager",
            name="relationship_type"
        ), nullable=False),
        sa.Column("team_name", sa.String(255)),
        sa.Column("confidence", sa.Float, server_default=sa.text("0.5")),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.add_column("people", sa.Column("team_id", UUID(as_uuid=True)))
    op.add_column("people", sa.Column("influence_score", sa.Float, server_default=sa.text("0.0")))
    op.add_column("people", sa.Column("response_probability", sa.Float, server_default=sa.text("0.0")))
    op.add_column("people", sa.Column("referral_probability", sa.Float, server_default=sa.text("0.0")))
    op.add_column("people", sa.Column("activity_score", sa.Float, server_default=sa.text("0.0")))
    op.add_column("people", sa.Column("expertise_areas", JSONB, server_default=sa.text("'[]'::jsonb")))

    op.create_index("ix_org_relationships_person", "org_relationships", ["person_id"])
    op.create_index("ix_org_relationships_company", "org_relationships", ["company_id"])
    op.create_index("ix_org_teams_company", "org_teams", ["company_id"])
    op.create_index("ix_people_team", "people", ["team_id"])


def downgrade() -> None:
    op.drop_index("ix_people_team", table_name="people")
    op.drop_index("ix_org_teams_company", table_name="org_teams")
    op.drop_index("ix_org_relationships_company", table_name="org_relationships")
    op.drop_index("ix_org_relationships_person", table_name="org_relationships")

    op.drop_column("people", "expertise_areas")
    op.drop_column("people", "activity_score")
    op.drop_column("people", "referral_probability")
    op.drop_column("people", "response_probability")
    op.drop_column("people", "influence_score")
    op.drop_column("people", "team_id")

    op.drop_table("org_relationships")
    op.drop_table("org_teams")
    op.execute("DROP TYPE IF EXISTS relationship_type")
