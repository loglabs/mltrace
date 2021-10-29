"""Create label tables

Revision ID: 8824d15c21d6
Revises: 331edc89f24b
Create Date: 2021-10-29 14:37:32.851506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8824d15c21d6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("labels", sa.Column("id", sa.String, primary_key=True))

    op.create_table(
        "labels_io_pointers",
        sa.Column("label", sa.String, sa.ForeignKey("labels.id"), index=True),
        sa.Column("io_pointer_name", sa.String),
        sa.Column("io_pointer_value", sa.LargeBinary),
        sa.ForeignKeyConstraint(
            ["io_pointer_name", "io_pointer_value"],
            ["io_pointers.name", "io_pointers.value"],
        ),
    )

    op.create_table(
        "deleted_labels",
        sa.Column(
            "label", sa.String, sa.ForeignKey("labels.id"), primary_key=True
        ),
        sa.Column("deletion_request_time", sa.DateTime),
    )


def downgrade():
    op.drop_table("labels_io_pointers")
    op.drop_table("deleted_labels")
    op.drop_table("labels")
