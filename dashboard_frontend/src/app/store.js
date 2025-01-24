import { configureStore } from '@reduxjs/toolkit';

import manualOverrideReducer from '../features/state/ManualOverrideSlice';
import seasonReducer from '../features/state/seasonSlice';
import summerReducer from '../features/summer/summerSlice';
import authReducer from '../redux/AuthSlice';

export const store = configureStore({
  reducer: {
    summerData: summerReducer,
    season: seasonReducer,
    manualOverride: manualOverrideReducer,
    auth: authReducer,
  },
});
