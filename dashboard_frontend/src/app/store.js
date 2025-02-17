import { configureStore } from '@reduxjs/toolkit';

import chronosReducer from '../features/chronos/chronosSlice';
import temperatureReducer from '../features/chronos/temperatureSlice';
import manualOverrideReducer from '../features/state/ManualOverrideSlice';
import authReducer from '../redux/AuthSlice';
export const store = configureStore({
  reducer: {
    chronos: chronosReducer,
    temperature: temperatureReducer,
    manualOverride: manualOverrideReducer,
    auth: authReducer,
  },
});
