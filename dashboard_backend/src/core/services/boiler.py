from src.core.repositories.boiler_repository import BoilerRepository
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.device import Device
from src.core.utils.constant import Relay


class Boiler(Device):
    TYPE = "boiler"

    def __init__(self):
        super().__init__("Boiler")
        self.number = 0
        self.relay_number = Relay.BOILER.value
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.boiler_repository = BoilerRepository()

    @property
    def cascade_current_power(self):
        return self.history_repository._get_property_from_db("cascade_current_power")

    @property
    def lead_firing_rate(self):
        return self.history_repository._get_property_from_db("lead_firing_rate")

    @property
    def switched_timestamp(self):
        return self.boiler_repository._get_property_from_db("switched_timestamp")

    @switched_timestamp.setter
    def switched_timestamp(self, switched_timestamp):
        self.boiler_repository._update_property_in_db(
            param="switched_timestamp",
            value=switched_timestamp,
        )

    @property
    def status(self):
        return self.boiler_repository._get_property_from_db("status")

    @status.setter
    def status(self, status):
        self.boiler_repository._update_property_in_db("status", status)

    def set_boiler_setpoint(self, effective_setpoint):
        pass

    def read_modbus_data(self):
        pass
