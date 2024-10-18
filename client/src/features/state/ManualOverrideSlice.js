import { createSlice } from '@reduxjs/toolkit';

const manualOverrideSlice = createSlice({
  name: 'manualOverride',
  initialState: {},
  reducers: {
    setInitialState: (state, action) => {
      return { ...action.payload };
    },
    setOverride: (state, action) => {
      const { device, value } = action.payload;
      state[device] = value;
    },
  },
});

export const { setOverride, setInitialState } = manualOverrideSlice.actions;

export default manualOverrideSlice.reducer;
