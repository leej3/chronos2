import axiosApi from './axios';

export const updateUserSettings = async (settings) => {
  try {
    const response = await axiosApi.post('/settings', settings);
    return response.data;
  } catch (error) {
    throw error?.response?.data || error;
  }
};
