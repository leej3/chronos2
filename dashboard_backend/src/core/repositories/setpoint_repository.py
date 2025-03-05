from typing import Optional

from src.core.models import SetpointLookup


class SetpointRepository:
    def get_by_value(self, param, value: int) -> Optional[SetpointLookup]:
        return (
            self.session.query(SetpointLookup)
            .filter(SetpointLookup[param] == value)
            .first()
        )
