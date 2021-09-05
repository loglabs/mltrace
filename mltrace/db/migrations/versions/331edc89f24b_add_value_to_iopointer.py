"""add value to iopointer

Revision ID: 331edc89f24b
Revises: 017c5f7dc0aa
Create Date: 2021-09-03 18:40:19.411290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "331edc89f24b"
down_revision = "017c5f7dc0aa"
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraints
    op.drop_constraint(
        "component_runs_inputs_input_path_name_fkey",
        "component_runs_inputs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "component_runs_outputs_output_path_name_fkey",
        "component_runs_outputs",
        type_="foreignkey",
    )

    op.drop_constraint("io_pointers_pkey", "io_pointers", type_="primary")
    op.add_column(
        "io_pointers",
        sa.Column(
            "value",
            sa.LargeBinary,
            nullable=True,
        ),
    )

    op.execute(f"UPDATE io_pointers SET value = ''")
    op.alter_column("io_pointers", "value", nullable=False)
    op.create_primary_key("io_pointers_pkey", "io_pointers", ["name", "value"])

    # Alter component run association tables

    # Add columns
    op.add_column(
        "component_runs_inputs",
        sa.Column("input_path_value", sa.LargeBinary),
    )
    op.add_column(
        "component_runs_outputs",
        sa.Column("output_path_value", sa.LargeBinary),
    )

    # Create foreign keys
    op.create_foreign_key(
        "fk_component_runs_inputs_io_pointers",
        "component_runs_inputs",
        "io_pointers",
        ["input_path_name", "input_path_value"],
        ["name", "value"],
    )
    op.create_foreign_key(
        "fk_component_runs_outputs_io_pointers",
        "component_runs_outputs",
        "io_pointers",
        ["output_path_name", "output_path_value"],
        ["name", "value"],
    )


def downgrade():
    # Remove columns from component run association tables
    op.drop_constraint(
        "fk_component_runs_inputs_io_pointers",
        "component_runs_inputs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_component_runs_outputs_io_pointers",
        "component_runs_outputs",
        type_="foreignkey",
    )
    op.drop_column("component_runs_inputs", "input_path_value")
    op.drop_column("component_runs_outputs", "output_path_value")

    # Remove column from iopointer
    op.drop_constraint("io_pointers_pkey", "io_pointers", type_="primary")
    op.drop_column("io_pointers", "value")
    op.create_primary_key("io_pointers_pkey", "io_pointers", ["name"])

    # Add fk constraints
    op.create_foreign_key(
        "component_runs_inputs_input_path_name_fkey",
        "component_runs_inputs",
        "io_pointers",
        ["input_path_name"],
        ["name"],
    )
    op.create_foreign_key(
        "component_runs_outputs_output_path_name_fkey",
        "component_runs_outputs",
        "io_pointers",
        ["output_path_name"],
        ["name"],
    )
