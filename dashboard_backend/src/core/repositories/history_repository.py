from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.sql import func
from src.core.configs.database import session_scope
from src.core.models import History, Settings


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

    def get_last_histories(self, hours=1):
        with session_scope() as session:
            timespan = datetime.now() - timedelta(hours=hours)
            rows = (
                session.query(History)
                .filter(History.timestamp > timespan)
                .order_by(desc(History.id))
                .all()
            )
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
