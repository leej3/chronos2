import { configureStore } from '@reduxjs/toolkit';

import chronosReducer from '../features/chronos/chronosSlice';
import manualOverrideReducer from '../features/state/ManualOverrideSlice';
import summerReducer from '../features/summer/summerSlice';
import authReducer from '../redux/AuthSlice';

export const store = configureStore({
  reducer: {
    summerData: summerReducer,
    chronos: chronosReducer,
    manualOverride: manualOverrideReducer,
    auth: authReducer,
  },
});
