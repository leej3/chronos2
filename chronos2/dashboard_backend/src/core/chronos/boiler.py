from src.core.chronos.device import Device
from src.core.utils.config_parser import cfg


class Boiler(Device):

    TYPE = "boiler"

    def __init__(self):
        self.number = 0
        self.relay_number = cfg.relay.boiler
        self.table_class_name = "Boiler"

    @property
    def cascade_current_power(self):
        return self._get_property_from_db("cascade_current_power")

    @property
    def lead_firing_rate(self):
        return self._get_property_from_db("lead_firing_rate")

    def set_boiler_setpoint(self, effective_setpoint):
        pass

    def read_modbus_data(self):
        pass
