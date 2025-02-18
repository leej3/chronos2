import React, { useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom';

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
