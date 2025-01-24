import { useState } from 'react';

import { useDispatch } from 'react-redux';

import axiosApi from '../api/axios';
import { setAccessToken } from '../redux/AuthSlice';

const UseTokenRefresh = () => {
  const dispatch = useDispatch();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshAccessToken = async (refresh_token) => {
    setIsRefreshing(true);
    try {
      const response = await axiosApi.post('auth/token/refresh', {
        refresh_token: refresh_token,
      });
      const { access, refresh } = response.data.tokens;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      dispatch(setAccessToken(access));
      setIsRefreshing(false);
      return access;
    } catch (error) {
      setIsRefreshing(false);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      throw error;
    }
  };

  return { refreshAccessToken, isRefreshing };
};

export default UseTokenRefresh;
