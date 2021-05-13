"""add staleness indicator

Revision ID: ee85d7af6f26
Revises: 
Create Date: 2021-05-13 12:51:45.676626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ee85d7af6f26"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("stale", sa.Boolean))


def downgrade():
    pass
