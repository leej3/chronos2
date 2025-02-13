import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

import { getDashboardData } from '../../api/getDashboardData';

const initialState = {
  data: null,
  status: 'idle',
  error: null,
  season: 0,
  mock_devices: true,
  read_only_mode: false,
  lastUpdated: null,
};

export const fetchData = createAsyncThunk('chronos/fetchData', async () => {
  const response = await getDashboardData();
  return response?.data;
});

export const chronosSlice = createSlice({
  name: 'chronos',
  initialState,
  reducers: {},
  extraReducers(builder) {
    builder
      .addCase(fetchData.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchData.fulfilled, (state, action) => {
        const data = action.payload;
        console.log('Received data from backend:', data);
        state.data = data;
        state.season = data.results.mode;
        state.mock_devices = data.mock_devices;
        state.read_only_mode = data.read_only_mode;
        console.log('Updated read_only_mode state:', state.read_only_mode);
        state.lastUpdated = new Date().toISOString();
        state.status = 'succeeded';
        state.error = null;
      })
      .addCase(fetchData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
        state.isFirstLoad = false;
      });
  },
});

// // Action creators are generated for each case reducer function
// export const getAllData = (state) => state.summerData.data
// export const getDataError = (state) => state.summerData.error
// export const getDataStatus = (state) => state.summerData.status

export default chronosSlice.reducer;
