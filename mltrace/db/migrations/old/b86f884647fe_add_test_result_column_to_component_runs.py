"""add test_result column to component_runs

Revision ID: b86f884647fe
Revises: 331edc89f24b
Create Date: 2021-11-21 11:59:43.100036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b86f884647fe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "component_runs", sa.Column("test_results", sa.JSON, default=False)
    )


def downgrade():
    op.drop_column("component_runs", "test_results")
