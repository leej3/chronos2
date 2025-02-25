import { createSlice } from '@reduxjs/toolkit';

const manualOverrideSlice = createSlice({
  name: 'manualOverride',
  initialState: {
    boiler: {
      id: 0,
      state: 'auto',
      lastSwitch: null,
    },
    chiller1: {
      id: 1,
      state: 'auto',
      lastSwitch: null,
    },
    chiller2: {
      id: 2,
      state: 'auto',
      lastSwitch: null,
    },
    chiller3: {
      id: 3,
      state: 'auto',
      lastSwitch: null,
    },
    chiller4: {
      id: 4,
      state: 'auto',
      lastSwitch: null,
    },
  },
  reducers: {
    setOverride: (state, action) => {
      const { name, value } = action.payload;
      if (Object.prototype.hasOwnProperty.call(state, name)) {
        state[name] = value;
      }
    },
    setInitialState: (state, action) => {
      return action.payload;
    },
    setUnlockTimestamp: (state, action) => {
      const { name, value } = action.payload;
      if (Object.prototype.hasOwnProperty.call(state, name)) {
        state[name].lastSwitch = value;
      }
    },
  },
});

export const { setOverride, setInitialState } = manualOverrideSlice.actions;
export default manualOverrideSlice.reducer;
