from datetime import datetime

from src.core import models
from src.core.configs.database import session_scope
from src.core.repositories.setting_repository import SettingRepository


class ChillerRepository:
    def __init__(self):
        self.timestamp = datetime.now()
        self.setting = SettingRepository()

    def _update_value_in_db(self, chiller_name: str, **kwargs):
        model_class = getattr(models, chiller_name)
        to_backup = kwargs.pop("to_backup", False)
        with session_scope() as session:
            property_ = (
                session.query(model_class)
                .filter(model_class.backup == to_backup)
                .first()
            )
            for key, value in kwargs.items():
                setattr(property_, key, value)

    def _get_property_from_db(self, chiller_name: str, *args, **kwargs):
        device = getattr(models, chiller_name)
        from_backup = kwargs.pop("from_backup", False)
        with session_scope() as session:
            instance = (
                session.query(device).filter(device.backup == from_backup).first()
            )
            result = [getattr(instance, arg) for arg in args]
        if len(result) == 1:
            result = result[0]
        return result

    def set_chiller_status(self, chiller_name: str, status: int):
        self._update_value_in_db(chiller_name, "status", status)
        self._update_value_in_db(chiller_name, "switched_timestamp", self.timestamp)

    def get_chiller_status(self, chiller_name: str) -> int:
        return self._get_property_from_db(chiller_name, "status")

    def get_unlock_timestamp(self, chiller_name: str):
        return self._get_property_from_db(chiller_name, "switched_timestamp")
