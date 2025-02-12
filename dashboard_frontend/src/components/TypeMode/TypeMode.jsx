import React, { useState, useEffect } from 'react';

import { CCardBody, CRow, CCol, CBadge, CCard } from '@coreui/react';
import { FaThermometerHalf } from 'react-icons/fa';
import { useSelector } from 'react-redux';
import { getFormattedChicagoTime } from '../../utils/dateUtils';
import './TypeMode.css';

const TypeMode = ({ homedata }) => {
  const season = useSelector((state) => state.chronos.season);

  const outdoorTemp = homedata?.results?.outside_temp || 'N/A';
  const avgTemp = homedata?.efficiency?.average_temperature_difference || 'N/A';
  const [currentTime, setCurrentTime] = useState('');

  const [isSmallScreen, setIsSmallScreen] = useState(false);

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(getFormattedChicagoTime());
    };

    updateTime();
    const timer = setInterval(updateTime, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setIsSmallScreen(window.innerWidth <= 768);
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <CRow>
      <CCol>
        <CCard>
          <CCardBody>
            <div className="d-flex flex-column align-items-center">
              <h2 className="chronous-title text-center mb-2">
                {season === 'Winter' ? 'Winter Mode' : 'Summer Mode'}
              </h2>
              <div className="current-time">{currentTime}</div>
            </div>

            <CCardBody className="mt-3">
              <CRow className="justify-content-center g-3">
                <CCol xs={6} className="text-center">
                  <div className="temp-circle">
                    <FaThermometerHalf
                      size={isSmallScreen ? 20 : 35}
                      color="#FFB600"
                    />
                    <div className="temp-value">{outdoorTemp}°F</div>
                  </div>
                  <div className="temp-label mt-2">Outdoor Temp</div>
                </CCol>

                <CCol xs={6} className="text-center">
                  <div className="temp-circle">
                    <FaThermometerHalf
                      size={isSmallScreen ? 20 : 35}
                      color="#FFB600"
                    />
                    <div className="temp-value">{avgTemp}°F</div>
                  </div>
                  <div className="temp-label mt-2">Avg Temp (96 hrs)</div>
                </CCol>
              </CRow>
            </CCardBody>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default TypeMode;
