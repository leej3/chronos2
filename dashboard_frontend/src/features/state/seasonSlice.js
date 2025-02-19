import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  season: 'Summer',
  mockDevices: false,
  systemStatus: 'OFFLINE',
  read_only_mode: false,
  manual_override: false,
};

// Create the slice
const seasonSlice = createSlice({
  name: 'season',
  initialState,
  reducers: {
    setSeason: (state, action) => {
      state.season = action.payload;
    },
    setMockDevices: (state, action) => {
      state.mockDevices = action.payload;
    },
    setSystemStatus: (state, action) => {
      state.systemStatus = action.payload;
    },
    setManualOverride: (state, action) => {
      state.manual_override = action.payload;
    },
  },
});

// Export the action creator
export const { setSeason, setMockDevices, setSystemStatus, setManualOverride } =
  seasonSlice.actions;

// Export the reducer
export default seasonSlice.reducer;
