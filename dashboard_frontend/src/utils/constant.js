export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const DEVICES = {
  boiler: 0,
  chiller1: 1,
  chiller2: 2,
  chiller3: 3,
  chiller4: 4,
};

export const getDeviceId = (device) => {
  return DEVICES[device];
};

export const REFRESH_TIME = 5;
export const RETRY_TIME = 10;
