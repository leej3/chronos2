from src.core.repositories.device_repository import DeviceRepository
from src.core.services.device import Device
from src.core.services.edge_server import EdgeServer
from src.core.utils.constant import Relay


class Valve(Device):
    def __init__(self, season):
        if season not in ("winter", "summer"):
            raise ValueError("Valve must be winter or summer")
        else:
            self.relay_number = Relay["{}_VALVE".format(season.upper())]
            self.table_class_name = "{}Valve".format(season.capitalize())
            self.device_repository = DeviceRepository(self.table_class_name)
            self.edge_server = EdgeServer()

    def __getattr__(self, name):
        if name in ("save_status", "restore_status"):
            raise AttributeError("There is no such attribute")
        super(Valve, self).__getattr__(name)

    def turn_on(self, relay_only=False, is_season_switch=False):
        self._switch_state(
            "on", relay_only=relay_only, is_season_switch=is_season_switch
        )

    def turn_off(self, relay_only=False, is_season_switch=False):
        self._switch_state(
            "off", relay_only=relay_only, is_season_switch=is_season_switch
        )
