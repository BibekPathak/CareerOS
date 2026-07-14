"""Add conversation_memory and follow_up_suggestions tables

Revision ID: 007_memory
Revises: 006_outreach_intelligence
Create Date: 2025-01-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "007_memory"
down_revision: Union[str, None] = "006_outreach_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversation_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.Enum(
            "message_sent", "message_read", "response_received",
            "follow_up_sent", "connection_accepted", "meeting_scheduled",
            "person_posted", "connected",
            name="conversation_event_type",
        ), nullable=False),
        sa.Column("event_data", JSONB),
        sa.Column("context_snapshot", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "follow_up_suggestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_event_id", UUID(as_uuid=True)),
        sa.Column("suggestion_type", sa.String(50), nullable=False),
        sa.Column("reasoning", sa.Text),
        sa.Column("suggested_message", sa.Text),
        sa.Column("urgency", sa.String(20), server_default="medium"),
        sa.Column("is_read", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_conversation_memory_person", "conversation_memory", ["person_id"])
    op.create_index("ix_follow_up_suggestions_user", "follow_up_suggestions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_follow_up_suggestions_user", table_name="follow_up_suggestions")
    op.drop_index("ix_conversation_memory_person", table_name="conversation_memory")
    op.drop_table("follow_up_suggestions")
    op.drop_table("conversation_memory")
    op.execute("DROP TYPE IF EXISTS conversation_event_type")
