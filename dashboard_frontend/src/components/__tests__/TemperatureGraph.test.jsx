import React from 'react';
import { render, act, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResizeObserver from 'resize-observer-polyfill';
import { getCharData } from '../../api/getCharData';
import TemperatureGraph from '../TemperatureGraph/TemperatureGraph';

global.ResizeObserver = ResizeObserver;

jest.mock('../TemperatureGraph/TemperatureGraph.css', () => {});

jest.mock('../../api/getCharData', () => ({
  getCharData: jest.fn(),
}));

jest.mock('../../utils/constant', () => ({
  API_BASE_URL: jest.fn(() => 1),
}));

describe('TemperatureGraph', () => {
  it('should render the graph and display temperature history after data is fetched', async () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
      { date: '2024-07-31T14:00:00Z', 'column-2': 85, 'column-1': 78 },
    ];
    getCharData.mockResolvedValue({ data: mockData });

    await act(async () => {
      render(<TemperatureGraph />);
    });
    expect(
      screen.getByText(/Inlet\/Outlet Temperature History/i),
    ).toBeInTheDocument();
  });
});
