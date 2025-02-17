from sqlalchemy import desc
from src.core.configs.database import session_scope
from src.core.models import Settings


class SettingRepository:
    def _get_property_from_db(self, param):
        param = getattr(Settings, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value

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

    def _update_property_in_db(self, param, value):
        param = getattr(Settings, param)
        with session_scope() as session:
            session.query(Settings).filter(Settings.id == 1).update({param: value})
