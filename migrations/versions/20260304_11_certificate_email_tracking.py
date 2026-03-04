"""certificate email tracking

Revision ID: 20260304_11
Revises: 20260304_10
Create Date: 2026-03-04 00:00:01

"""
from alembic import op
import sqlalchemy as sa


revision = "20260304_11"
down_revision = "20260304_10"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("certificates", sa.Column("emailed_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE certificates SET emailed_at = issued_at WHERE emailed_at IS NULL")


def downgrade():
    op.drop_column("certificates", "emailed_at")
