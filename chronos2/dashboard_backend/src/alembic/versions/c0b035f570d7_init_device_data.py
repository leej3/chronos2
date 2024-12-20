"""Init device data

Revision ID: c0b035f570d7
Revises: ffb68c387231
Create Date: 2024-12-17 09:47:50.693416

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.alembic.seeds.boiler_data import BOILER_DATA
from src.alembic.seeds.chiller_data import CHILLER1_DATA, CHILLER2_DATA, CHILLER3_DATA, CHILLER4_DATA
from src.alembic.seeds.setting_data import SETTING_DATA
from src.alembic.seeds.value_data import SUMMER_DATA, WINTER_DATA

# revision identifiers, used by Alembic.
revision: str = "c0b035f570d7"
down_revision: Union[str, None] = "ffb68c387231"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            "boiler",
            sa.column("id", sa.Integer),
            sa.column("backup", sa.Boolean),
            sa.column("timestamp", sa.DateTime),
            sa.column("switched_timestamp", sa.DateTime),
            sa.column("status", sa.Integer),
            sa.column("manual_override", sa.Integer),
            sa.column("system_supply_temp", sa.Float),
            sa.column("inlet_temp", sa.Float),
            sa.column("outlet_temp", sa.Float),
            sa.column("flue_temp", sa.Float),
            sa.column("cascade_current_power", sa.Integer),
            sa.column("lead_firing_rate", sa.Integer),
        ),
        BOILER_DATA,
    )

    op.bulk_insert(
        sa.table(
            "chiller1",
            sa.column("id", sa.Integer),
            sa.column("backup", sa.Boolean),
            sa.column("timestamp", sa.DateTime),
            sa.column("switched_timestamp", sa.DateTime),
            sa.column("status", sa.Integer),
            sa.column("manual_override", sa.Integer),
        ),
        CHILLER1_DATA,
    )

    op.bulk_insert(
        sa.table(
            "chiller2",
            sa.column("id", sa.Integer),
            sa.column("backup", sa.Boolean),
            sa.column("timestamp", sa.DateTime),
            sa.column("switched_timestamp", sa.DateTime),
            sa.column("status", sa.Integer),
            sa.column("manual_override", sa.Integer),
        ),
        CHILLER2_DATA,
    )

    op.bulk_insert(
        sa.table(
            "chiller3",
            sa.column("id", sa.Integer),
            sa.column("backup", sa.Boolean),
            sa.column("timestamp", sa.DateTime),
            sa.column("switched_timestamp", sa.DateTime),
            sa.column("status", sa.Integer),
            sa.column("manual_override", sa.Integer),
        ),
        CHILLER3_DATA,
    )

    op.bulk_insert(
        sa.table(
            "chiller4",
            sa.column("id", sa.Integer),
            sa.column("backup", sa.Boolean),
            sa.column("timestamp", sa.DateTime),
            sa.column("switched_timestamp", sa.DateTime),
            sa.column("status", sa.Integer),
            sa.column("manual_override", sa.Integer),
        ),
        CHILLER4_DATA,
    )

    op.bulk_insert(
        sa.table(
            "settings",
            sa.column("id", sa.Integer),
            sa.column("setpoint_min", sa.Float),
            sa.column("setpoint_max", sa.Float),
            sa.column("setpoint_offset_summer", sa.Float),
            sa.column("setpoint_offset_winter", sa.Float),
            sa.column("tolerance", sa.Float),
            sa.column("mode_change_delta_temp", sa.Integer),
            sa.column("cascade_time", sa.Integer),
            sa.column("mode", sa.Integer),
            sa.column("mode_switch_timestamp", sa.DateTime),
            sa.column("mode_switch_lockout_time", sa.Integer),
        ),
        SETTING_DATA,
    )

    op.bulk_insert(
        sa.table(
            "summer_valve",
            sa.column("backup", sa.Boolean),
            sa.column("status", sa.Integer),
        ),
        SUMMER_DATA,
    )

    op.bulk_insert(
        sa.table(
            "winter_valve",
            sa.column("backup", sa.Boolean),
            sa.column("status", sa.Integer),
        ),
        WINTER_DATA,
    )


def downgrade() -> None:
    pass
