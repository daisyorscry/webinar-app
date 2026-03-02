"""profile photo and email verification

Revision ID: 20260301_09
Revises: 20260301_08
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_09"
down_revision = "20260301_08"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("participants", sa.Column("profile_photo_path", sa.String(length=255), nullable=True))
    op.add_column("participants", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("participants", sa.Column("email_verification_token", sa.String(length=64), nullable=True))
    op.create_index("ix_participants_email_verification_token", "participants", ["email_verification_token"], unique=True)


def downgrade():
    op.drop_index("ix_participants_email_verification_token", table_name="participants")
    op.drop_column("participants", "email_verification_token")
    op.drop_column("participants", "email_verified")
    op.drop_column("participants", "profile_photo_path")
