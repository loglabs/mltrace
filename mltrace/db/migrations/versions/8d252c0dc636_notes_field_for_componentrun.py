"""Notes field for ComponentRun

Revision ID: 8d252c0dc636
Revises: a2cdf9aa818c
Create Date: 2021-05-26 09:52:19.057302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d252c0dc636"
down_revision = "a2cdf9aa818c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("notes", sa.String))


def downgrade():
    op.drop_column("component_runs", "notes")
