import axiosApi from './axios';

export const updateSettings = async (data) => {
  return await axiosApi.post('/update_settings', data);
};
