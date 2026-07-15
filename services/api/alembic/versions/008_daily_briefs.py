"""Add daily_briefs table

Revision ID: 008_daily_briefs
Revises: 007_memory
Create Date: 2025-01-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "008_daily_briefs"
down_revision: Union[str, None] = "007_memory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_briefs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("summary", sa.Text),
        sa.Column("items", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_read", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_daily_briefs_user_date", "daily_briefs", ["user_id", "date"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_daily_briefs_user_date", table_name="daily_briefs")
    op.drop_table("daily_briefs")
