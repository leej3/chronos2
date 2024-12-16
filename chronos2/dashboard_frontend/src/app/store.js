import { configureStore } from '@reduxjs/toolkit';
import summerReducer from '../features/summer/summerSlice';
import seasonReducer from '../features/state/seasonSlice';
import manualOverrideReducer from '../features/state/ManualOverrideSlice';

export const store = configureStore({
  reducer: {
    summerData: summerReducer,
    season: seasonReducer,
    manualOverride: manualOverrideReducer,
  },
});
