from enum import Enum

# WEATHER_URL = "https://test.barnreportpro.com/api/live_data/divy"
WEATHER_URL = "https://barnreportpro.com/api/live_data/tlco"


WEATHER_HEADERS = {
    "Authorization": "Bearer -_--8-_FLa0Ny995DE__--Hd._L6si4-CB3W-_.O4D_x.UOyP9n-zx_n9sp10H07cC-_.7g-5s96.CJ7tU.E699K8..A8_7-l9hHs._b93_9_.X.v04.5erQbM.-7_6R"
}
OFF, ON = 0, 1
MANUAL_OFF, MANUAL_ON, MANUAL_AUTO = 2, 1, 0
VALVES_SWITCH_TIME = 1

EFFICIENCY_HOUR = 12


# TODO: Replace these constants with Enum
class State(Enum):
    OFF = 0
    ON = 1


class ManualState(Enum):
    MANUAL_OFF = 2
    MANUAL_ON = 1
    MANUAL_AUTO = 0


class ValveSwitchTime(Enum):
    VALVES_SWITCH_TIME = 2


class Relay(Enum):
    BOILER = 0
    CHILLER1 = 1
    CHILLER2 = 2
    CHILLER3 = 3
    CHILLER4 = 4
    WINTER_VALVE = 5
    SUMMER_VALVE = 6
    LED_BREATHER = 7
    LED_RED = 8
    LED_GREEN = 9
    LED_BLUE = 10


class Mode(Enum):
    WINTER = 0
    SUMMER = 1
    WAITING_SWITCH_TO_WINTER = 2
    WAITING_SWITCH_TO_SUMMER = 3
    SWITCHING_TO_WINTER = 4
    SWITCHING_TO_SUMMER = 5
