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

  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('Outdoor Temp');

  const menuItems = [
    { value: 'Outdoor Temp', label: 'Outdoor Temp' },
    { value: 'Avg Temp', label: 'Avg Temp (96 hrs)' },
  ];

  useEffect(() => {
    const handleResize = () => {
      setIsSmallScreen(window.innerWidth <= 768);
    };

    handleResize();
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
    <CRow>
      <CCol>
        <CCard className="bgr p-0">
          <CCardBody>
            <div className="d-flex flex-column align-items-center">
              <h2 className="sensor-title text-center mb-2">
                {season === 'Winter' ? 'Winter Mode' : 'Summer Mode'}
              </h2>
              <CBadge color={systemStatus === 'ONLINE' ? 'success' : 'danger'}>
                {systemStatus}
              </CBadge>
            </div>

            <CCardBody className="mt-3">
              <CRow className="justify-content-center g-3">
                {isSmallScreen ? (
                  <CCol xs={12}>
                    <CDropdown className="d-md-none mb-3">
                      <CDropdownToggle color="secondary" className="w-100">
                        Select Metric
                      </CDropdownToggle>
                      <CDropdownMenu className="w-100">
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

                    <div className="text-center">{getSelectedContent()}</div>
                  </CCol>
                ) : (
                  <>
                    <CCol xs={12} sm={6} className="text-center">
                      <div className="temp-circle">
                        <FaThermometerHalf size={35} color="#FFB600" />
                        <div className="temp-value">{outdoorTemp}°F</div>
                      </div>
                      <div className="temp-label mt-2">Outdoor Temp</div>
                    </CCol>

                    <CCol xs={12} sm={6} className="text-center">
                      <div className="temp-circle">
                        <FaThermometerHalf size={35} color="#FFB600" />
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
  );
};

export default TypeMode;
