from src.core.repositories.device_repository import DeviceRepository
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.device import Device
from src.core.services.edge_server import EdgeServer
from src.core.utils.constant import Relay


class Boiler(Device):
    TYPE = "boiler"

    def __init__(self):
        self.number = 0
        self.relay_number = Relay.BOILER.value
        self.table_class_name = "Boiler"
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.device_repository = DeviceRepository(self.table_class_name)
        self.edge_server = EdgeServer()

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
