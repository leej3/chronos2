import React, { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { getFormattedChicagoTime } from '../../utils/dateUtils';

import { cilFactorySlash, cilLockLocked } from '@coreui/icons';
import CIcon from '@coreui/icons-react';
import {
  CContainer,
  CHeader,
  CHeaderNav,
  CNavLink,
  CNavItem,
  CHeaderBrand,
} from '@coreui/react';
import { useSelector } from 'react-redux';

const AppHeader = () => {
  const headerRef = useRef();
  const [currentTime, setCurrentTime] = useState('');
  // const { colorMode, setColorMode } = useColorModes(
  //   'coreui-free-react-admin-template-theme'
  // );

  // Get mockDevices state from Redux store
  const mockDevices = useSelector((state) => state.chronos.mock_devices);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);

  // Add shadow effect on scroll
  useEffect(() => {
    document.addEventListener('scroll', () => {
      headerRef.current &&
        headerRef.current.classList.toggle(
          'shadow-sm',
          document.documentElement.scrollTop > 0,
        );
    });
  }, []);

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(getFormattedChicagoTime());
    };

    updateTime();
    const timer = setInterval(updateTime, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <CHeader position="sticky" ref={headerRef}>
      <CContainer fluid className="px-4">
        <CHeaderBrand className="d-flex align-items-center">
          <NavLink
            to="/"
            className="text-decoration-none text-white d-flex align-items-center "
            style={{ fontSize: { xs: '1rem', md: '1.25rem' } }}
          >
            Chronus Dashboard
            <div
              className={`season-icon ${season === 'Summer' ? 'active' : ''}`}
            >
              {season === 'Summer' && <span className="season-emoji">☀️</span>}
              {season === 'Winter' && <span className="season-emoji">❄️</span>}
            </div>
          </NavLink>
        </CHeaderBrand>

        <CHeaderNav className="d-flex flex-column flex-md-row gap-2 pl-md-0">
          <CNavItem className="d-flex align-items-center w-100">
            <CNavLink
              href="#"
              className="d-flex align-items-center w-100 px-0"
              style={{
                borderRadius: '8px',
                minWidth: { md: '250px' },
              }}
            >
              <CIcon
                icon={cilClock}
                className="me-2"
                style={{
                  width: '1.25rem',
                  height: '1.25rem',
                }}
              />
              <span
                className="fw-medium "
                style={{
                  letterSpacing: '0.3px',
                  whiteSpace: 'nowrap',
                }}
              >
                {currentTime}
              </span>
            </CNavLink>
          </CNavItem>

          {mockDevices && (
            <CNavItem className="d-flex align-items-center w-100">
              <CNavLink
                href="#"
                className="d-flex align-items-center text-danger  w-100 px-0"
                style={{
                  background: 'rgba(255, 0, 0, 0.05)',
                  borderRadius: '8px',
                }}
              >
                <CIcon
                  icon={cilFactorySlash}
                  className="me-2 p-0"
                  style={{
                    width: '1.25rem',
                    height: '1.25rem',
                  }}
                />
                <span className="fw-medium" style={{ whiteSpace: 'nowrap' }}>
                  Mock Devices Mode
                </span>
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
      </CContainer>
    </CHeader>
  );
};

export default AppHeader;
