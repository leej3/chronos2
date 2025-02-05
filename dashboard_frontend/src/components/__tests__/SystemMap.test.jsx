/* eslint-env jest */
import React from 'react';

import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';

import SystemMap from '../systemMap/SystemMap';

jest.mock('../systemMap/SystemMap.css', () => {});
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

  it('should render winter view correctly', () => {
    const homedata = {
      results: { water_out_temp: 50, return_temp: 40 },
      sensors: { water_out_temp: 50, return_temp: 40 },
    };

    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={homedata} season={0} />
      </Provider>,
    );

    // Check title
    expect(screen.getByText('System Map - Winter')).toBeInTheDocument();

    // Check boiler image
    const boilerImage = screen.getByAltText('Boiler');
    expect(boilerImage).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Boiler-OFF.png',
    );

    // Check temperatures
    expect(screen.getByText('50.0°F')).toBeInTheDocument();
    expect(screen.getByText('40.0°F')).toBeInTheDocument();

    // Check buttons
    ['Advanced', 'Sensors', 'Mode', 'User Setting'].forEach((buttonText) => {
      expect(screen.getByText(buttonText)).toBeInTheDocument();
    });
  });

  it('should render summer view correctly', () => {
    const homedata = {
      results: { water_out_temp: 70, return_temp: 60 },
      sensors: { water_out_temp: 70, return_temp: 60 },
    };

    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={homedata} season={1} />
      </Provider>,
    );

    // Check title
    expect(screen.getByText('System Map - Summer')).toBeInTheDocument();

    // Check chiller images
    for (let i = 1; i <= 4; i++) {
      const chillerImage = screen.getByAltText(`Chiller ${i}`);
      expect(chillerImage).toHaveAttribute(
        'src',
        'images/Icons/Boiler/Chiller-OFF.png',
      );
    }

    // Check temperatures
    expect(screen.getByText('70.0°F')).toBeInTheDocument();
    expect(screen.getByText('60.0°F')).toBeInTheDocument();
  });

  it('should handle null/undefined data gracefully', () => {
    const homedata = {
      results: { water_out_temp: null, return_temp: undefined },
      sensors: { water_out_temp: 'N/A', return_temp: 'N/A' },
    };

    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={homedata} season={0} />
      </Provider>,
    );

    // Check that N/A is displayed for missing temperatures
    const naTemps = screen.getAllByText('N/A');
    expect(naTemps).toHaveLength(2);
  });

  it('should handle empty homedata object', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap homedata={{}} season={0} />
      </Provider>,
    );

    // Component should render without crashing
    expect(screen.getByText('System Map - Winter')).toBeInTheDocument();
  });

  it('should handle missing homedata prop', () => {
    render(
      <Provider store={mockStore(defaultState)}>
        <SystemMap season={0} />
      </Provider>,
    );

    // Component should render without crashing
    expect(screen.getByText('System Map - Winter')).toBeInTheDocument();
  });
});
