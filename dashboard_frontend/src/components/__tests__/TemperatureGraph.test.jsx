import React from 'react';
import { render, act, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResizeObserver from 'resize-observer-polyfill';
import TemperatureGraph from '../TemperatureGraph/TemperatureGraph';

global.ResizeObserver = ResizeObserver;

jest.mock('../TemperatureGraph/TemperatureGraph.css', () => {});

jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ data, children }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
      {children}
    </div>
  ),
  Line: ({ dataKey, stroke }) => (
    <div data-testid={`line-${dataKey}`} data-stroke={stroke}>
      Line-{dataKey}
    </div>
  ),
  XAxis: ({ dataKey, tickFormatter }) => (
    <div data-testid="x-axis" data-key={dataKey}>
      {tickFormatter && (
        <span>Formatted X: {tickFormatter('2024-07-31, 12:00 PM')}</span>
      )}
    </div>
  ),
  YAxis: ({ children, tickFormatter }) => (
    <div data-testid="y-axis">
      {children}
      {tickFormatter && <span>Formatted Y: {tickFormatter(75.5)}</span>}
    </div>
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid">Grid</div>,
  Tooltip: () => <div data-testid="tooltip">Tooltip</div>,
  Legend: () => <div data-testid="legend">Legend</div>,
  Label: ({ value }) => <div data-testid="axis-label">{value}</div>,
}));

describe('TemperatureGraph', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });

    jest.clearAllMocks();
  });

  it('should show loading state when no data is provided', () => {
    render(<TemperatureGraph data={null} />);
    expect(
      screen.getByText(/Loading temperature data.../i),
    ).toBeInTheDocument();
  });

  it('should render the graph when data is provided', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
      { date: '2024-07-31T14:00:00Z', 'column-2': 85, 'column-1': 78 },
    ];

    render(<TemperatureGraph data={mockData} />);

    expect(
      screen.getByText(/Inlet\/Outlet Temperature History/i),
    ).toBeInTheDocument();

    const inletLine = screen.getByTestId('line-inlet');
    const outletLine = screen.getByTestId('line-outlet');
    expect(inletLine).toBeInTheDocument();
    expect(outletLine).toBeInTheDocument();

    expect(screen.getByText('Temperature (°F)')).toBeInTheDocument();
  });

  it('should handle empty data array', () => {
    render(<TemperatureGraph data={[]} />);
    expect(
      screen.getByText(/Inlet\/Outlet Temperature History/i),
    ).toBeInTheDocument();
  });

  it('should render download button and handle click', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
    ];

    const mockLink = {
      click: jest.fn(),
      setAttribute: jest.fn(),
    };

    const originalCreateElement = document.createElement;
    document.createElement = (tagName) => {
      if (tagName === 'a') {
        return mockLink;
      }
      return originalCreateElement.call(document, tagName);
    };

    render(<TemperatureGraph data={mockData} />);

    const downloadButton = screen.getByText(/Download logs csv/i);
    expect(downloadButton).toBeInTheDocument();

    fireEvent.click(downloadButton);

    expect(mockLink.setAttribute).toHaveBeenCalledWith(
      'download',
      'temperature_data.csv',
    );
    expect(mockLink.click).toHaveBeenCalled();

    document.createElement = originalCreateElement;
  });

  it('should adjust layout for mobile view', () => {
    window.innerWidth = 767;

    fireEvent(window, new Event('resize'));

    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
    ];

    render(<TemperatureGraph data={mockData} />);

    expect(
      screen.getByText(/Inlet\/Outlet Temperature History/i),
    ).toBeInTheDocument();
  });

  it('should correctly format and display temperature data', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80.5, 'column-1': 75.3 },
      { date: '2024-07-31T14:00:00Z', 'column-2': 85.7, 'column-1': 78.9 },
    ];

    render(<TemperatureGraph data={mockData} />);

    const chartContainer = screen.getByTestId('line-chart');
    const chartData = JSON.parse(
      chartContainer.getAttribute('data-chart-data'),
    );

    expect(chartData).toHaveLength(2);
    expect(chartData[0]).toHaveProperty('inlet');
    expect(chartData[0]).toHaveProperty('outlet');

    expect(chartData[0].inlet).toBe('80.5');
    expect(chartData[0].outlet).toBe('75.3');

    const inletLine = screen.getByTestId('line-inlet');
    const outletLine = screen.getByTestId('line-outlet');
    expect(inletLine.getAttribute('data-stroke')).toBe('#ffca28');
    expect(outletLine.getAttribute('data-stroke')).toBe('#ff7043');
  });

  it('should handle time formatting correctly', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
    ];

    render(<TemperatureGraph data={mockData} />);

    const xAxis = screen.getByTestId('x-axis');
    expect(xAxis).toHaveTextContent('12:00 PM');
  });

  it('should handle Y-axis temperature formatting', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80.5, 'column-1': 75.5 },
    ];

    render(<TemperatureGraph data={mockData} />);

    const yAxis = screen.getByTestId('y-axis');
    expect(yAxis).toHaveTextContent('75.5');
    expect(screen.getByTestId('axis-label')).toHaveTextContent(
      'Temperature (°F)',
    );
  });

  it('should adjust chart display for different screen sizes', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
    ];

    window.innerWidth = 767;
    fireEvent(window, new Event('resize'));
    const { rerender } = render(<TemperatureGraph data={mockData} />);

    const chartContainerMobile = screen.getByTestId('responsive-container');
    expect(chartContainerMobile).toBeInTheDocument();

    window.innerWidth = 1024;
    fireEvent(window, new Event('resize'));
    rerender(<TemperatureGraph data={mockData} />);

    const chartContainerDesktop = screen.getByTestId('responsive-container');
    expect(chartContainerDesktop).toBeInTheDocument();
  });

  it('should handle tooltip interactions', () => {
    const mockData = [
      { date: '2024-07-31T12:00:00Z', 'column-2': 80, 'column-1': 75 },
    ];

    render(<TemperatureGraph data={mockData} />);

    const tooltip = screen.getByTestId('tooltip');
    expect(tooltip).toBeInTheDocument();
  });
});
