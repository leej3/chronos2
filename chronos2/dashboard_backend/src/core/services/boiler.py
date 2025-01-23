from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.utils.constant import Relay


class Boiler:

    TYPE = "boiler"

    def __init__(self):
        self.number = 0
        self.relay_number = Relay.BOILER
        self.table_class_name = "Boiler"
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()

    @property
    def cascade_current_power(self):
        return self.history_repository._get_property_from_db("cascade_current_power")

    @property
    def lead_firing_rate(self):
        return self.history_repository._get_property_from_db("lead_firing_rate")

    def set_boiler_setpoint(self, effective_setpoint):
        pass

    def read_modbus_data(self):
        pass
