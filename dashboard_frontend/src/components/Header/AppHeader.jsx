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
import SeasonSwitch from '../SeasonSwitch/SeasonSwitch';

const AppHeader = () => {
  const headerRef = useRef();
  const [currentTime, setCurrentTime] = useState('');
  // const { colorMode, setColorMode } = useColorModes(
  //   'coreui-free-react-admin-template-theme'
  // );

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
      <CContainer fluid className="px-2 px-sm-3">
        <div className="d-flex flex-wrap align-items-center justify-content-between w-100 gap-1 gap-sm-2">
          <CHeaderBrand className="me-0">
            <div className="d-flex flex-column">
              <NavLink
                to="/"
                className="text-decoration-none text-white mb-0"
                style={{ fontSize: '1.1rem' }}
              >
                Chronus Dashboard
              </NavLink>
              <div
                className="d-flex align-items-center mt-0 mt-sm-1"
                style={{ fontSize: '0.8rem' }}
              >
                <span className="text-white-50 me-1 me-sm-2">SYSTEM - </span>
                <span
                  className={`${systemStatus === 'ONLINE' ? 'text-success' : 'text-danger'
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
            </div>
          </CHeaderBrand>

          <CHeaderNav className="d-flex flex-wrap align-items-center gap-2 gap-sm-3">
            <CNavItem>
              <CNavLink href="#" className="d-flex align-items-center p-0">
                <CIcon
                  icon={cilClock}
                  className="me-1 me-sm-2"
                  style={{ width: '0.9rem' }}
                />
                <span className="text-nowrap" style={{ fontSize: '0.9rem' }}>
                  {currentTime}
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
