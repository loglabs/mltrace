"""Add git tags column

Revision ID: 017c5f7dc0aa
Revises: 799660f69710
Create Date: 2021-06-30 14:28:42.827950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017c5f7dc0aa'
down_revision = '799660f69710'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("git_tags", sa.PickleType))


def downgrade():
    op.drop_column("component_runs", "git_tags")
