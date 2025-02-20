export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const DEVICES = {
  boiler: 0,
  chiller1: 1,
  chiller2: 2,
  chiller3: 3,
  chiller4: 4,
};

export const getDeviceId = (device) => DEVICES[device];

export const REFRESH_TIME = 5;
export const RETRY_TIME = 10;

export const SEASON_MODE = {
  WINTER: 0,
  SUMMER: 1,
  WAITING_SWITCH_TO_WINTER: 2,
  WAITING_SWITCH_TO_SUMMER: 3,
  SWITCHING_TO_WINTER: 4,
  SWITCHING_TO_SUMMER: 5,
};
