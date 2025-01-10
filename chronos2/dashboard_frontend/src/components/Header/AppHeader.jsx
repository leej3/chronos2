import React, { useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  CContainer,
  CHeader,
  CHeaderNav,
  CNavLink,
  CNavItem,
  useColorModes,
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilFactorySlash } from '@coreui/icons';

const AppHeader = () => {
  const headerRef = useRef();
  const { colorMode, setColorMode } = useColorModes(
    'coreui-free-react-admin-template-theme'
  );

  // Get mockDevices state from Redux store
  const mockDevices = useSelector((state) => state.season.mockDevices);

  // Add shadow effect on scroll
  useEffect(() => {
    document.addEventListener('scroll', () => {
      headerRef.current &&
        headerRef.current.classList.toggle(
          'shadow-sm',
          document.documentElement.scrollTop > 0
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
                <CIcon icon={cilFactorySlash} size="lg" className="mr-2" />
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
