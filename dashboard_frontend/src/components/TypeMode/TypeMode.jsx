import React, { useState, useEffect } from 'react';

import {
  CCardBody,
  CRow,
  CCol,
  CBadge,
  CDropdownItem,
  CDropdownMenu,
  CDropdown,
  CDropdownToggle,
  CContainer,
  CCard,
} from '@coreui/react';
import { FaThermometerHalf } from 'react-icons/fa';
import { useSelector } from 'react-redux';
import './TypeMode.css';

const TypeMode = ({ homedata }) => {
  const season = useSelector((state) => state.chronos.season);

  const outdoorTemp = homedata?.results?.outside_temp || 'N/A';
  const avgTemp = homedata?.efficiency?.average_temperature_difference || 'N/A';
  const systemStatus = homedata?.status ? 'ONLINE' : 'OFFLINE';

  // State for screen size and selected dropdown item
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('Outdoor Temp');

  const menuItems = [
    { value: 'Outdoor Temp', label: 'Outdoor Temp' },
    { value: 'Avg Temp', label: 'Avg Temp (96 hrs)' },
  ];

  // Handle screen resizing
  useEffect(() => {
    const handleResize = () => {
      setIsSmallScreen(window.innerWidth <= 768);
    };

    handleResize(); // Initial check
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getSelectedContent = () => {
    if (selectedOption === 'Outdoor Temp') {
      return (
        <>
          <div className="temp-circle">
            <FaThermometerHalf size={50} color="#FFB600" />
            <div className="temp-value">{outdoorTemp}°F</div>
          </div>
          <div className="temp-label mt-2">Outdoor Temp</div>
        </>
      );
    } else if (selectedOption === 'Avg Temp') {
      return (
        <>
          <div className="temp-circle">
            <FaThermometerHalf size={50} color="#FFB600" />
            <div className="temp-value">{avgTemp}°F</div>
          </div>
          <div className="temp-label mt-2">Avg Temp (96 hrs)</div>
        </>
      );
    }
    return null;
  };

  return (
    <CContainer fluid>
      <CRow>
        <CCol>
          <CCard className="mb-4 bgr p-0">
            <CCardBody>
              <h2 className="sensor-title text-center">
                {season === 'Winter' ? 'Winter Mode' : 'Summer Mode'}
              </h2>
              <CBadge color={systemStatus === 'ONLINE' ? 'success' : 'danger'}>
                {systemStatus}
              </CBadge>

              <CCardBody className="mt-4">
                <CRow className="d-flex justify-content-center">
                  {/* For small screens, show dropdown */}
                  {isSmallScreen ? (
                    <CCol xs={12}>
                      <CDropdown className="d-md-none">
                        <CDropdownToggle color="secondary">
                          Select Metric
                        </CDropdownToggle>
                        <CDropdownMenu>
                          {menuItems.map((item) => (
                            <CDropdownItem
                              key={item.value}
                              onClick={() => setSelectedOption(item.value)}
                            >
                              {item.label}
                            </CDropdownItem>
                          ))}
                        </CDropdownMenu>
                      </CDropdown>

                      <CCol xs={12} className="mt-2">
                        {getSelectedContent()}
                      </CCol>
                    </CCol>
                  ) : (
                    <>
                      <CCol xs={12} md={6}>
                        <div className="temp-circle">
                          <FaThermometerHalf size={50} color="#FFB600" />
                          <div className="temp-value">{outdoorTemp}°F</div>
                        </div>
                        <div className="temp-label mt-2">Outdoor Temp</div>
                      </CCol>

                      <CCol xs={12} md={6}>
                        <div className="temp-circle">
                          <FaThermometerHalf size={50} color="#FFB600" />
                          <div className="temp-value">{avgTemp}°F</div>
                        </div>
                        <div className="temp-label mt-2">Avg Temp (96 hrs)</div>
                      </CCol>
                    </>
                  )}
                </CRow>
              </CCardBody>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  );
};

export default TypeMode;
