from src.core.repositories.chiller_repository import ChillerRepository
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.device import Device
from src.core.utils.constant import Relay


class Chiller(Device):
    TYPE = "chiller"

    def __init__(self, number):
        if number not in range(1, 5):
            raise ValueError("Chiller number must be in range from 1 to 4")

        self.number = number
        self.relay_number = Relay[f"CHILLER{number}"]
        self.table_class_name = f"Chiller{number}"
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.chiller_repository = ChillerRepository(self.table_class_name)
        super().__init__(table_class_name=self.table_class_name)

    @property
    def setpoint(self):
        return self.setting_repository._get_property_from_db("setpoint")

    @property
    def switched_timestamp(self):
        return self.chiller_repository._get_property_from_db("switched_timestamp")

    @switched_timestamp.setter
    def switched_timestamp(self, switched_timestamp):
        self.chiller_repository._update_value_in_db(
            param="switched_timestamp",
            value=switched_timestamp,
        )

    @property
    def status(self):
        return self.chiller_repository._get_property_from_db("status")

    @status.setter
    def status(self, status):
        self.chiller_repository._update_value_in_db("status", status)
