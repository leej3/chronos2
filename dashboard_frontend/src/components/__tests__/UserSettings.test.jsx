/* eslint-env jest */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import UserSettings from '../UserSettings/UserSettings';
import '@testing-library/jest-dom';
import { toast } from 'react-toastify';

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

const mockStore = (state) => {
  return createStore(() => state);
};

describe('UserSettings Component', () => {
  it('should render user settings component correctly with Summer mode', () => {
    const state = {
      season: {
        season: 'Summer',
      },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
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
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    const winterIcon = container.querySelector('.season-icon:not(.active)');
    const summerIcon = container.querySelector('.season-icon.active');

    expect(winterIcon.querySelector('.season-emoji').textContent).toBe('❄️');
    expect(
      winterIcon.querySelector('span:not(.season-emoji)').textContent,
    ).toBe('Winter');

    expect(summerIcon.querySelector('.season-emoji').textContent).toBe('☀️');
    expect(
      summerIcon.querySelector('span:not(.season-emoji)').textContent,
    ).toBe('Summer');

    expect(container.querySelector('#tolerance')).toHaveValue(2);
    expect(container.querySelector('#setpoint_min')).toHaveValue(45);
    expect(container.querySelector('#setpoint_max')).toHaveValue(85);
    expect(container.querySelector('#setpoint_offset_summer')).toHaveValue(5);
    expect(container.querySelector('#mode_change_delta_temp')).toHaveValue(4);
    expect(container.querySelector('#mode_switch_lockout_time')).toHaveValue(
      30,
    );
    expect(container.querySelector('#cascade_time')).toHaveValue(15);

    expect(container.querySelector('.show-settings-btn')).toHaveTextContent(
      'Show Settings',
    );
    expect(container.querySelector('.update-btn')).toHaveTextContent('Update');
  });
  it('should render user settings loading state when data is not fetched', () => {
    const state = {
      season: {
        season: 'Summer',
      },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    expect(screen.getByText('Loading user settings...')).toBeInTheDocument();
  });
  it('should handle season mode switching correctly', async () => {
    const state = {
      season: {
        season: 'Summer',
      },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
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
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    let winterIcon = container.querySelector('.season-icon:not(.active)');
    let summerIcon = container.querySelector('.season-icon.active');

    expect(winterIcon.querySelector('.season-emoji').textContent).toBe('❄️');
    expect(summerIcon.querySelector('.season-emoji').textContent).toBe('☀️');
    expect(summerIcon).toHaveClass('active');
    expect(winterIcon).not.toHaveClass('active');

    fireEvent.click(winterIcon);

    winterIcon = container.querySelector('.season-icon.active');
    summerIcon = container.querySelector('.season-icon:not(.active)');

    expect(winterIcon).toHaveClass('active');
    expect(summerIcon).not.toHaveClass('active');

    fireEvent.click(summerIcon);

    winterIcon = container.querySelector('.season-icon:not(.active)');
    summerIcon = container.querySelector('.season-icon.active');

    expect(summerIcon).toHaveClass('active');
    expect(winterIcon).not.toHaveClass('active');
  });
  it('should handle season mode switching error correctly', async () => {
    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    const state = {
      season: {
        season: 'Summer',
      },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
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
    };

    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    let winterIcon = container.querySelector('.season-icon:not(.active)');

    fireEvent.click(winterIcon);

    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(toast.error).toHaveBeenCalledWith('Failed to switch season');

    expect(
      container
        .querySelector('.season-icon.active')
        .querySelector('.season-emoji').textContent,
    ).toBe('☀️');

    consoleErrorSpy.mockRestore();
    global.fetch.mockClear();
    delete global.fetch;
    jest.clearAllMocks();
  });

  it('should handle invalid server response when switching modes', async () => {
    const state = {
      season: {
        season: 'Summer',
      },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
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
    };

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ error: 'Failed to switch season' }),
      }),
    );

    const { container } = render(
      <Provider store={mockStore(state)}>
        <UserSettings data={state.settings} />
      </Provider>,
    );

    let winterIcon = container.querySelector('.season-icon:not(.active)');

    fireEvent.click(winterIcon);

    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(toast.error).toHaveBeenCalledWith('Failed to switch season');

    expect(
      container
        .querySelector('.season-icon.active')
        .querySelector('.season-emoji').textContent,
    ).toBe('☀️');

    global.fetch.mockClear();
    delete global.fetch;
    jest.clearAllMocks();
  });
});
