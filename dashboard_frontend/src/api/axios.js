import axios from 'axios';

import { API_BASE_URL } from '../utils/constant';

const axiosApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

axiosApi.interceptors.request.use(
  async function (config) {
    const access_token = await localStorage.getItem('access_token');

    if (access_token) {
      config.headers.Authorization = `Bearer ${access_token}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  },
);

axiosApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      localStorage.getItem('refresh_token')
    ) {
      const refresh_token = localStorage.getItem('refresh_token');

      try {
        const response = await axiosApi.post('auth/token/refresh', {
          refresh_token: refresh_token,
        });
        const { access, refresh } = response.data.tokens;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        originalRequest.headers.Authorization = `Bearer ${response.data.tokens.access}`;

        return axiosApi(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return Promise.reject(refreshError);
      }
    }
    if (error.response && error.response.data) {
      return Promise.reject(error?.response?.data);
    }
    return Promise.reject(error);
  },
);

export default axiosApi;
