"""github oauth fields

Revision ID: 20260301_08
Revises: 20260301_07
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_08"
down_revision = "20260301_07"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("participants", sa.Column("github_id", sa.String(length=64), nullable=True))
    op.add_column("participants", sa.Column("github_username", sa.String(length=120), nullable=True))
    op.add_column("participants", sa.Column("avatar_url", sa.String(length=255), nullable=True))
    op.create_index("ix_participants_github_id", "participants", ["github_id"], unique=True)


def downgrade():
    op.drop_index("ix_participants_github_id", table_name="participants")
    op.drop_column("participants", "avatar_url")
    op.drop_column("participants", "github_username")
    op.drop_column("participants", "github_id")
