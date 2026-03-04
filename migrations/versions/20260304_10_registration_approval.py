"""registration approval flow

Revision ID: 20260304_10
Revises: 20260301_09
Create Date: 2026-03-04 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260304_10"
down_revision = "20260301_09"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "registrations",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
    )
    op.add_column("registrations", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("registrations", sa.Column("approved_by_admin_id", sa.Integer(), nullable=True))
    op.execute("UPDATE registrations SET status = 'approved', approved_at = created_at")
    op.create_foreign_key(
        "fk_registrations_approved_by_admin_id_admins",
        "registrations",
        "admins",
        ["approved_by_admin_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_registrations_approved_by_admin_id_admins", "registrations", type_="foreignkey")
    op.drop_column("registrations", "approved_by_admin_id")
    op.drop_column("registrations", "approved_at")
    op.drop_column("registrations", "status")
