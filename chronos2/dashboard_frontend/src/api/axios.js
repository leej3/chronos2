import axios from 'axios';
import { API_BASE_URL } from '../utils/constant';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const axiosApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

axiosApi.interceptors.request.use(
  async function (config) {
    const token = await localStorage.getItem('token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);
axiosApi.interceptors.response.use(
  function (response) {
    return response;
  },
  function (error) {
    const status = error.response?.status;
    if (status === 400) {
      toast.error(error.response?.data?.message);
    } else if (status === 401) {
      toast.error('Login session has expired, please log in again');
      localStorage.removeItem('token');
      const navigate = useNavigate();
      navigate('/login');
    }
    return Promise.reject(error);
  }
);

export default axiosApi;
