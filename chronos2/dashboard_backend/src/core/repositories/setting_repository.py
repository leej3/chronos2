from src.core.configs.database import session_scope
from src.core.models import *
from sqlalchemy import desc


class SettingRepository:
    def get_last_settings(self):
        with session_scope() as session:
            settings = session.query(Settings).order_by(desc(Settings.id)).first()
            session.expunge_all()
        return settings

    def _get_property_from_db(self, param):
        param = getattr(Settings, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value
