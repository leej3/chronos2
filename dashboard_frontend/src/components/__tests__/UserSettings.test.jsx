import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
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

jest.mock('../UserSettings/UserSettings.css', () => {});
jest.mock('../SeasonSwitch/SeasonSwitch.css', () => {});

jest.mock('../../api/updateSetting', () => ({
  updateSettings: jest.fn(),
}));

jest.mock('../../api/updateBoilerSetpoint', () => ({
  getTemperatureLimits: jest.fn(() =>
    Promise.resolve({
      hard_limits: { min_setpoint: 70, max_setpoint: 110 },
      soft_limits: { min_setpoint: 70, max_setpoint: 110 },
    }),
  ),
}));

const mockStore = (state) => {
  return createStore(() => state);
};

describe('UserSettings Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render user settings component correctly', () => {
    const state = {
      settings: {
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
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    expect(container.querySelector('#tolerance')).toHaveValue(5);
    expect(container.querySelector('#setpoint_min')).toHaveValue(75);
    expect(container.querySelector('#setpoint_max')).toHaveValue(105);
    expect(container.querySelector('#setpoint_offset_summer')).toHaveValue(0);
    expect(container.querySelector('#mode_change_delta_temp')).toHaveValue(5);
    expect(container.querySelector('#mode_switch_lockout_time')).toHaveValue(
      10,
    );
    expect(container.querySelector('#cascade_time')).toHaveValue(6);

    expect(container.querySelector('.update-btn')).toHaveTextContent('Update');
  });

  it('should render user settings loading state when data is not fetched', () => {
    const state = {
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    expect(screen.getByText('Loading user settings...')).toBeInTheDocument();
  });

  it('should handle input changes correctly', () => {
    const state = {
      settings: {
        results: {
          tolerance: 5,
          setpoint_min: 75,
          setpoint_max: 105,
        },
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    const toleranceInput = container.querySelector('#tolerance');
    fireEvent.change(toleranceInput, {
      target: { value: '6', name: 'tolerance' },
    });
    expect(toleranceInput).toHaveValue(6);
  });

  it('should show validation error when setpoint_min is greater than setpoint_max', async () => {
    const state = {
      settings: {
        results: {
          tolerance: 5,
          setpoint_min: 75,
          setpoint_max: 105,
        },
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    const minInput = container.querySelector('#setpoint_min');
    const maxInput = container.querySelector('#setpoint_max');
    const form = container.querySelector('form');

    fireEvent.change(minInput, {
      target: { value: '100', name: 'setpoint_min' },
    });
    fireEvent.change(maxInput, {
      target: { value: '90', name: 'setpoint_max' },
    });

    await act(async () => {
      fireEvent.submit(form);
    });

    const { toast } = jest.requireMock('react-toastify');
    expect(toast.error).toHaveBeenCalledWith(
      'Maximum setpoint must be greater than minimum setpoint',
    );
  });

  it('should show validation error when setpoint is outside hard limits', async () => {
    const state = {
      settings: {
        results: {
          tolerance: 5,
          setpoint_min: 75,
          setpoint_max: 105,
        },
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    const minInput = container.querySelector('#setpoint_min');
    const form = container.querySelector('form');

    fireEvent.change(minInput, {
      target: { value: '60', name: 'setpoint_min' },
    });

    await act(async () => {
      fireEvent.submit(form);
    });

    const { toast } = jest.requireMock('react-toastify');
    expect(toast.error).toHaveBeenCalledWith(
      'Minimum setpoint must be between 70°F and 110°F',
    );
  });

  it('should show success message on successful update', async () => {
    const state = {
      settings: {
        results: {
          tolerance: 5,
          setpoint_min: 75,
          setpoint_max: 105,
        },
      },
      chronos: {
        season: 1,
        lockoutInfo: null,
      },
    };

    const { updateSettings } = require('../../api/updateSetting');
    updateSettings.mockResolvedValueOnce({
      data: { message: 'Settings updated successfully' },
    });

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    const toleranceInput = container.querySelector('#tolerance');
    const form = container.querySelector('form');

    fireEvent.change(toleranceInput, {
      target: { value: '6', name: 'tolerance' },
    });

    await act(async () => {
      fireEvent.submit(form);
    });

    const { toast } = jest.requireMock('react-toastify');
    expect(updateSettings).toHaveBeenCalledWith(
      expect.objectContaining({
        tolerance: 6,
      }),
    );
    expect(toast.success).toHaveBeenCalledWith('Settings updated successfully');
  });
});
