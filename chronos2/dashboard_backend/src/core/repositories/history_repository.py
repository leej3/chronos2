from sqlalchemy import desc, or_
from sqlalchemy.sql import func
from src.core.configs.database import session_scope
from src.core.models import *
from src.core.utils.config_parser import cfg


class HistoryRepository:
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
