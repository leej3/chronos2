import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import '@testing-library/jest-dom';
import MockAdapter from 'axios-mock-adapter';
import { Provider } from 'react-redux';

import axiosApi from '../../api/axios';
import Login from '../../pages/Login/Login';

import { configureStore } from '@reduxjs/toolkit';

import { BrowserRouter as Router } from 'react-router-dom';
import React from 'react';

jest.mock('../../utils/constant', () => ({
  API_BASE_URL: jest.fn(() => 1),
}));
jest.mock('../../pages/Login/Login.css', () => {});

beforeEach(() => {
  localStorage.clear();
});

const store = configureStore({
  reducer: {
    auth: (state = { isLoggedIn: false }) => state,
  },
});

describe('Login Component', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(axiosApi);
  });

  afterEach(() => {
    mock.reset();
  });
  it('should display an error message when please enter email and password', async () => {
    render(
      <Provider store={store}>
        <Router>
          <Login />
        </Router>
      </Provider>,
    );

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: '' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: '' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      const errorMessage = screen.getByText('Please enter email and password.');
      expect(errorMessage).toBeInTheDocument();
    });
  });
  it('should display an error message when login fails', async () => {
    mock.onPost('/auth/login').reply(400, { message: 'Invalid credentials' });

    render(
      <Provider store={store}>
        <Router>
          <Login />
        </Router>
      </Provider>,
    );

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@gmail.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'wrongpassword' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      const errorMessage = screen.getByText('Invalid credentials');
      expect(errorMessage).toBeInTheDocument();
    });
  });

  it('should login successfully and redirect', async () => {
    mock.onPost('/auth/login').reply(200, {
      tokens: { access: 'fake-access-token', refresh: 'fake-refresh-token' },
    });

    render(
      <Provider store={store}>
        <Router>
          <Login />
        </Router>
      </Provider>,
    );

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@gmail.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('fake-access-token');
      expect(localStorage.getItem('refresh_token')).toBe('fake-refresh-token');
    });
  });
});
