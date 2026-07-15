"""Add knowledge_graph_entities and knowledge_graph_edges tables

Revision ID: 010_knowledge_graph
Revises: 009_career_goals
Create Date: 2025-01-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "010_knowledge_graph"
down_revision: Union[str, None] = "009_career_goals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_graph_entities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.execute("ALTER TABLE knowledge_graph_entities ADD COLUMN embedding vector(1536)")

    op.create_table(
        "knowledge_graph_edges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("weight", sa.Float, server_default=sa.text("1.0")),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_kg_entities_type", "knowledge_graph_entities", ["type"])
    op.create_index("ix_kg_edges_source", "knowledge_graph_edges", ["source_id"])
    op.create_index("ix_kg_edges_target", "knowledge_graph_edges", ["target_id"])
    op.create_index("ix_kg_edges_type", "knowledge_graph_edges", ["relationship_type"])


def downgrade() -> None:
    op.drop_index("ix_kg_edges_type", table_name="knowledge_graph_edges")
    op.drop_index("ix_kg_edges_target", table_name="knowledge_graph_edges")
    op.drop_index("ix_kg_edges_source", table_name="knowledge_graph_edges")
    op.drop_index("ix_kg_entities_type", table_name="knowledge_graph_entities")
    op.drop_table("knowledge_graph_edges")
    op.drop_table("knowledge_graph_entities")
