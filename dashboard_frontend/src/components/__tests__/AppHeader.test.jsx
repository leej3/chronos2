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
jest.mock('../SeasonSwitch/SeasonSwitch.css', () => {});

describe('AppHeader Component', () => {
  const renderAppHeader = (state) => {
    return render(
      <Provider store={mockStore(state)}>
        <BrowserRouter>
          <AppHeader />
        </BrowserRouter>
      </Provider>,
    );
  };

  it('should render header with basic elements', () => {
    const state = {
      season: {
        mockDevices: false,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    expect(screen.getByText('Chronus Dashboard')).toBeInTheDocument();
    expect(screen.getByText('SYSTEM -')).toBeInTheDocument();
    expect(screen.getByText('ONLINE')).toBeInTheDocument();
    expect(screen.getByText('8:00:00 PM CST')).toBeInTheDocument();
  });

  it('should show system status as OFFLINE with red indicator', () => {
    const state = {
      season: {
        mockDevices: false,
        systemStatus: 'OFFLINE',
      },
    };

    const { container } = renderAppHeader(state);

    expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    const statusIndicator = container.querySelector('.rounded-circle');
    expect(statusIndicator).toHaveStyle({ backgroundColor: '#dc3545' });
  });

  it('should show system status as ONLINE with green indicator', () => {
    const state = {
      season: {
        mockDevices: false,
        systemStatus: 'ONLINE',
      },
    };

    const { container } = renderAppHeader(state);

    expect(screen.getByText('ONLINE')).toBeInTheDocument();
    const statusIndicator = container.querySelector('.rounded-circle');
    expect(statusIndicator).toHaveStyle({ backgroundColor: '#198754' });
  });

  it('should show Mock Devices Mode when mockDevices is true', () => {
    const state = {
      season: {
        mockDevices: true,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    expect(screen.getByText('Mock Devices Mode')).toBeInTheDocument();
  });

  it('should not show Mock Devices Mode when mockDevices is false', () => {
    const state = {
      season: {
        mockDevices: false,
        systemStatus: 'ONLINE',
      },
    };

    renderAppHeader(state);

    expect(screen.queryByText('Mock Devices Mode')).not.toBeInTheDocument();
  });
});
