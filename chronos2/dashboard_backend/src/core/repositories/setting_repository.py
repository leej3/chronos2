from sqlalchemy import desc
from src.core.configs.database import session_scope
from src.core.models import *


class SettingRepository:
    def get_last_settings(self):
        with session_scope() as session:
            settings = session.query(Settings).order_by(desc(Settings.id)).first()
            session.expunge_all()
        return settings
