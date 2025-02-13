import axiosApi from './axios';

export const updateBoilerSetpoint = async (temperature) => {
  return await axiosApi.post('/boiler_set_setpoint', { temperature });
};
