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
      boiler: false,
      chiller1: false,
      chiller2: false,
      chiller3: false,
      chiller4: false,
    },
  };

  const defaultHomedata = {
    results: { water_out_temp: 50, return_temp: 40 },
    sensors: { water_out_temp: 50, return_temp: 40 },
    boiler: { some: 'data' },
  };

  it('should render winter view with correct temperatures and formatting', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={defaultHomedata} season={0} />
      </Provider>,
    );

    expect(screen.getByText('Water Out: 50.0°F')).toBeInTheDocument();
    expect(screen.getByText('Return: 40.0°F')).toBeInTheDocument();

    const boilerImage = screen.getByAltText('Boiler');
    expect(boilerImage).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Boiler-OFF.png',
    );

    expect(screen.getByText('Manual Override')).toBeInTheDocument();
  });

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
        boiler: true,
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
        chiller1: true,
        chiller2: true,
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

    expect(screen.getByText('Water Out: N/A')).toBeInTheDocument();
    expect(screen.getByText('Return: N/A')).toBeInTheDocument();
  });

  it('should handle missing homedata prop', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap />
      </Provider>,
    );

    expect(screen.getByText('Water Out: N/A')).toBeInTheDocument();
    expect(screen.getByText('Return: N/A')).toBeInTheDocument();
  });
});
