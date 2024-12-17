from src.core.configs.database import get_db, session
from fastapi import Depends
from sqlalchemy.orm import Session
from src.core.models import History, Settings
from sqlalchemy import desc

class HistoryRepository:

    async def get_last_data(self):
        history = session.query(History).order_by(desc(History.id)).limit(1).first()
        settings = session.query(Settings).first()
        return history, settings