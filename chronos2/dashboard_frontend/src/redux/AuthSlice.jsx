import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isLoggedIn: !!localStorage.getItem('access_token'),
  accessToken: localStorage.getItem('access_token') || null,
  refreshToken: localStorage.getItem('refresh_token') || null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    login: (state, action) => {
      state.isLoggedIn = true;
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      localStorage.setItem('access_token', action.payload.accessToken);
      localStorage.setItem('refresh_token', action.payload.refreshToken);
    },
    logout: (state) => {
      state.isLoggedIn = false;
      state.accessToken = null;
      state.refreshToken = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    setAccessToken: (state, action) => {
      state.accessToken = action.payload;
      state.isLoggedIn = !!action.payload;
      if (action.payload) {
        localStorage.setItem('access_token', action.payload);
      } else {
        localStorage.removeItem('access_token');
      }
    },
  },
});

export const { login, logout, setAccessToken } = authSlice.actions;

export default authSlice.reducer;
