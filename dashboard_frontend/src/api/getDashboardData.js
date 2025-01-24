import axiosApi from './axios';

export const getDashboardData = async () => {
  return await axiosApi.get('/');
};
