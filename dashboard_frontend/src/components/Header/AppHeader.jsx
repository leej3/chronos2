import React, { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';

import { cilClock, cilFactorySlash, cilLockLocked } from '@coreui/icons';
import CIcon from '@coreui/icons-react';
import {
  CContainer,
  CHeader,
  CHeaderNav,
  CNavLink,
  CNavItem,
  CHeaderBrand,
  CRow,
  CCol,
} from '@coreui/react';
import { useSelector } from 'react-redux';
import { formatDate } from '../../utils/tranform';
import './AppHeader.css';

const AppHeader = () => {
  const headerRef = useRef();
  const { systemStatus, season, lastUpdated } = useSelector(
    (state) => state.chronos,
  );
  const data = useSelector((state) => state.chronos.data);

  const outdoorTemp = data?.results?.outside_temp || 'N/A';
  const avgTemp = data?.efficiency?.average_temperature_difference || 'N/A';
  // Get mockDevices state from Redux store
  const mockDevices = useSelector((state) => state.chronos.mock_devices);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);

  useEffect(() => {
    document.addEventListener('scroll', () => {
      headerRef.current?.classList.toggle(
        'shadow-sm',
        document.documentElement.scrollTop > 0,
      );
    });
  }, []);
  const getSeasonIcon = () => {
    if (season === 1) {
      return '/images/Icons/WinterSummer/SOn.png';
    }
    return '/images/Icons/WinterSummer/WOn.png';
  };

  return (
    <CHeader position="sticky" ref={headerRef}>
      <CContainer fluid className="p-2 px-sm-3 header-container">
        <div className="d-flex flex-wrap align-items-center justify-content-between w-100 gap-1 gap-sm-2 d-none d-lg-flex">
          <CHeaderBrand className="me-0">
            <div className="d-flex flex-column">
              <NavLink
                to="/"
                className="text-decoration-none text-white mb-0 "
                style={{ fontSize: '1.1rem' }}
              >
                Chronus Dashboard
              </NavLink>
              <div
                className="d-flex align-items-center mt-0 mt-sm-1"
                style={{ fontSize: '0.8rem' }}
              >
                <span className="text-white-50 me-1 me-sm-2 text-info">
                  SYSTEM
                </span>
                <span
                  className={`${
                    systemStatus === 'ONLINE' ? 'text-success' : 'text-danger'
                  } d-flex align-items-center`}
                >
                  <span
                    className="d-inline-block rounded-circle me-1"
                    style={{
                      width: '6px',
                      height: '6px',
                      backgroundColor:
                        systemStatus === 'ONLINE' ? '#198754' : '#dc3545',
                    }}
                  />
                  {systemStatus}
                </span>
              </div>
              {lastUpdated && (
                <div className="d-flex align-items-center text-info">
                  <span
                    className=" me-1 me-sm-2 "
                    style={{ fontSize: '0.8rem' }}
                  >
                    Last sync:
                  </span>
                  <span
                    className=" me-1 me-sm-2 font-weight-bold"
                    style={{ fontSize: '0.8rem' }}
                  >
                    {formatDate(lastUpdated, 'HH:mm:ss')}
                  </span>
                </div>
              )}
            </div>
          </CHeaderBrand>

          <CHeaderNav className="d-flex flex-wrap align-items-center ">
            {mockDevices && (
              <CNavItem>
                <CNavLink
                  href="#"
                  className="d-flex align-items-center text-danger p-0"
                >
                  <CIcon
                    icon={cilFactorySlash}
                    className="me-1 me-sm-2"
                    style={{ width: '0.9rem' }}
                  />
                  <span className="text-nowrap" style={{ fontSize: '0.9rem' }}>
                    Mock Devices Mode
                  </span>
                  <img
                    className="me-1 me-sm-2 ms-2"
                    src={getSeasonIcon()}
                    alt={`${season === 1 ? 'Summer' : 'Winter'} mode`}
                  />
                </CNavLink>
              </CNavItem>
            )}
            {readOnlyMode && (
              <CNavItem>
                <CNavLink
                  href="#"
                  className="d-flex align-items-center text-warning m-1"
                >
                  <CIcon icon={cilLockLocked} className="mr-2" />
                  <span className="font-weight-bold m-2">Read Only Mode</span>
                </CNavLink>
              </CNavItem>
            )}
          </CHeaderNav>
        </div>
        <CRow className="g-0 w-100  d-lg-none">
          <CCol xs={6} md={6} className="mb-2 mb-md-0">
            <div className="d-flex align-items-center mb-1 ">
              <img
                src={getSeasonIcon()}
                alt={`${season === 1 ? 'Summer' : 'Winter'} mode`}
              />
              <div
                className={`ms-1 d-flex align-items-center ${
                  systemStatus === 'ONLINE' ? 'text-success' : 'text-danger'
                } status-indicator`}
              >
                <span
                  className={`status-dot ${
                    systemStatus === 'ONLINE'
                      ? 'status-dot-online'
                      : 'status-dot-offline'
                  }`}
                />
                <span>{systemStatus}</span>
              </div>
            </div>
            {lastUpdated && (
              <div className="d-flex align-items-center text-info">
                <span className=" me-1 me-sm-2 " style={{ fontSize: '0.9rem' }}>
                  Last sync:
                </span>
                <span className=" me-1 me-sm-2 font-weight-bold">
                  {formatDate(lastUpdated, 'HH:mm:ss')}
                </span>
              </div>
            )}
          </CCol>

          <CCol xs={6} md={6}>
            <div className="d-flex flex-column flex-md-row justify-content-md-end h-100">
              {mockDevices && (
                <div className="mock-devices-alert me-md-3 text-danger m-0">
                  <CIcon
                    icon={cilFactorySlash}
                    className="me-1 me-sm-2"
                    style={{ width: '0.9rem' }}
                  />
                  <span className="text-nowrap" style={{ fontSize: '0.9rem' }}>
                    Mock Devices Mode
                  </span>
                </div>
              )}
              {readOnlyMode && (
                <div className="mock-devices-alert me-md-3 text-warning m-0">
                  <CIcon
                    icon={cilLockLocked}
                    className="me-1 me-sm-2"
                    style={{ width: '0.9rem' }}
                  />
                  <span className="text-nowrap" style={{ fontSize: '0.9rem' }}>
                    Read Only Mode
                  </span>
                </div>
              )}

              <div className="d-flex flex-column flex-md-row">
                <div className="temperature-container d-flex align-items-center">
                  <span className="temperature-label">Avg (96hrs):</span>
                  <span className="temperature-value">{avgTemp}°F</span>
                </div>
                <div className="d-flex align-items-center">
                  <span className="temperature-label">Outdoor:</span>
                  <span className="temperature-value">{outdoorTemp}°F</span>
                </div>
              </div>
            </div>
          </CCol>
        </CRow>
      </CContainer>
    </CHeader>
  );
};

export default AppHeader;
