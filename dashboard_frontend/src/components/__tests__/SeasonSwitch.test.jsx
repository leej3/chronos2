import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import { switchSeason } from '../../api/switchSeason';
import SeasonSwitch from '../SeasonSwitch/SeasonSwitch';

jest.mock('../../api/switchSeason');
jest.mock('react-redux', () => ({
  ...jest.requireActual('react-redux'),
  useDispatch: jest.fn(),
}));
jest.mock('../../utils/constant', () => ({
  API_BASE_URL: jest.fn(() => 1),
}));

const mockStore = configureStore([]);

describe('SeasonSwitch Component', () => {
  let store;
  const mockDispatch = jest.fn();

  beforeEach(() => {
    store = mockStore({
      chronos: {
        read_only_mode: false,
        unlock_time: null,
        is_switching_season: false,
      },
    });
    jest.clearAllMocks();
    require('react-redux').useDispatch.mockReturnValue(mockDispatch);
  });

  it('renders both season buttons', () => {
    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    expect(screen.getByText('winter')).toBeInTheDocument();
    expect(screen.getByText('summer')).toBeInTheDocument();
  });

  it('shows active state for current season', () => {
    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    const winterButton = screen.getByText('winter').parentElement;
    const summerButton = screen.getByText('summer').parentElement;

    expect(winterButton.className).toContain('active');
    expect(summerButton.className).not.toContain('active');
  });

  it('handles season switch when clicked', async () => {
    switchSeason.mockResolvedValueOnce({});

    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    const summerButton = screen.getByText('summer').parentElement;
    await act(async () => {
      fireEvent.click(summerButton);
    });

    expect(switchSeason).toHaveBeenCalledWith('summer');
    expect(mockDispatch).toHaveBeenCalled();
  });

  it('shows warning in read-only mode', () => {
    store = mockStore({
      chronos: {
        read_only_mode: true,
        unlock_time: null,
        is_switching_season: false,
      },
    });

    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    const summerButton = screen.getByText('summer').parentElement;
    fireEvent.click(summerButton);

    expect(screen.getByText('Warning!')).toBeInTheDocument();
    expect(screen.getByText('You are in read only mode')).toBeInTheDocument();
  });

  it('shows countdown when unlock_time is set', () => {
    const futureDate = new Date(Date.now() + 2 * 60 * 1000).toISOString();
    store = mockStore({
      chronos: {
        read_only_mode: false,
        unlock_time: futureDate,
        is_switching_season: false,
      },
    });

    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    expect(screen.getByText(/System locked/)).toBeInTheDocument();
  });

  it('disables season switching during animation', async () => {
    render(
      <Provider store={store}>
        <SeasonSwitch season_mode="winter" />
      </Provider>,
    );

    const summerButton = screen.getByText('summer').parentElement;

    await act(async () => {
      fireEvent.click(summerButton);
    });
    expect(switchSeason).toHaveBeenCalledTimes(1);

    await act(async () => {
      fireEvent.click(summerButton);
    });
    expect(switchSeason).toHaveBeenCalledTimes(1);
  });
});
