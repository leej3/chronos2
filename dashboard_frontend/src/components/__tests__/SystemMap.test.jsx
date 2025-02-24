/* eslint-env jest */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';

import SystemMap from '../systemMap/SystemMap';

jest.mock('../systemMap/SystemMap.css', () => {});
jest.mock('../ManualOverride/ManualOverride.css', () => {});

jest.mock('../Modebus/Modbus.css', () => {});
jest.mock('../TypeMode/TypeMode.css', () => {});
jest.mock('../UserSettings/UserSettings.css', () => {});
jest.mock('../Sensor/tabletemplate.css', () => {});
jest.mock('../../utils/constant', () => ({
  getDeviceId: jest.fn(() => 1),
}));

const mockStore = (state) => {
  return createStore(() => state);
};

describe('SystemMap component', () => {
  const defaultState = {
    manualOverride: {
      boiler: {
        id: 0,
        state: true,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller1: {
        id: 1,
        state: false,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller2: {
        id: 2,
        state: false,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller3: {
        id: 3,
        state: false,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
      chiller4: {
        id: 4,
        state: false,
        switched_timestamp: '2024-01-01T00:00:00Z',
      },
    },
  };

  const defaultHomedata = {
    results: { water_out_temp: 50, return_temp: 40 },
    sensors: { water_out_temp: 50, return_temp: 40 },
  };

  it('should render summer view with all chillers', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={defaultHomedata} season={1} />
      </Provider>,
    );

    for (let i = 1; i <= 4; i++) {
      const chillerImage = screen.getByAltText(`Chiller ${i}`);
      expect(chillerImage).toHaveAttribute(
        'src',
        'images/Icons/Boiler/Chiller-OFF.png',
      );
    }

    expect(screen.getByText('Water Out: 50.0°F')).toBeInTheDocument();
    expect(screen.getByText('Return: 40.0°F')).toBeInTheDocument();
  });

  it('should handle manual override for boiler in winter mode', () => {
    const overrideState = {
      manualOverride: {
        ...defaultState.manualOverride,
        boiler: {
          ...defaultState.manualOverride.boiler,
          state: 1,
          switched_timestamp: '2024-01-01T00:00:00Z',
        },
      },
    };

    render(
      <Provider store={mockStore(overrideState)}>
        <SystemMap homedata={defaultHomedata} season={0} />
      </Provider>,
    );

    const boilerImage = screen.getByAltText('Boiler');

    expect(boilerImage).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Boiler-ON.png',
    );
  });

  it('should handle manual override for chillers in summer mode', () => {
    const overrideState = {
      manualOverride: {
        ...defaultState.manualOverride,
        chiller1: {
          ...defaultState.manualOverride.chiller1,
          state: 1,
          switched_timestamp: '2024-01-01T00:00:00Z',
        },
        chiller2: {
          ...defaultState.manualOverride.chiller2,
          state: 1,
          switched_timestamp: '2024-01-01T00:00:00Z',
        },
        chiller3: {
          ...defaultState.manualOverride.chiller3,
          state: 0,
          switched_timestamp: '2024-01-01T00:00:00Z',
        },
        chiller4: {
          ...defaultState.manualOverride.chiller4,
          state: 0,
          switched_timestamp: '2024-01-01T00:00:00Z',
        },
      },
    };

    render(
      <Provider store={mockStore(overrideState)}>
        <SystemMap homedata={defaultHomedata} season={1} />
      </Provider>,
    );

    expect(screen.getByAltText('Chiller 1')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Chiller-ON.png',
    );
    expect(screen.getByAltText('Chiller 2')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Chiller-ON.png',
    );

    expect(screen.getByAltText('Chiller 3')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Chiller-OFF.png',
    );
    expect(screen.getByAltText('Chiller 4')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Chiller-OFF.png',
    );
  });

  it('should handle null/undefined data gracefully', () => {
    const homedata = {
      results: { water_out_temp: null, return_temp: undefined },
      sensors: { water_out_temp: null, return_temp: undefined },
    };

    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={homedata} season={0} />
      </Provider>,
    );

    const naValues = screen.getAllByText('N/A');
    expect(naValues.length).toBeGreaterThan(0);
  });

  it('should handle missing homedata prop', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap />
      </Provider>,
    );

    const naValues = screen.getAllByText('N/A');
    expect(naValues.length).toBeGreaterThan(0);
  });
});
