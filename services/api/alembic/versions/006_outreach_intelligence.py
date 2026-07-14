"""Add outreach_intelligence table

Revision ID: 006_outreach_intelligence
Revises: 005_resume_matching
Create Date: 2025-01-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "006_outreach_intelligence"
down_revision: Union[str, None] = "005_resume_matching"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outreach_intelligence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("best_conversation_starters", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("topics_to_avoid", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("person_interests", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("response_approach", sa.String(100)),
        sa.Column("optimal_send_time", sa.String(100)),
        sa.Column("referral_readiness", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("outreach_intelligence")
