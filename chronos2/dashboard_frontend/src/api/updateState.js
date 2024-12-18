import axiosApi from './axios';

export const updateState = async (data) => {
  return await axiosApi.post('/update_state', data);
};
