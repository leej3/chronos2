import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  season: 'default', 
};

// Create the slice
const seasonSlice = createSlice({
  name: 'season',
  initialState,
  reducers: {
    setSeason: (state, action) => {
      state.season = action.payload;
    },
  },
});

// Export the action creator
export const { setSeason } = seasonSlice.actions;

// Export the reducer
export default seasonSlice.reducer;
