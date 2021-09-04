"""create stale

Revision ID: a2cdf9aa818c
Revises: 0a8485e5ba50
Create Date: 2021-05-18 14:05:25.540236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2cdf9aa818c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("stale", sa.PickleType))


def downgrade():
    pass
