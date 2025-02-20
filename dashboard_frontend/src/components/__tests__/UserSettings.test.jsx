/* eslint-env jest */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import UserSettings from '../UserSettings/UserSettings';
import '@testing-library/jest-dom';

jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

jest.mock('../../utils/constant', () => ({
  API_BASE_URL: jest.fn(() => 1),
}));

jest.mock('../../api/updateBoilerSetpoint', () => ({
  getTemperatureLimits: jest.fn(),
}));

jest.mock('../UserSettings/UserSettings.css', () => {});
jest.mock('../SeasonSwitch/SeasonSwitch.css', () => {});

const mockStore = (state) => {
  return createStore(() => state);
};

describe('UserSettings Component', () => {
  it('should render user settings component correctly', () => {
    const state = {
      settings: {
        results: {
          tolerance: 2,
          setpoint_min: 45,
          setpoint_max: 85,
          setpoint_offset_summer: 5,
          setpoint_offset_winter: 3,
          mode_change_delta_temp: 4,
          mode_switch_lockout_time: 30,
          cascade_time: 15,
        },
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
        unlock_time: null,
      },
      manualOverride: {
        manual_override: false,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    expect(container.querySelector('#tolerance')).toHaveValue(2);
    expect(container.querySelector('#setpoint_min')).toHaveValue(45);
    expect(container.querySelector('#setpoint_max')).toHaveValue(85);
    expect(container.querySelector('#setpoint_offset_summer')).toHaveValue(5);
    expect(container.querySelector('#mode_change_delta_temp')).toHaveValue(4);
    expect(container.querySelector('#mode_switch_lockout_time')).toHaveValue(
      30,
    );
    expect(container.querySelector('#cascade_time')).toHaveValue(15);

    expect(container.querySelector('.update-btn')).toHaveTextContent('Update');
  });

  it('should render user settings loading state when data is not fetched', () => {
    const state = {
      chronos: {
        season: 1,
        unlock_time: null,
      },
      manualOverride: {
        manual_override: false,
      },
    };

    render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    expect(screen.getByText('Loading user settings...')).toBeInTheDocument();
  });
});
