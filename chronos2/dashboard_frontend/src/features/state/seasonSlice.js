import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  season: 'default', 
  timer: false
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
  },
});

// Export the action creator
export const { setSeason } = seasonSlice.actions;

// Export the reducer
export default seasonSlice.reducer;
