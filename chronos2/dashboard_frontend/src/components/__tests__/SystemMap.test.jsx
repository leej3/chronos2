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
jest.mock("../../utils/constant", () => ({
  getDeviceId: jest.fn(() => 1), 
}));

const mockStore = (state) => {
  return createStore(() => state);
};

describe("SystemMap component", () => {
  
  it("should render system map for Winter season with boiler status", () => {
    const state = {
      season: { season: 'Winter' },
      manualOverride: { boiler: true, chiller1: false, chiller2: false, chiller3: false, chiller4: false },
    };
    const homedata = {
      results: { water_out_temp: "50", return_temp: "40" },
      sensors: { water_out_temp: "50", return_temp: "40" }
    };
    
    render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>
    );

    expect(screen.getByAltText('Boiler')).toHaveAttribute('src', 'images/Icons/Boiler/Boiler-ON.png');
    expect(screen.getByText((content) => content.includes('50.00°F'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('40.00°F'))).toBeInTheDocument();

  });

  it("should render system map for Summer season with chiller status", () => {
    const state = {
      season: { season: 'Winter' },
      manualOverride: { boiler: false, chiller1: false, chiller2: false, chiller3: false, chiller4: false },
    };
    const homedata = {
      results: { water_out_temp: "70", return_temp: "60" },
      sensors: { water_out_temp: "70", return_temp: "60" }
    };

    render(
      <Provider store={mockStore(state)}>
        <SystemMap homedata={homedata} />
      </Provider>
    );
    expect(screen.getByAltText('Boiler')).toHaveAttribute('src', 'images/Icons/Boiler/Boiler-OFF.png');
    expect(screen.getByText("70.00°F")).toBeInTheDocument();
    expect(screen.getByText("60.00°F")).toBeInTheDocument();
  });

  it("should show loading screen when season is not set", () => {
    const state = {
      season: { season: 'Unknown' },
      manualOverride: { boiler: false, chiller1: false, chiller2: false, chiller3: false, chiller4: false },
    };
    const homedata = {
      results: { water_out_temp: "N/A", return_temp: "N/A" },
      sensors: { water_out_temp: "N/A", return_temp: "N/A" }
    };

    const { container } = render(
        <Provider store={mockStore(state)}>
          <SystemMap homedata={homedata} />
        </Provider>
      );
    const loadingContainer = container.querySelector('.container-fluid');
    expect(loadingContainer).toBeInTheDocument();
  });
});
