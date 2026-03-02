"""init

Revision ID: 20260301_01
Revises: 
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("attendance_status", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("attended_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_participants_participant_id", "participants", ["participant_id"], unique=True)
    op.create_index("ix_participants_email", "participants", ["email"], unique=True)

    op.create_table(
        "graduation_status",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), sa.ForeignKey("participants.id"), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), sa.ForeignKey("participants.id"), nullable=False),
        sa.Column("certificate_number", sa.String(length=64), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_certificates_certificate_number", "certificates", ["certificate_number"], unique=True)


def downgrade():
    op.drop_index("ix_certificates_certificate_number", table_name="certificates")
    op.drop_table("certificates")
    op.drop_table("graduation_status")
    op.drop_index("ix_participants_email", table_name="participants")
    op.drop_index("ix_participants_participant_id", table_name="participants")
    op.drop_table("participants")
