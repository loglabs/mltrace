"""Add output flag.

Revision ID: 799660f69710
Revises: 8d252c0dc636
Create Date: 2021-06-21 15:14:35.282173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "799660f69710"
down_revision = "8d252c0dc636"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("io_pointers", sa.Column("flag", sa.Boolean, default=False))


def downgrade():
    op.drop_column("io_pointers", "flag")
