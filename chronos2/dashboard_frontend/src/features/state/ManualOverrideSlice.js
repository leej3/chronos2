// src/features/state/ManualOverrideSlice.js
import { createSlice } from '@reduxjs/toolkit';

const manualOverrideSlice = createSlice({
  name: 'manualOverride',
  initialState: {
    boiler: 'auto',
    chiller1: 'auto',
    chiller2: 'auto',
    chiller3: 'auto',
    chiller4: 'auto',
  },

  reducers: {
    setOverride: (state, action) => {
      const { name, value } = action.payload;
      if (state.hasOwnProperty(name)) {
        state[name] = value;
      }
    },
    setInitialState: (state, action) => {
      return { ...state, ...action.payload };
    },
  },
});

export const { setOverride, setInitialState } = manualOverrideSlice.actions;
export default manualOverrideSlice.reducer;
