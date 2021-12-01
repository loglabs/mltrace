"""add_mlflow_run_id_column

Revision ID: 52750448d2da
Revises: 331edc89f24b
Create Date: 2021-12-01 14:17:19.791799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52750448d2da'
down_revision = '331edc89f24b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("component_runs", sa.Column("mlflow_run_id", sa.String, default=None))


def downgrade():
    op.drop_column("component_runs", "mlflow_run_id")
