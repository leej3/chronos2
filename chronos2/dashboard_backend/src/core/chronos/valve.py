from src.core.chronos.device import Device
from src.core.utils.config_parser import cfg


class Valve(Device):

    def __init__(self, season):
        if season not in ("winter", "summer"):
            raise ValueError("Valve must be winter or summer")
        else:
            self.relay_number = getattr(cfg.relay, "{}_valve".format(season))
            self.table_class_name = "{}Valve".format(season.capitalize())

    def __getattr__(self, name):
        if name in ("save_status", "restore_status"):
            raise AttributeError("There is no such attribute")
        super(Valve, self).__getattr__(name)

    def turn_on(self, relay_only=False):
        self._switch_state("on", relay_only=relay_only)

    def turn_off(self, relay_only=False):
        self._switch_state("off", relay_only=relay_only)