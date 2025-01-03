import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import SystemMap from '../systemMap/SystemMap';
import React from 'react';

jest.mock('../systemMap/SystemMap.css', () => {});

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

    expect(screen.getByAltText('Tank')).toHaveAttribute('src', 'images/Icons/Boiler/Boiler-ON.png');
    expect(screen.getByText("50°F")).toBeInTheDocument();
    expect(screen.getByText("40°F")).toBeInTheDocument();
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
    expect(screen.getByAltText('Tank')).toHaveAttribute('src', 'images/Icons/Boiler/Boiler-OFF.png');
    expect(screen.getByText("70°F")).toBeInTheDocument();
    expect(screen.getByText("60°F")).toBeInTheDocument();
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

    const loadingContainer = container.querySelector('.loading-container');
    expect(loadingContainer).toBeInTheDocument();
  });
});
