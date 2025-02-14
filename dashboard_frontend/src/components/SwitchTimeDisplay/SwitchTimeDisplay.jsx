import React from 'react';
import { CCard, CCardBody, CCardHeader, CRow, CCol } from '@coreui/react';
import './SwitchTimeDisplay.css';

const SwitchTimeDisplay = ({ data }) => {
  // Thêm dữ liệu mẫu
  const mockData = {
    lastSwitch: [
      { chiller1: 3600 },
      { chiller2: 7200 },
      { chiller3: 10800 },
      { chiller4: 14400 },
    ],
  };

  const displayData = data || mockData;

  const formatTime = (seconds) => {
    if (!seconds && seconds !== 0) return 'N/A';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(
      2,
      '0',
    )}:${String(remainingSeconds).padStart(2, '0')}`;
  };

  const getChillerTime = (chillerNumber) => {
    const chillerData = displayData?.lastSwitch?.find(
      (item) => Object.keys(item)[0] === `chiller${chillerNumber}`,
    );
    return chillerData ? Object.values(chillerData)[0] : null;
  };

  return (
    <CRow>
      <CCol>
        <CCard>
          <CCardBody>
            <h2 className="chronous-title">Last Switch Time</h2>
            <div className="switch-time-grid">
              {[1, 2, 3, 4].map((number) => (
                <div
                  key={number}
                  className="d-flex justify-content-between align-items-center mb-2"
                >
                  <strong>Chiller {number}:</strong>
                  <span>{formatTime(getChillerTime(number))}</span>
                </div>
              ))}
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default SwitchTimeDisplay;
