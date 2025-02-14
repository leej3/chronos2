import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import UserSettings from './UserSettings';
import { updateSettings } from '../../api/updateSetting';
import { getTemperatureLimits } from '../../api/updateBoilerSetpoint';
import { toast } from 'react-toastify';

// Mock the API calls and toast functions
jest.mock('../../api/updateSetting');
jest.mock('../../api/updateBoilerSetpoint');
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Create a dummy Redux store, providing a simple reducer with initial state
const initialState = { chronos: { season: 'Summer' } };
const storeReducer = (state = initialState, action) => state;
const store = createStore(storeReducer);

// Dummy data prop for UserSettings
const dummyData = {
  results: {
    tolerance: 5,
    setpoint_min: 75,
    setpoint_max: 105,
    setpoint_offset_summer: 0,
    setpoint_offset_winter: 0,
    mode_change_delta_temp: 5,
    mode_switch_lockout_time: 10,
    cascade_time: 6,
    baseline_setpoint: 80,
    tha_setpoint: 85,
    effective_setpoint: 82,
  },
};

// Mock getTemperatureLimits to return hard limits
getTemperatureLimits.mockResolvedValue({
  hard_limits: { min_setpoint: 70, max_setpoint: 110 },
  soft_limits: { min_setpoint: 70, max_setpoint: 110 },
});

describe('UserSettings Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays error message when updateSettings fails with read-only mode error', async () => {
    // Simulate updateSettings API call rejecting with a read-only mode error
    updateSettings.mockRejectedValue({
      data: { detail: 'Operation not permitted: system is in read-only mode' },
    });

    render(
      <Provider store={store}>
        <UserSettings data={dummyData} />
      </Provider>,
    );

    // Click the button to show the settings form
    const showButton = screen.getByRole('button', { name: /show settings/i });
    fireEvent.click(showButton);

    // Click the Update button (form submission)
    const updateButton = screen.getByRole('button', { name: /update/i });
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(updateSettings).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Operation not permitted: system is in read-only mode',
      );
    });
  });

  test('displays success message when updateSettings succeeds', async () => {
    // Simulate a successful API call
    updateSettings.mockResolvedValue({
      data: { message: 'Settings updated successfully' },
    });

    render(
      <Provider store={store}>
        <UserSettings data={dummyData} />
      </Provider>,
    );

    // Click the button to show the settings form
    const showButton = screen.getByRole('button', { name: /show settings/i });
    fireEvent.click(showButton);

    // Click the Update button
    const updateButton = screen.getByRole('button', { name: /update/i });
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(updateSettings).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        'Settings updated successfully',
      );
    });
  });
});
