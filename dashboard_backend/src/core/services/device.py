from datetime import UTC

from src.core.repositories.device_repository import DeviceRepository
from src.core.services.edge_server import EdgeServer
from src.core.utils.constant import MANUAL_AUTO, MANUAL_OFF, MANUAL_ON, OFF, ON, State
from src.core.utils.helpers import get_current_time


class Device(object):
    TYPE = "device"

    def __init__(self, table_class_name=None):
        self.device_repository = DeviceRepository(table_class_name)
        self.edge_server = EdgeServer()
        self.table_class_name = table_class_name

    def _device_state(self, id, state, is_season_switch=False):
        return self.edge_server.update_device_state(
            id=id, state=state, is_season_switch=is_season_switch
        )

    def turn_on(self, is_season_switch=False):
        self._device_state(
            id=self.relay_number,
            state=State.ON.value,
            is_season_switch=is_season_switch,
        )

        if self.TYPE == "boiler":
            switched_timestamp = get_current_time(UTC)
            self._update_value_in_db(switched_timestamp=switched_timestamp)

    def turn_off(self, is_season_switch=False):
        self._device_state(
            id=self.relay_number,
            state=State.OFF.value,
            is_season_switch=is_season_switch,
        )

        if self.TYPE == "boiler":
            switched_timestamp = get_current_time(UTC)
            self._update_value_in_db(switched_timestamp=switched_timestamp)

    def _get_property_from_db(self, *args, **kwargs):
        return self.device_repository._get_property_from_db(*args, **kwargs)

    def _update_value_in_db(self, **kwargs):
        return self.device_repository._update_value_in_db(**kwargs)

    def save_status(self):
        self._update_value_in_db(
            status=self.status,
            manual_override=self.manual_override,
            switched_timestamp=self.switched_timestamp,
            to_backup=True,
        )

    def restore_status(self):
        status, manual_override, switched_timestamp = self._get_property_from_db(
            "status", "manual_override", "switched_timestamp", from_backup=True
        )
        self._update_value_in_db(
            status=status,
            manual_override=manual_override,
            switched_timestamp=switched_timestamp,
            to_backup=False,
        )

    @property
    def timestamp(self):
        return self._get_property_from_db("timestamp")

    @property
    def switched_timestamp(self):
        return self._get_property_from_db("switched_timestamp")

    @property
    def status(self):
        return self._get_property_from_db("status")

    @property
    def manual_override(self):
        return self._get_property_from_db("manual_override")

    @manual_override.setter
    def manual_override(self, manual_override, is_season_switch=False):
        if manual_override == MANUAL_ON:
            if self.status != ON:
                self.turn_on(is_season_switch=is_season_switch)
            self._update_value_in_db(manual_override=MANUAL_ON)
        elif manual_override == MANUAL_OFF:
            if self.status != OFF:
                self.turn_off(is_season_switch=is_season_switch)
            self._update_value_in_db(manual_override=MANUAL_OFF)
        elif manual_override == MANUAL_AUTO:
            self._update_value_in_db(manual_override=MANUAL_AUTO)
