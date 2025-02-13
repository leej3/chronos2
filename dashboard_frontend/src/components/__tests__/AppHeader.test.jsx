import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { createStore } from 'redux';
import AppHeader from '../Header/AppHeader';
import '@testing-library/jest-dom';

jest.mock('../../utils/dateUtils', () => ({
  getFormattedChicagoTime: () => '8:00:00 PM CST',
}));
jest.mock('../../utils/constant', () => ({
  API_BASE_URL: jest.fn(() => 1),
}));
const mockStore = (state) => {
  return createStore(() => state);
};
jest.mock('../Header/AppHeader.css', () => {});

const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (args[0].includes('Warning: validateDOMNesting')) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});



afterAll(() => {
  console.error = originalError;
});

describe('AppHeader Component', () => {
  const renderAppHeader = (state) => {
    return render(
      <Provider store={mockStore(state)}>
        <BrowserRouter future={{ v7_startTransition: true }}>
          <AppHeader />
        </BrowserRouter>
      </Provider>,
    );
  };

  it('should render header with basic elements', () => {
    const state = {
      chronos: {
        mock_devices: false,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    expect(screen.getByText('Chronus Dashboard')).toBeInTheDocument();
    expect(screen.getByText('SYSTEM')).toBeInTheDocument();
    const onlineElements = screen.getAllByText('ONLINE');
    expect(onlineElements.length).toBeGreaterThan(0);
    expect(onlineElements[0]).toBeInTheDocument();
  });

  it('should show system status as OFFLINE with red indicator', () => {
    const state = {
      chronos: {
        mock_devices: false,
        systemStatus: 'OFFLINE',
      },
    };

    const { container } = renderAppHeader(state);

    const offlineElements = screen.getAllByText('OFFLINE');
    expect(offlineElements.length).toBeGreaterThan(0);
    expect(offlineElements[0]).toBeInTheDocument();
    const statusIndicator = container.querySelector('.rounded-circle');
    expect(statusIndicator).toHaveStyle({ backgroundColor: '#dc3545' });
  });

  it('should show system status as ONLINE with green indicator', () => {
    const state = {
      chronos: {
        mock_devices: false,
        systemStatus: 'ONLINE',
      },
    };

    const { container } = renderAppHeader(state);

    const onlineElements = screen.getAllByText('ONLINE');
    expect(onlineElements.length).toBeGreaterThan(0);
    expect(onlineElements[0]).toBeInTheDocument();
    const statusIndicator = container.querySelector('.rounded-circle');
    expect(statusIndicator).toHaveStyle({ backgroundColor: '#198754' });
  });

  it('should show Mock Devices Mode when mock_devices is true', () => {
    const state = {
      chronos: {
        mock_devices: true,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    const mockDeviceElements = screen.getAllByText('Mock Devices Mode');
    expect(mockDeviceElements.length).toBeGreaterThan(0);
    expect(mockDeviceElements[0]).toBeInTheDocument();
  });

  it('should not show Mock Devices Mode when mock_devices is false', () => {
    const state = {
      chronos: {
        mock_devices: false,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    expect(screen.queryByText('Mock Devices Mode')).not.toBeInTheDocument();
  });
});
