from datetime import UTC

from src.core import models
from src.core.configs.database import session_scope
from src.core.repositories.setting_repository import SettingRepository
from src.core.utils.helpers import get_current_time


class ChillerRepository:
    def __init__(self, chiller_name: str):
        self.timestamp = get_current_time(UTC)
        self.setting = SettingRepository()
        self.chiller_name = chiller_name

    def _update_value_in_db(self, param, value, **kwargs):
        model_class = getattr(models, self.chiller_name)
        to_backup = kwargs.pop("to_backup", False)
        with session_scope() as session:
            property_ = (
                session.query(model_class)
                .filter(model_class.backup == to_backup)
                .first()
            )
            setattr(property_, param, value)

    def _get_property_from_db(self, *args, **kwargs):
        device = getattr(models, self.chiller_name)
        from_backup = kwargs.pop("from_backup", False)
        with session_scope() as session:
            instance = (
                session.query(device).filter(device.backup == from_backup).first()
            )
            result = [getattr(instance, arg) for arg in args]
        if len(result) == 1:
            result = result[0]
        return result

    def set_chiller_status(self, status: int):
        self._update_value_in_db("status", status)
        self._update_value_in_db("switched_timestamp", self.timestamp)

    def get_chiller_status(self) -> int:
        return self._get_property_from_db("status")

    def get_unlock_timestamp(self):
        return self._get_property_from_db("switched_timestamp")
