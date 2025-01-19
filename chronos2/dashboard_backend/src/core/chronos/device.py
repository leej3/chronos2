import sys
from datetime import datetime

import serial
from src.core.chronos.constant import *
from src.core.configs.database import session_scope
from src.core.configs.root_logger import root_logger as logger
from src.core.models import *
from src.core.utils.config_parser import cfg


class Device(object):
    def _switch_state(self, command, relay_only=False):
        try:
            with serial.Serial(
                cfg.serial.portname, cfg.serial.baudr, timeout=1
            ) as ser_port:
                ser_port.write("relay {} {}\n\r".format(command, self.relay_number))
        except serial.SerialException as e:
            logger.error("Serial port error: {}".format(e))
            sys.exit(1)
        else:
            logger.debug(
                "Relay {} has been turned {}. Relay only: {}".format(
                    self.relay_number, command, relay_only
                )
            )
            if command == "on" and not relay_only:
                self._update_value_in_db(status=ON)
            elif command == "off" and not relay_only:
                self._update_value_in_db(status=OFF)

    @property
    def relay_state(self):
        try:
            with serial.Serial(
                cfg.serial.portname, cfg.serial.baudr, timeout=1
            ) as ser_port:
                ser_port.write("relay read {}\n\r".format(self.relay_number))
                response = ser_port.read(25)
        except serial.SerialException as e:
            logger.error("Serial port error: {}".format(e))
            sys.exit(1)
        else:
            if "on" in response:
                state = True
            elif "off" in response:
                state = False
            else:
                logger.error("Unexpected response: {}".format(response))
            return state

    def _send_socketio_message(
        self, event=None, status=None, switched_timestamp=None, manual_override=None
    ):
        if switched_timestamp:
            switched_timestamp = switched_timestamp.strftime("%B %d, %I:%M %p")
        # socketio_client.send({
        #     "event": event,
        #     "message": {
        #         "status": status,
        #         "device": self.number,
        #         "switched_timestamp": switched_timestamp,
        #         "manual_override": manual_override
        #     }
        # })

    def turn_on(self, relay_only=False):
        self._switch_state("on", relay_only=relay_only)
        switched_timestamp = False
        if not (relay_only and isinstance(self, Boiler)):
            switched_timestamp = datetime.now()
            self._update_value_in_db(switched_timestamp=switched_timestamp)
        self._send_socketio_message(
            event=self.TYPE, status=ON, switched_timestamp=switched_timestamp
        )

    def turn_off(self, relay_only=False):
        self._switch_state("off", relay_only=relay_only)
        now = False
        if not relay_only and not isinstance(self, Boiler):
            now = datetime.now()
            self._update_value_in_db(timestamp=now, switched_timestamp=now)
        self._send_socketio_message(event=self.TYPE, status=OFF, switched_timestamp=now)

    def _get_property_from_db(self, *args, **kwargs):
        device = getattr(db, self.table_class_name)
        from_backup = kwargs.pop("from_backup", False)
        with session_scope() as session:
            instance = (
                session.query(device).filter(device.backup == from_backup).first()
            )
            result = [getattr(instance, arg) for arg in args]
        if len(result) == 1:
            result = result[0]
        return result

    def _update_value_in_db(self, **kwargs):
        print("======")
        device = getattr(db, self.table_class_name)
        to_backup = kwargs.pop("to_backup", False)
        with session_scope() as session:
            property_ = session.query(device).filter(device.backup == to_backup).first()
            for key, value in kwargs.items():
                setattr(property_, key, value)

    def save_status(self):
        self._update_value_in_db(
            status=self.status,
            manual_override=self.manual_override,
            switched_timestamp=self.switched_timestamp,
            to_backup=True,
        )

    def restore_status(self):
        status, manual_override, switched_timestamp = self._get_property_from_db(
            "status", "manual_override", "switched_timestamp", from_backup=True
        )
        self._update_value_in_db(
            status=status,
            manual_override=manual_override,
            switched_timestamp=switched_timestamp,
            to_backup=False,
        )

    @property
    def timestamp(self):
        return self._get_property_from_db("timestamp")

    @property
    def switched_timestamp(self):
        return self._get_property_from_db("switched_timestamp")

    @property
    def status(self):
        return self._get_property_from_db("status")

    @property
    def manual_override(self):
        return self._get_property_from_db("manual_override")

    @manual_override.setter
    def manual_override(self, manual_override):
        print("123456789")
        if manual_override == MANUAL_ON:
            if self.status != ON:
                self.turn_on()
            self._update_value_in_db(manual_override=MANUAL_ON)
        elif manual_override == MANUAL_OFF:
            if self.status != OFF:
                self.turn_off()
            self._update_value_in_db(manual_override=MANUAL_OFF)
        elif manual_override == MANUAL_AUTO:
            self._update_value_in_db(manual_override=MANUAL_AUTO)
        # self._send_socketio_message(
        #     event="manual_override", manual_override=manual_override
        # )
