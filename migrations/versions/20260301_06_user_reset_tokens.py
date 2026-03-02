"""participant reset tokens

Revision ID: 20260301_06
Revises: 20260301_05
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_06"
down_revision = "20260301_05"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "participant_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), sa.ForeignKey("participants.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_participant_reset_tokens_token_hash", "participant_reset_tokens", ["token_hash"], unique=True)


def downgrade():
    op.drop_index("ix_participant_reset_tokens_token_hash", table_name="participant_reset_tokens")
    op.drop_table("participant_reset_tokens")
