import os
# from src.chronos.lib import Chronos, WINTER, SUMMER, TO_WINTER, TO_SUMMER, db_queries
# from chronos.lib.config_parser import cfg

class DashboardService:
    def __init__(self):
        # self.chronos = Chronos()
        pass

    # def get_chronos_status():
    #     chronos_status = True
    #     try:
    #         with open("/var/run/chronos.pid") as pid_file:
    #             pid = int(pid_file.readline())
    #     except IOError:
    #         chronos_status = False
    #     else:
    #         chronos_status = os.path.exists("/proc/{}".format(pid))
    #     return chronos_status

    def get_data(self):
        # history, settings = db_queries.get_last_data()
        # results = {
        #     "outside_temp": history.outside_temp,
        #     "baseline_setpoint": self.chronos.baseline_setpoint,
        #     "tha_setpoint": history.tha_setpoint,
        #     "effective_setpoint": history.effective_setpoint,
        #     "tolerance": settings.tolerance,
        #     "setpoint_min": settings.setpoint_min,
        #     "setpoint_max": settings.setpoint_max,
        #     "mode_change_delta_temp": settings.mode_change_delta_temp,
        #     "mode_switch_lockout_time": settings.mode_switch_lockout_time,
        #     "return_temp": self.chronos.return_temp,
        #     "water_out_temp": self.chronos.water_out_temp,
        #     "mode": settings.mode,
        #     "setpoint_offset_summer": settings.setpoint_offset_summer,
        #     "setpoint_offset_winter": settings.setpoint_offset_winter,
        #     "cascade_time": settings.cascade_time / 60,
        #     "wind_chill_avg": history.avg_outside_temp
        # }
        # efficiency = db_queries.calculate_efficiency()
        # efficiency["cascade_fire_rate_avg"] = round(self.chronos.cascade_fire_rate_avg, 1)
        # efficiency["hours"] = cfg.efficiency.hours
        # actStream = [{
        #     "timeStamp": device.switched_timestamp.strftime("%B %d, %I:%M %p"),
        #     "status": device.status,
        #     "MO": device.manual_override} for device in self.chronos.devices
        # ]
        # return {
        #     "results": results,
        #     "actStream": actStream,
        #     "chronos_status": self.get_chronos_status(),
        #     "efficiency": efficiency
        # }

        return {}