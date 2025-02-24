from src.core import models
from src.core.configs.database import session_scope


class DeviceRepository:
    def __init__(self, table_class_name):
        self.table_class_name = table_class_name

    def _update_value_in_db(self, **kwargs):
        model_class = getattr(models, self.table_class_name)
        to_backup = kwargs.pop("to_backup", False)
        with session_scope() as session:
            property_ = (
                session.query(model_class)
                .filter(model_class.backup == to_backup)
                .first()
            )
            for key, value in kwargs.items():
                setattr(property_, key, value)

    def _get_property_from_db(self, *args, **kwargs):
        device = getattr(models, self.table_class_name)
        from_backup = kwargs.pop("from_backup", False)
        with session_scope() as session:
            instance = (
                session.query(device).filter(device.backup == from_backup).first()
            )
            result = [getattr(instance, arg) for arg in args]
        if len(result) == 1:
            result = result[0]
        return result
