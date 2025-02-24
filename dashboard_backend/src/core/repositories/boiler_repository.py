from datetime import datetime

from src.core.configs.database import session_scope
from src.core.models import Boiler
from src.core.repositories.setting_repository import SettingRepository


class BoilerRepository:
    def __init__(self):
        self.timestamp = datetime.now()
        self.setting = SettingRepository()

    def _get_property_from_db(self, param):
        param = getattr(Boiler, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value

    def _update_property_in_db(self, param, value):
        param = getattr(Boiler, param)
        with session_scope() as session:
            session.query(Boiler).filter(Boiler.id == 1).update({param: value})

    def set_status(self, status: int):
        self._update_property_in_db("status", status)
        self._update_property_in_db("switched_timestamp", self.timestamp)

    def get_status(self) -> int:
        return self._get_property_from_db("status")

    def get_unlock_timestamp(self):
        return self._get_property_from_db("switched_timestamp")
