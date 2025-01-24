import axiosApi from './axios';

export const updateDeviceState = async (data) => {
  return await axiosApi.post('/update_device_state', data);
};
