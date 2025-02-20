import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

import { getCharData } from '../../api/getCharData';

const initialState = {
  data: null,
  status: 'idle',
  error: null,
};

export const fetchCharData = createAsyncThunk(
  'temperature/fetchCharData',
  async () => {
    const response = await getCharData();
    return response?.data;
  },
);

export const temperatureSlice = createSlice({
  name: 'temperature',
  initialState,
  reducers: {},
  extraReducers(builder) {
    builder
      .addCase(fetchCharData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchCharData.fulfilled, (state, action) => {
        state.data = action.payload;
        state.status = 'succeeded';
      })
      .addCase(fetchCharData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export default temperatureSlice.reducer;
