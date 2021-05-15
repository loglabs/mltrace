"""Add stale array

Revision ID: b87dcaa95df1
Revises: c44c32b73207
Create Date: 2021-05-14 18:15:26.934479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b87dcaa95df1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("stale", sa.ARRAY(sa.String)))


def downgrade():
    pass
