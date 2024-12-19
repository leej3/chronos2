import serial
import sys
from datetime import datetime
from chronos.lib.config_parser import cfg
from chronos.lib.root_logger import root_logger as logger

class Device(object):

    def _switch_state(self, command, relay_only=False):
        # TODO... why is serial used instead of modbus? If this is for
        # winter/summer we should delete it
        try:
            with serial.Serial(cfg.serial.portname, cfg.serial.baudr, timeout=1) as ser_port:
                ser_port.write("relay {} {}\n\r".format(command, self.relay_number))
        except serial.SerialException as e:
            logger.error("Serial port error: {}".format(e))
            sys.exit(1)
        else:
            logger.debug("Relay {} has been turned {}. Relay only: {}".format(
                self.relay_number, command, relay_only
            ))
            if command == "on" and not relay_only:
                self._update_value_in_db(status=ON)
            elif command == "off" and not relay_only:
                self._update_value_in_db(status=OFF)

    @property
    def relay_state(self):
        try:
            with serial.Serial(cfg.serial.portname, cfg.serial.baudr, timeout=1) as ser_port:
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

    def _send_socketio_message(self, event=None, status=None, switched_timestamp=None,
                               manual_override=None):
        if switched_timestamp:
            switched_timestamp = switched_timestamp.strftime("%B %d, %I:%M %p")
        socketio_client.send({
            "event": event,
            "message": {
                "status": status,
                "device": self.number,
                "switched_timestamp": switched_timestamp,
                "manual_override": manual_override
            }
        })

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
        self._send_socketio_message(
            event=self.TYPE, status=OFF, switched_timestamp=now
        )

    def _get_property_from_db(self, *args, **kwargs):
        device = getattr(db, self.table_class_name)
        from_backup = kwargs.pop("from_backup", False)
        with db.session_scope() as session:
            instance = session.query(device).filter(device.backup == from_backup).first()
            result = [getattr(instance, arg) for arg in args]
        if len(result) == 1:
            result = result[0]
        return result

    def _update_value_in_db(self, **kwargs):
        device = getattr(db, self.table_class_name)
        to_backup = kwargs.pop("to_backup", False)
        with db.session_scope() as session:
            property_ = session.query(device).filter(device.backup == to_backup).first()
            for key, value in kwargs.items():
                setattr(property_, key, value)

    def save_status(self):
        self._update_value_in_db(
            status=self.status,
            manual_override=self.manual_override,
            switched_timestamp=self.switched_timestamp,
            to_backup=True
        )

    def restore_status(self):
        status, manual_override, switched_timestamp = self._get_property_from_db(
            "status", "manual_override", "switched_timestamp", from_backup=True)
        self._update_value_in_db(
            status=status,
            manual_override=manual_override,
            switched_timestamp=switched_timestamp,
            to_backup=False
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
        self._send_socketio_message(event="manual_override", manual_override=manual_override)


class Chiller(Device):

    TYPE = "chiller"

    def __init__(self, number):
        if number not in range(1, 5):
            raise ValueError("Chiller number must be in range from 1 to 4")
        else:
            self.number = number
            self.relay_number = getattr(cfg.relay, "chiller{}".format(number))
            self.table_class_name = "Chiller{}".format(number)


class Boiler(Device):

    TYPE = "boiler"

    def __init__(self):
        self.number = 0
        self.relay_number = cfg.relay.boiler


    @property
    def cascade_current_power(self):
        return self._get_property_from_db("cascade_current_power")

    @property
    def lead_firing_rate(self):
        return self._get_property_from_db("lead_firing_rate")

    def set_boiler_setpoint(self, effective_setpoint):
        setpoint = int(-101.4856 + 1.7363171 * int(effective_setpoint))
        if setpoint > 0 and setpoint < 100:
            for i in range(3):
                try:
                    with modbus_session() as modbus:
                        modbus.write_register(0, 4, unit=cfg.modbus.unit)
                        modbus.write_register(2, setpoint, unit=cfg.modbus.unit)
                except (ModbusException, serial.SerialException, OSError):
                    logger.error("Modbus error")
                    time.sleep(0.5)
                else:
                    logger.info("Setpoint {} has been sent to the boiler".format(setpoint))
                    break
            else:
                logger.error("Couldn't send setpoint to the boiler.")
        else:
            logger.error("Incorrect setpoint")

    def read_modbus_data(self):
        boiler_stats = {
            "system_supply_temp": 0,
            "outlet_temp": 0,
            "inlet_temp": 0,
            "flue_temp": 0,
            "cascade_current_power": 0,
            "lead_firing_rate": 0
        }
        for i in range(1, 4):
            try:
                with modbus_session() as modbus:
                    # Read one register from 40006 address
                    # to get System Supply Temperature
                    # Memory map for the boiler is here on page 8:
                    # http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf
                    hregs = modbus.read_holding_registers(6, count=1, unit=cfg.modbus.unit)
                    # Read 9 registers from 30003 address
                    iregs = modbus.read_input_registers(3, count=9, unit=cfg.modbus.unit)
                    boiler_stats = {
                        "system_supply_temp": c_to_f(hregs.getRegister(0) / 10.0),
                        "outlet_temp": c_to_f(iregs.getRegister(5) / 10.0),
                        "inlet_temp": c_to_f(iregs.getRegister(6) / 10.0),
                        "flue_temp": c_to_f(iregs.getRegister(7) / 10.0),
                        "cascade_current_power": float(iregs.getRegister(3)),
                        "lead_firing_rate": float(iregs.getRegister(8))
                    }
            except (AttributeError, IndexError):
                logger.warning("Attempt {}. Modbus answer is empty, retrying.".format(i))
                time.sleep(1)
            except (OSError, ModbusException, serial.SerialException):
                logger.exception("Cannot connect to modbus")
                break
            else:
                logger.info("Attempt {}. {}".format(i, boiler_stats))
                break
        else:
            logger.error("Couldn't read modbus stats")
        return boiler_stats
