import axiosApi from './axios';

export const getCharData = async () => {
  return await axiosApi.get('/chart_data');
};
