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
  it('should render system map for Winter season with boiler status', () => {
    const state = {
      season: { season: 'Winter' },
      manualOverride: {
        boiler: true,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
    };
    const homedata = {
      results: { water_out_temp: 50, return_temp: 40 },
      sensors: { water_out_temp: 50, return_temp: 40 },
    };

    render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>,
    );

    expect(screen.getByAltText('Boiler')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Boiler-ON.png',
    );

    // Check for exact temperature strings
    const temperatures = screen.getAllByText('50.0°F');
    expect(temperatures).toHaveLength(1);
    const returnTemps = screen.getAllByText('40.0°F');
    expect(returnTemps).toHaveLength(1);
  });

  it('should render system map for Summer season with chiller status', () => {
    const state = {
      season: { season: 'Summer' },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
    };
    const homedata = {
      results: { water_out_temp: 70, return_temp: 60 },
      sensors: { water_out_temp: 70, return_temp: 60 },
    };

    render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>,
    );
    expect(screen.getByAltText('Chiller 1')).toHaveAttribute(
      'src',
      'images/Icons/Boiler/Chiller-OFF.png',
    );

    // Check for exact temperature strings
    const outTemps = screen.getAllByText('70.0°F');
    expect(outTemps).toHaveLength(1);
    const returnTemps = screen.getAllByText('60.0°F');
    expect(returnTemps).toHaveLength(1);
  });

  it('should show loading screen when season is not set', () => {
    const state = {
      season: { season: 'Unknown' },
      manualOverride: {
        boiler: false,
        chiller1: false,
        chiller2: false,
        chiller3: false,
        chiller4: false,
      },
    };
    const homedata = {
      results: { water_out_temp: 'N/A', return_temp: 'N/A' },
      sensors: { water_out_temp: 'N/A', return_temp: 'N/A' },
    };

    const { container } = render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>,
    );
    const loadingContainer = container.querySelector('.container-fluid');
    expect(loadingContainer).toBeInTheDocument();
  });

  it('should handle N/A temperatures correctly', () => {
    const state = {
      season: { season: 'Winter' },
      manualOverride: { boiler: false },
    };
    const homedata = {
      results: { water_out_temp: 'N/A', return_temp: 'N/A' },
      sensors: { water_out_temp: 'N/A', return_temp: 'N/A' },
    };

    render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>,
    );

    const naTemps = screen.getAllByText('N/A');
    expect(naTemps).toHaveLength(2);
  });
});
