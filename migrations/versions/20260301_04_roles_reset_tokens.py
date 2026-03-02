"""roles and reset tokens

Revision ID: 20260301_04
Revises: 20260301_03
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_04"
down_revision = "20260301_03"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("admins", sa.Column("role", sa.String(length=32), nullable=False, server_default="admin"))
    op.add_column("admins", sa.Column("api_token_hash", sa.String(length=64), nullable=True))
    op.create_index("ix_admins_api_token_hash", "admins", ["api_token_hash"], unique=True)

    op.create_table(
        "admin_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admins.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_admin_reset_tokens_token_hash", "admin_reset_tokens", ["token_hash"], unique=True)


def downgrade():
    op.drop_index("ix_admin_reset_tokens_token_hash", table_name="admin_reset_tokens")
    op.drop_table("admin_reset_tokens")
    op.drop_index("ix_admins_api_token_hash", table_name="admins")
    op.drop_column("admins", "api_token_hash")
    op.drop_column("admins", "role")
