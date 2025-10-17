"""create messages table

Revision ID: 6e4be2a7d509
Revises:
Create Date: 2025-10-16 15:14:16.841141

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6e4be2a7d509"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("length", sa.Integer, nullable=False),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )
    op.create_index("ix_messages_user_deleted", "messages", ["user_id", "deleted_at"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_messages_user_deleted", table_name="messages")
    op.drop_table("messages")

