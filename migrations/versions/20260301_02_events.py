"""events

Revision ID: 20260301_02
Revises: 20260301_01
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_02"
down_revision = "20260301_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_admins_email", "admins", ["email"], unique=True)

    op.create_table(
        "mentors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("registration_deadline", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("quota", sa.Integer(), nullable=False),
        sa.Column("invitation_code", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id"), nullable=False),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admins.id"), nullable=True),
    )
    op.create_index("ix_events_invitation_code", "events", ["invitation_code"], unique=True)

    op.create_table(
        "registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), sa.ForeignKey("participants.id"), nullable=False),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("referral_code", sa.String(length=32), nullable=True),
        sa.Column("invited_by_registration_id", sa.Integer(), sa.ForeignKey("registrations.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.add_column("participants", sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("participants", "created_at")
    op.drop_table("registrations")
    op.drop_index("ix_events_invitation_code", table_name="events")
    op.drop_table("events")
    op.drop_table("mentors")
    op.drop_index("ix_admins_email", table_name="admins")
    op.drop_table("admins")
