/* global jest, it, expect */
import React from 'react';

import { render, screen, fireEvent, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';

import { updateDeviceState } from '../../api/updateState';
import ManualOverride from '../ManualOverride/ManualOverride';

jest.mock('../ManualOverride/ManualOverride.css', () => {});
jest.mock('../../api/updateState');
jest.mock('../../utils/constant', () => ({
  getDeviceId: jest.fn(() => 1),
}));

const mockStore = configureStore([]);

it('should render and toggle device states', async () => {
  updateDeviceState.mockResolvedValue({
    message: 'Updated state successfully',
  });

  const store = mockStore({
    manualOverride: {
      boiler: {
        id: 0,
        status: true,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller1: {
        id: 1,
        status: false,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller2: {
        id: 2,
        status: true,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller3: {
        id: 3,
        status: true,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller4: {
        id: 4,
        status: true,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
    },
    chronos: {
      read_only_mode: false,
      season: 0,
    },
  });
  const devices = [
    { id: 0, state: true },
    { id: 1, state: true },
    { id: 2, state: true },
    { id: 3, state: true },
    { id: 4, state: true },
  ];
  render(
    <Provider store={store}>
      <ManualOverride
        data={{
          devices,
        }}
      />
    </Provider>,
  );

  expect(screen.getByText('Boiler')).toBeInTheDocument();
  expect(screen.getByText('Chiller1')).toBeInTheDocument();

  const boilerSwitch = screen
    .getByText('Boiler')
    .closest('div')
    .querySelector('input');
  await act(async () => {
    fireEvent.click(boilerSwitch);
  });

  expect(updateDeviceState).toHaveBeenCalledTimes(1);
  expect(updateDeviceState).toHaveBeenCalledWith({
    id: 1,
    state: true,
  });
});
