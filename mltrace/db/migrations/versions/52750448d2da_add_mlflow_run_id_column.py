"""add_mlflow_run_id_column

Revision ID: 52750448d2da
Revises: c41d714da766
Create Date: 2021-12-01 14:17:19.791799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52750448d2da"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "component_runs", sa.Column("mlflow_run_id", sa.String, default=None)
    )
    op.add_column(
        "component_runs", sa.Column("mlflow_run_params", sa.PickleType)
    )
    op.add_column(
        "component_runs", sa.Column("mlflow_run_metrics", sa.PickleType)
    )


def downgrade():
    op.drop_column("component_runs", "mlflow_run_id")
    op.drop_column("component_runs", "mlflow_run_params")
    op.drop_column("component_runs", "mlflow_run_metrics")
