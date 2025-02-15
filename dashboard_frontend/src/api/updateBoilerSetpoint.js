import axiosApi from './axios';

export const updateBoilerSetpoint = async (temperature) => {
  return await axiosApi.post('/boiler_set_setpoint', { temperature });
};

export const getTemperatureLimits = async () => {
  try {
    const response = await axiosApi.get('/api/temperature_limits');
    return response.data;
  } catch (error) {
    throw error?.response?.data || error;
  }
};
