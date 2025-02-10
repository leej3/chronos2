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

  // Add time update effect
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(getFormattedChicagoTime());
    };

    updateTime(); // Initial update
    const timer = setInterval(updateTime, 1000); // Update every second

    return () => clearInterval(timer); // Cleanup on unmount
  }, []);

  return (
    <CHeader position="sticky" className="p-2" ref={headerRef}>
      <CContainer fluid>
        <CHeaderNav className="d-none d-md-flex">
          <CNavItem>
            <CNavLink to="/" as={NavLink}>
              Chronus Dashboard
            </CNavLink>
          </CNavItem>
        </CHeaderNav>
        <CHeaderNav className="ms-auto">
          <CNavItem>
            <CNavLink
              href="#"
              className="d-flex align-items-center justify-content-center m-1"
              style={{
                minWidth: '250px',
                borderRadius: '8px',
                padding: '8px 16px',
                color: '#fff',
                textDecoration: 'none',
              }}
            >
              <CIcon
                icon={cilClock}
                style={{
                  width: '20px',
                  height: '20px',
                  marginRight: '8px',
                  color: '#666',
                }}
              />
              <span
                style={{
                  fontSize: '0.95rem',
                  fontWeight: '500',
                  letterSpacing: '0.3px',
                }}
              >
                {currentTime}
              </span>
            </CNavLink>
          </CNavItem>
          {mockDevices && (
            <CNavItem>
              <CNavLink
                href="#"
                className="d-flex align-items-center text-danger m-1"
                style={{
                  background: 'rgba(255, 0, 0, 0.05)',
                  borderRadius: '8px',
                  padding: '8px 16px',
                }}
              >
                <CIcon
                  icon={cilFactorySlash}
                  style={{
                    width: '20px',
                    height: '20px',
                    marginRight: '8px',
                  }}
                />
                <span className="font-weight-bold">Mock Devices Mode</span>
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
