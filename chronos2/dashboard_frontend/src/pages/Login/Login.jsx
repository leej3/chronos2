import React, { useState, useEffect } from 'react';

import './Login.css';
import { useNavigate } from 'react-router-dom';

import { cilLockLocked, cilUser } from '@coreui/icons';
import CIcon from '@coreui/icons-react';
import {
  CButton,
  CCard,
  CCardBody,
  CCardGroup,
  CCol,
  CContainer,
  CForm,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CRow,
  CSpinner,
} from '@coreui/react';
import { useDispatch, useSelector } from 'react-redux';



import axiosApi from '../../api/axios';
import { login } from '../../redux/AuthSlice';
const Login = () => {
  const dispatch = useDispatch();
  const { isLoggedIn } = useSelector((state) => state.auth);
  const [isEmail, setEmail] = useState('');
  const [isPassword, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  useEffect(() => {
    if (isLoggedIn) {
      navigate('/');
    }
  }, [isLoggedIn, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!isEmail || !isPassword) {
      setError('Please enter email and password.');
      return;
    }

    setLoading(true);
    try {
      const response = await axiosApi.post('/auth/login', {
        email: isEmail,
        password: isPassword,
      });

      const tokens = response.data.tokens;

      if (tokens && tokens.access && tokens.refresh) {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        dispatch(
          login({ accessToken: tokens.access, refreshToken: tokens.refresh })
        );
        navigate('/');
      } else {
        setError('Error. Please try again');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error. Please try again');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-body-tertiary min-vh-100 d-flex flex-row align-items-center">
      <CContainer>
        <CRow className="justify-content-center">
          <CCol md={8}>
            <CCardGroup>
              <CCard className="p-4">
                <CCardBody>
                  <CForm onSubmit={handleLogin}>
                    <h1>Login</h1>
                    <p className="text-body-secondary">
                      Sign In to your account
                    </p>
                    <CInputGroup className="mb-3">
                      <CInputGroupText>
                        <CIcon icon={cilUser} />
                      </CInputGroupText>
                      <CFormInput
                        type="email"
                        placeholder="Email"
                        autoComplete="email"
                        value={isEmail}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </CInputGroup>
                    <CInputGroup className="mb-4">
                      <CInputGroupText>
                        <CIcon icon={cilLockLocked} />
                      </CInputGroupText>
                      <CFormInput
                        type="password"
                        placeholder="Password"
                        autoComplete="current-password"
                        value={isPassword}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                    </CInputGroup>
                    {error && <div className="text-danger">{error}</div>}
                    <CRow>
                      <CCol xs={6}>
                        <CButton
                          color="primary"
                          className="px-4"
                          type="submit"
                          disabled={loading}
                        >
                          {loading ? 'Logging in...' : 'Login'}
                        </CButton>
                      </CCol>
                    </CRow>
                  </CForm>
                </CCardBody>
              </CCard>
              <CCard
                className="text-white bg-primary py-5"
                style={{ width: '44%' }}
              >
                <CCardBody className="text-center">
                  <div>
                    <h2>Chronos</h2>
                    <p>
                      Welcome to Chronos! Please log in to manage your hotel
                      efficiently and seamlessly. Enjoy advanced features to
                      control and monitor your heating and cooling systems
                      effortlessly.
                    </p>
                  </div>
                </CCardBody>
              </CCard>
            </CCardGroup>
          </CCol>
        </CRow>
      </CContainer>
      {loading && (
        <div className="spinner-overlay">
          <CSpinner color="primary"  />
        </div>
      )}
    </div>
  );
};

export default Login;
