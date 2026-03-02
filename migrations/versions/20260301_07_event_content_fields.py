"""event content fields

Revision ID: 20260301_07
Revises: 20260301_06
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_07"
down_revision = "20260301_06"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("events", sa.Column("objectives", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("materials", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("benefits", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("requirements", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("agenda", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("events", "agenda")
    op.drop_column("events", "requirements")
    op.drop_column("events", "benefits")
    op.drop_column("events", "materials")
    op.drop_column("events", "objectives")
