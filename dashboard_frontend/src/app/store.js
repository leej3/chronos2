import { configureStore } from '@reduxjs/toolkit';

import chronosReducer from '../features/chronos/chronosSlice';
import manualOverrideReducer from '../features/state/ManualOverrideSlice';
import authReducer from '../redux/AuthSlice';

export const store = configureStore({
  reducer: {
    chronos: chronosReducer,
    manualOverride: manualOverrideReducer,
    auth: authReducer,
  },
});
