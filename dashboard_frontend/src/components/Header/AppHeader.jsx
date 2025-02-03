import React, { useEffect, useState, useRef } from 'react';
import { NavLink } from 'react-router-dom';
import { cilFactorySlash, cilClock } from '@coreui/icons';
import CIcon from '@coreui/icons-react';
import {
  CContainer,
  CHeader,
  CHeaderNav,
  CNavLink,
  CNavItem,
} from '@coreui/react';
import { useSelector } from 'react-redux';
import { getFormattedTime } from '../../utils/timezone';

const AppHeader = () => {
  const [currentTime, setCurrentTime] = useState('');
  const headerRef = useRef();
  const mockDevices = useSelector((state) => state.season.mockDevices);

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(getFormattedTime());
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    document.addEventListener('scroll', () => {
      headerRef.current &&
        headerRef.current.classList.toggle(
          'shadow-sm',
          document.documentElement.scrollTop > 0,
        );
    });
  }, []);

  return (
    <CHeader position="sticky" className="p-2" ref={headerRef}>
      <CContainer fluid>
        <CHeaderNav className="d-none d-md-flex">
          <CNavItem>
            <CNavLink
              to="/"
              as={NavLink}
              className="text-primary font-weight-bold"
            >
              Chronus Dashboard
            </CNavLink>
          </CNavItem>
        </CHeaderNav>
        <CHeaderNav className="ms-auto">
          <CNavItem>
            <CNavLink
              href="#"
              className="d-flex align-items-center font-weight-bold m-1"
            >
              <CIcon icon={cilClock} className="mr-2" />
              <span className="font-weight-bold m-2">{currentTime}</span>
            </CNavLink>
          </CNavItem>
          {mockDevices && (
            <CNavItem>
              <CNavLink
                href="#"
                className="d-flex align-items-center text-danger m-1"
              >
                <CIcon icon={cilFactorySlash} className="mr-2" />
                <span className="font-weight-bold m-2">Mock Devices Mode</span>
              </CNavLink>
            </CNavItem>
          )}
        </CHeaderNav>
      </CContainer>
    </CHeader>
  );
};

export default AppHeader;
