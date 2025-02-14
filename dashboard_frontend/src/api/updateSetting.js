import axiosApi from './axios';

export const updateSettings = async (data) => {
  try {
    const response = await axiosApi.post('/update_settings', data);
    return response;
  } catch (error) {
    if (error.response) {
      throw error.response;
    }
    throw error;
  }
};
