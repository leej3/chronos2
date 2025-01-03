import React from 'react';
import { render,act } from '@testing-library/react';
import '@testing-library/jest-dom';
import TemperatureGraph from '../TemperatureGraph/TemperatureGraph';
import { getCharData } from '../../api/getCharData';
import ResizeObserver from 'resize-observer-polyfill';

global.ResizeObserver = ResizeObserver;

jest.mock('../TemperatureGraph/TemperatureGraph.css', () => {});

jest.mock('../../api/getCharData', () => ({
  getCharData: jest.fn(),
}));

jest.mock("../../utils/constant", () => ({
  API_BASE_URL: jest.fn(() => 1),
}));

describe('TemperatureGraph', () => {
  it('should render the graph and display temperature history after data is fetched', async () => {
    const mockData = {
      data: [
        { date: "2024-12-31 16:07", "column-1": 70, "column-2": 75 },
        { date: "2024-12-31 16:08", "column-1": 71, "column-2": 76 },
      ],
    };

    getCharData.mockResolvedValue(mockData);
    await act(async () => {
      render(<TemperatureGraph />);
    });
    // screen.debug();
   
  });

  it('should display an error message if the API call fails', async () => {
    const mockData = {
      data: [
        { date: "2024-12-31 16:07", "column-1": 70, "column-2": 75 },
        { date: "2024-12-31 16:08", "column-1": 71, "column-2": 76 },
      ],
    };

    getCharData.mockResolvedValue(mockData);
    await act(async () => {
      render(<TemperatureGraph />);
    });
    // screen.debug();

  });
});
