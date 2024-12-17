import { createSlice } from '@reduxjs/toolkit'
import { createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios';
import { API_BASE_URL } from '../../utils/constant';

const initialState = {
    data: {},
    status: "idle",
    error: ""
}

export const fetchSummerData = createAsyncThunk("", async () => {
    const response = await axios.get(API_BASE_URL)
    return response?.data
})


export const summerSlice = createSlice({
  name: 'summer',
  initialState,
  reducers: {},
  extraReducers(builder) {
        builder
            .addCase(fetchSummerData.pending, (state, action) => {
                state.status = "loading"
            })
            .addCase(fetchSummerData.fulfilled, (state, action) => {
                state.status = "succeeded"
                state.data = action.payload;
            })
            .addCase(fetchSummerData.rejected, (state, action) => {
                state.status = "failed"
                state.error = action.error.message
            })
           
    }
})

// // Action creators are generated for each case reducer function
// export const getAllData = (state) => state.summerData.data
// export const getDataError = (state) => state.summerData.error
// export const getDataStatus = (state) => state.summerData.status


export default summerSlice.reducer