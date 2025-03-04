import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

import { getDashboardData } from '../../api/getDashboardData';
const initialState = {
  devices: [],
  data: null,
  status: 'idle',
  error: null,
  season: 0,
  mock_devices: true,
  read_only_mode: false,
  lastUpdated: null,
  systemStatus: 'OFFLINE',
  unlock_time: null,
  switch_override: false,
};

export const fetchData = createAsyncThunk('chronos/fetchData', async () => {
  const response = await getDashboardData();
  return response?.data;
});

export const chronosSlice = createSlice({
  name: 'chronos',
  initialState,
  reducers: {
    setSeason(state, action) {
      state.season = action.payload;
    },
    setSwitchOverride: (state, action) => {
      state.switch_override = action.payload;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(fetchData.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchData.fulfilled, (state, action) => {
        const data = action.payload;
        state.devices = data.devices;
        state.data = data;
        state.season = data.results.mode;
        state.mock_devices = data.mock_devices;
        state.read_only_mode = data.read_only_mode;
        state.lastUpdated = new Date().toISOString();
        state.status = 'succeeded';
        state.systemStatus = data.status ? 'ONLINE' : 'OFFLINE';
        state.error = null;
        state.unlock_time =
          data.results?.unlock_time &&
          new Date(data.results.unlock_time).getTime() > new Date().getTime()
            ? new Date(data.results.unlock_time).toISOString()
            : null;
      })

      .addCase(fetchData.rejected, (state, action) => {
        state.switch_override = false;
        state.status = 'failed';
        state.systemStatus = 'OFFLINE';
        state.error = action.error.message;
        state.isFirstLoad = false;
      });
  },
});

// // Action creators are generated for each case reducer function
// export const getAllData = (state) => state.summerData.data
// export const getDataError = (state) => state.summerData.error
// export const getDataStatus = (state) => state.summerData.status
export const { setSwitchOverride, setSeason } = chronosSlice.actions;
export default chronosSlice.reducer;
