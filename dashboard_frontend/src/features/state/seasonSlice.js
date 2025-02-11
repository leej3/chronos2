import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  season: 'Summer',
  timer: false,
};

// Create the slice
const seasonSlice = createSlice({
  name: 'season',
  initialState,
  reducers: {
    setSeason: (state, action) => {
      state.season = action.payload;
      state.timer = true;
    },
    setMockDevices: (state, action) => {
      state.mockDevices = action.payload;
    },
  },
});

// Export the action creator
export const { setSeason, setMockDevices } = seasonSlice.actions;

// Export the reducer
export default seasonSlice.reducer;
