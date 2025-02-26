from datetime import UTC

from src.core.repositories.device_repository import DeviceRepository
from src.core.services.edge_server import EdgeServer
from src.core.utils.constant import MANUAL_AUTO, MANUAL_OFF, MANUAL_ON, OFF, ON
from src.core.utils.helpers import get_current_time


class Device(object):
    TYPE = "device"

    def __init__(self, table_class_name=None):
        self.device_repository = DeviceRepository(table_class_name)
        self.edge_server = EdgeServer()
        self.table_class_name = table_class_name

    def _switch_state(self, command, relay_only=False, is_season_switch=False):
        return self.edge_server._switch_state(command, relay_only, is_season_switch)

    # @property
    # def relay_state(self):
    #     # try:
    #     #     with serial.Serial(cfg.serial.portname, cfg.serial.baudr, timeout=1) as ser_port:
    #     #         ser_port.write("relay read {}\n\r".format(self.relay_number))
    #     #         response = ser_port.read(25)
    #     # except serial.SerialException as e:
    #     #     logger.error("Serial port error: {}".format(e))
    #     #     sys.exit(1)
    #     # else:
    #     #     if "on" in response:
    #     #         state = True
    #     #     elif "off" in response:
    #     #         state = False
    #     #     else:
    #     #         logger.error("Unexpected response: {}".format(response))
    #     #     return state
    #     # TODO: edge server
    #     return False

    def turn_on(self, relay_only=False, is_season_switch=False):
        self._switch_state(
            "on", relay_only=relay_only, is_season_switch=is_season_switch
        )

        if not relay_only and self.TYPE == "boiler":
            switched_timestamp = get_current_time(UTC)
            self._update_value_in_db(switched_timestamp=switched_timestamp)

    def turn_off(self, relay_only=False, is_season_switch=False):
        self._switch_state(
            "off", relay_only=relay_only, is_season_switch=is_season_switch
        )

        if not relay_only and self.TYPE == "boiler":
            switched_timestamp = get_current_time(UTC)
            self._update_value_in_db(
                timestamp=switched_timestamp, switched_timestamp=switched_timestamp
            )

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
