"""participants password and meet link and admin seed

Revision ID: 20260301_05
Revises: 20260301_04
Create Date: 2026-03-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260301_05"
down_revision = "20260301_04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "participants",
        sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column("events", sa.Column("meet_link", sa.String(length=255), nullable=True))
    op.add_column("events", sa.Column("meet_generated_at", sa.DateTime(), nullable=True))

    op.execute(
        """
        INSERT INTO admins (name, email, password_hash, role)
        SELECT 'Admin', 'admin@example.com',
        'scrypt:32768:8:1$mvQbENwSr5yzNeze$3098cddb4fc8f98ff1c85ccb2b76862246874bcccfd79d619403c67494f81be0c123bd3b86f2e14c1c52ea663f7ff231ea51049e67dd938a2f0c8abf5e75404e',
        'superadmin'
        WHERE NOT EXISTS (SELECT 1 FROM admins);
        """
    )


def downgrade():
    op.drop_column("events", "meet_generated_at")
    op.drop_column("events", "meet_link")
    op.drop_column("participants", "password_hash")
