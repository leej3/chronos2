"""Add boiler status fields

Revision ID: add_boiler_status_fields
Revises: 8ef3c957fd59
Create Date: 2024-03-19 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_boiler_status_fields"
down_revision: Union[str, None] = "8ef3c957fd59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to boiler table
    op.add_column("boiler", sa.Column("operating_mode", sa.INTEGER(), nullable=True))
    op.add_column(
        "boiler", sa.Column("operating_mode_str", sa.String(50), nullable=True)
    )
    op.add_column("boiler", sa.Column("cascade_mode", sa.INTEGER(), nullable=True))
    op.add_column("boiler", sa.Column("cascade_mode_str", sa.String(50), nullable=True))
    op.add_column("boiler", sa.Column("current_setpoint", sa.REAL(), nullable=True))
    op.add_column("boiler", sa.Column("setpoint_temperature", sa.REAL(), nullable=True))
    op.add_column("boiler", sa.Column("current_temperature", sa.REAL(), nullable=True))
    op.add_column("boiler", sa.Column("pressure", sa.REAL(), nullable=True))
    op.add_column("boiler", sa.Column("error_code", sa.INTEGER(), nullable=True))

    # Update existing rows to set default values
    op.execute(
        """
        UPDATE boiler 
        SET operating_mode = 0,
            operating_mode_str = 'Unknown',
            cascade_mode = 0,
            cascade_mode_str = 'Unknown',
            current_setpoint = 0,
            setpoint_temperature = 0,
            current_temperature = 0,
            pressure = 0,
            error_code = 0
    """
    )

    # Make columns not nullable after setting defaults
    op.alter_column(
        "boiler", "operating_mode", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "boiler", "operating_mode_str", existing_type=sa.String(50), nullable=False
    )
    op.alter_column(
        "boiler", "cascade_mode", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "boiler", "cascade_mode_str", existing_type=sa.String(50), nullable=False
    )
    op.alter_column(
        "boiler", "current_setpoint", existing_type=sa.REAL(), nullable=False
    )
    op.alter_column(
        "boiler", "setpoint_temperature", existing_type=sa.REAL(), nullable=False
    )
    op.alter_column(
        "boiler", "current_temperature", existing_type=sa.REAL(), nullable=False
    )
    op.alter_column("boiler", "pressure", existing_type=sa.REAL(), nullable=False)
    op.alter_column("boiler", "error_code", existing_type=sa.INTEGER(), nullable=False)


def downgrade() -> None:
    # Remove the new columns
    op.drop_column("boiler", "error_code")
    op.drop_column("boiler", "pressure")
    op.drop_column("boiler", "current_temperature")
    op.drop_column("boiler", "setpoint_temperature")
    op.drop_column("boiler", "current_setpoint")
    op.drop_column("boiler", "cascade_mode_str")
    op.drop_column("boiler", "cascade_mode")
    op.drop_column("boiler", "operating_mode_str")
    op.drop_column("boiler", "operating_mode")
