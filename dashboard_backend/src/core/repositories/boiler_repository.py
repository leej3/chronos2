from datetime import UTC, datetime

from src.core.configs.database import session_scope
from src.core.models import Boiler
from src.core.repositories.setting_repository import SettingRepository


class BoilerRepository:
    def __init__(self):
        self.timestamp = datetime.now(UTC)
        self.setting = SettingRepository()

    def _get_property_from_db(self, param, **kwargs):
        param = getattr(Boiler, param)
        to_backup = kwargs.pop("to_backup", False)

        with session_scope() as session:
            (value,) = session.query(param).filter(Boiler.backup == to_backup).first()
        return value

    def _update_property_in_db(self, param, value, **kwargs):
        param = getattr(Boiler, param)
        to_backup = kwargs.pop("to_backup", False)
        with session_scope() as session:
            session.query(Boiler).filter(Boiler.backup == to_backup).update(
                {param: value}
            )

    def set_status(self, status: int):
        self._update_property_in_db("status", status)
        self._update_property_in_db("switched_timestamp", self.timestamp)

    def get_status(self) -> int:
        return self._get_property_from_db("status")

    def get_unlock_timestamp(self):
        return self._get_property_from_db("switched_timestamp")
