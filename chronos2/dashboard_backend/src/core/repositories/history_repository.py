from sqlalchemy import desc, or_
from sqlalchemy.sql import func
from src.core.configs.database import session_scope
from src.core.models import *


class HistoryRepository:
    def _get_property_from_db(self, param):
        param = getattr(History, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value

    def get_last_history(self):
        with session_scope() as session:
            history = session.query(History).order_by(desc(History.id)).first()
            session.expunge_all()
        return history

    def get_last_histories(self, limit=40):
        with session_scope() as session:
            rows = session.query(History).order_by(desc(History.id)).limit(limit).all()
            session.expunge_all()
        return rows

    def three_minute_avg_delta(self):
        with session_scope() as session:
            result = (
                session.query(History.delta)
                .order_by(desc(History.id))
                .limit(3)
                .subquery()
            )
            (avg_result,) = session.query(func.avg(result.c.delta)).first()
            session.expunge_all()
        return avg_result

    def _get_property_from_db(self, param):
        param = getattr(Settings, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value
