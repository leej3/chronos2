import axios from 'axios';
import { API_BASE_URL } from '../utils/constant';

const axiosApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export default axiosApi;