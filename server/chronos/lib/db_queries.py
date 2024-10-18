import json
from chronos.lib import db
from sqlalchemy.sql import func
from sqlalchemy import desc, or_
from datetime import datetime, timedelta
from chronos.lib.config_parser import cfg


def get_chart_data():
    with db.session_scope() as session:
        rows = session.query(
            db.History.return_temp,
            db.History.timestamp,
            db.History.water_out_temp,
        ).order_by(desc(db.History.id)).limit(40).all()
        data = [{
            "column-1": row.water_out_temp,
            "column-2": row.return_temp,
            "date": row.timestamp.strftime("%Y-%m-%d %H:%M")
        } for row in reversed(rows)]
    return json.dumps(data)


def three_minute_avg_delta():
    with db.session_scope() as session:
        result = session.query(
            db.History.delta
        ).order_by(desc(db.History.id)).limit(3).subquery()
        avg_result, = session.query(func.avg(result.c.delta)).first()
    return avg_result


def get_last_data():
    with db.session_scope() as session:
        history = session.query(db.History).order_by(desc(db.History.id)).first()
        settings = session.query(db.Settings).first()
        session.expunge(history)
        session.expunge(settings)
    return history, settings


def log_generator():
    slice_ = 256
    offset = 0
    limit = 256
    stop = False
    log_limit = datetime.now() - timedelta(days=1)
    headers = ["LID", "logdatetime", "outsideTemp", "effective_setpoint",
               "waterOutTemp", "returnTemp", "boilerStatus",
               "cascadeFireRate", "leadFireRate", "chiller1Status",
               "chiller2Status", "chiller3Status", "chiller4Status",
               "setPoint2", "parameterX_winter", "parameterX_summer",
               "t1", "MO_B", "MO_C1", "MO_C2",
               "MO_C3", "MO_C4", "mode", "CCT", "windSpeed",
               "avgOutsideTemp"]
    yield ",".join(headers) + "\n"
    while not stop:
        with db.session_scope() as session:
            rows = session.query(
                db.History.id,
                db.History.timestamp,
                db.History.outside_temp,
                db.History.effective_setpoint,
                db.History.water_out_temp,
                db.History.return_temp,
                db.History.boiler_status,
                db.History.cascade_fire_rate,
                db.History.lead_fire_rate,
                db.History.chiller1_status,
                db.History.chiller2_status,
                db.History.chiller3_status,
                db.History.chiller4_status,
                db.History.tha_setpoint,
                db.History.setpoint_offset_winter,
                db.History.setpoint_offset_summer,
                db.History.tolerance,
                db.History.boiler_manual_override,
                db.History.chiller1_manual_override,
                db.History.chiller2_manual_override,
                db.History.chiller3_manual_override,
                db.History.chiller4_manual_override,
                db.History.mode,
                db.History.cascade_time,
                db.History.wind_speed,
                db.History.avg_outside_temp
            ).order_by(desc(db.History.id)).slice(offset, limit).all()
        offset += slice_
        limit += slice_
        if rows:
            for row in rows:
                if row[1] > log_limit:
                    str_row = [row.strftime("%d %b %I:%M %p") if isinstance(
                        row, datetime) else str(row) for row in row]
                    yield ",".join(str_row) + "\n"
                else:
                    stop = True
                    break
        else:
            stop = True


def calculate_efficiency():
    hours = cfg.efficiency.hours
    timespan = datetime.now() - timedelta(hours=hours)
    with db.session_scope() as session:
        amount_minutes = session.query(
            db.History.chiller1_status,
            db.History.chiller2_status,
            db.History.chiller3_status,
            db.History.chiller4_status,
        ).order_by(desc(db.History.id)).filter(
            db.History.mode == 1,
            db.History.timestamp > timespan,
            or_(
                db.History.chiller1_status == 1,
                db.History.chiller2_status == 1,
                db.History.chiller3_status == 1,
                db.History.chiller4_status == 1
            )
        ).count()
        rows = session.query(
            db.History.return_temp,
            db.History.effective_setpoint
        ).order_by(desc(db.History.id)).filter(
            db.History.timestamp > timespan
        ).subquery()
        effective_setpoint_avg, inlet_temp_avg = session.query(
            func.avg(rows.c.effective_setpoint),
            func.avg(rows.c.return_temp)
        ).first()
    effective_setpoint_avg = effective_setpoint_avg or 0
    inlet_temp_avg = inlet_temp_avg or 0
    average_temperature_difference = round(inlet_temp_avg - effective_setpoint_avg, 1)
    chiller_efficiency = round(amount_minutes / float(4 * 60 * hours), 1)
    return {
        "average_temperature_difference": average_temperature_difference,
        "chillers_efficiency": chiller_efficiency
    }


def keep_history_for_last_week():
    with db.session_scope() as session:
        old_history = session.query(db.History).filter(
            db.History.timestamp < (datetime.now() - timedelta(days=7))
        )
        old_history.delete()
