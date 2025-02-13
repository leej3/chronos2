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

    @property
    def operating_mode(self):
        return self.history_repository._get_property_from_db("operating_mode")

    @property
    def operating_mode_str(self):
        return self.history_repository._get_property_from_db("operating_mode_str")

    @property
    def cascade_mode(self):
        return self.history_repository._get_property_from_db("cascade_mode")

    @property
    def cascade_mode_str(self):
        return self.history_repository._get_property_from_db("cascade_mode_str")

    @property
    def current_setpoint(self):
        return self.history_repository._get_property_from_db("current_setpoint")

    @property
    def setpoint_temperature(self):
        return self.history_repository._get_property_from_db("setpoint_temperature")

    @property
    def current_temperature(self):
        return self.history_repository._get_property_from_db("current_temperature")

    @property
    def pressure(self):
        return self.history_repository._get_property_from_db("pressure")

    @property
    def error_code(self):
        return self.history_repository._get_property_from_db("error_code")

    def set_boiler_setpoint(self, effective_setpoint):
        pass

    def read_modbus_data(self):
        pass
