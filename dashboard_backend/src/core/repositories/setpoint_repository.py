from typing import Optional

from src.core.configs.database import session_scope
from src.core.models import SetpointLookup


class SetpointRepository:
    def get_setpoint_by_param_value(self, param: str, value: int) -> Optional[int]:
        with session_scope() as session:
            return (
                session.query(SetpointLookup)
                .filter(getattr(SetpointLookup, param) == value)
                .first()
                .setpoint
                if hasattr(SetpointLookup, param)
                else None
            )
