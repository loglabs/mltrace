"""Create monitoring tables

Revision ID: c41d714da766
Revises: None
Create Date: 2021-12-23 14:18:50.621612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c41d714da766"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create 2 new tables

    op.create_table(
        "outputs",
        sa.Column("timestamp", sa.DateTime),
        sa.Column("identifier", sa.String),
        sa.Column("task_name", sa.String),
        sa.Column("value", sa.Numeric),
        sa.Index("outputs_ts_name_asc", "timestamp", "task_name"),
        sa.Index(
            "outputs_ts_name_desc",
            sa.text("timestamp DESC"),
            "task_name",
        ),
    )

    op.create_table(
        "feedback",
        sa.Column("timestamp", sa.DateTime),
        sa.Column("identifier", sa.String),
        sa.Column("task_name", sa.String),
        sa.Column("value", sa.Numeric),
        sa.Index("feedback_ts_name_asc", "timestamp", "task_name"),
        sa.Index(
            "feedback_ts_name_desc",
            sa.text("timestamp DESC"),
            "task_name",
        ),
    )


def downgrade():
    op.drop_table("feedback")
    op.drop_table("outputs")
