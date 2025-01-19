"""Initial migration

Revision ID: ffb68c387231
Revises:
Create Date: 2024-12-16 11:19:43.043623

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ffb68c387231"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "boiler",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("switched_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.Column("manual_override", sa.INTEGER(), nullable=False),
        sa.Column("system_supply_temp", sa.REAL(), nullable=False),
        sa.Column("outlet_temp", sa.REAL(), nullable=False),
        sa.Column("inlet_temp", sa.REAL(), nullable=False),
        sa.Column("flue_temp", sa.REAL(), nullable=False),
        sa.Column("cascade_current_power", sa.REAL(), nullable=False),
        sa.Column("lead_firing_rate", sa.REAL(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chiller1",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("switched_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.Column("manual_override", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chiller2",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("switched_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.Column("manual_override", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chiller3",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("switched_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.Column("manual_override", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chiller4",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("switched_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.Column("manual_override", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "history",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("outside_temp", sa.REAL(), nullable=False),
        sa.Column("effective_setpoint", sa.REAL(), nullable=False),
        sa.Column("water_out_temp", sa.REAL(), nullable=False),
        sa.Column("return_temp", sa.REAL(), nullable=False),
        sa.Column("boiler_status", sa.INTEGER(), nullable=False),
        sa.Column("cascade_fire_rate", sa.REAL(), nullable=False),
        sa.Column("lead_fire_rate", sa.REAL(), nullable=False),
        sa.Column("chiller1_status", sa.INTEGER(), nullable=False),
        sa.Column("chiller2_status", sa.INTEGER(), nullable=False),
        sa.Column("chiller3_status", sa.INTEGER(), nullable=False),
        sa.Column("chiller4_status", sa.INTEGER(), nullable=False),
        sa.Column("tha_setpoint", sa.REAL(), nullable=False),
        sa.Column("setpoint_offset_winter", sa.REAL(), nullable=False),
        sa.Column("setpoint_offset_summer", sa.REAL(), nullable=False),
        sa.Column("tolerance", sa.REAL(), nullable=False),
        sa.Column("boiler_manual_override", sa.INTEGER(), nullable=False),
        sa.Column("chiller1_manual_override", sa.INTEGER(), nullable=False),
        sa.Column("chiller2_manual_override", sa.INTEGER(), nullable=False),
        sa.Column("chiller3_manual_override", sa.INTEGER(), nullable=False),
        sa.Column("chiller4_manual_override", sa.INTEGER(), nullable=False),
        sa.Column("mode", sa.INTEGER(), nullable=False),
        sa.Column("cascade_time", sa.INTEGER(), nullable=False),
        sa.Column("wind_speed", sa.REAL(), nullable=False),
        sa.Column("avg_outside_temp", sa.REAL(), nullable=False),
        sa.Column("avg_cascade_fire_rate", sa.REAL(), nullable=False),
        sa.Column("delta", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "setpoint_lookup",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("wind_chill", sa.INTEGER(), nullable=True),
        sa.Column("setpoint", sa.REAL(), nullable=True),
        sa.Column("avg_wind_chill", sa.INTEGER(), nullable=True),
        sa.Column("setpoint_offset", sa.INTEGER(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "settings",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("setpoint_min", sa.REAL(), nullable=False),
        sa.Column("setpoint_max", sa.REAL(), nullable=False),
        sa.Column("setpoint_offset_summer", sa.REAL(), nullable=False),
        sa.Column("setpoint_offset_winter", sa.REAL(), nullable=False),
        sa.Column("tolerance", sa.REAL(), nullable=False),
        sa.Column("mode_change_delta_temp", sa.INTEGER(), nullable=False),
        sa.Column("cascade_time", sa.INTEGER(), nullable=False),
        sa.Column("mode", sa.INTEGER(), nullable=False),
        sa.Column("mode_switch_timestamp", sa.DateTime(), nullable=False),
        sa.Column("mode_switch_lockout_time", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "summer_valve",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "winter_valve",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("backup", sa.BOOLEAN(), nullable=False),
        sa.Column("status", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("winter_valve")
    op.drop_table("summer_valve")
    op.drop_table("settings")
    op.drop_table("setpoint_lookup")
    op.drop_table("history")
    op.drop_table("chiller4")
    op.drop_table("chiller3")
    op.drop_table("chiller2")
    op.drop_table("chiller1")
    op.drop_table("boiler")
    # ### end Alembic commands ###
