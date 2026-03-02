"""admin auth and certificate links

Revision ID: 20260301_03
Revises: 20260301_02
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_03"
down_revision = "20260301_02"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("admins", sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""))
    op.add_column("certificates", sa.Column("event_id", sa.Integer(), nullable=True))
    op.add_column("certificates", sa.Column("registration_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_certificates_event", "certificates", "events", ["event_id"], ["id"])
    op.create_foreign_key(
        "fk_certificates_registration", "certificates", "registrations", ["registration_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("fk_certificates_registration", "certificates", type_="foreignkey")
    op.drop_constraint("fk_certificates_event", "certificates", type_="foreignkey")
    op.drop_column("certificates", "registration_id")
    op.drop_column("certificates", "event_id")
    op.drop_column("admins", "password_hash")
