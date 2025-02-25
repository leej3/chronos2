import React from 'react';
import { CCard, CCardBody, CCardHeader, CRow, CCol } from '@coreui/react';
import './SwitchTimeDisplay.css';
import { DEVICES } from '../../utils/constant';
import { formatDate } from '../../utils/tranform';
const SwitchTimeDisplay = ({ devices }) => {
  const getDeviceById = (id) => {
    return devices?.find((device) => device.id === id);
  };

  const lastSwitch = [
    { chiller1: getDeviceById(DEVICES.chiller1)?.switched_timestamp },
    { chiller2: getDeviceById(DEVICES.chiller2)?.switched_timestamp },
    { chiller3: getDeviceById(DEVICES.chiller3)?.switched_timestamp },
    { chiller4: getDeviceById(DEVICES.chiller4)?.switched_timestamp },
  ];

  const getChillerTime = (chillerNumber) => {
    const chillerData = lastSwitch?.find(
      (item) => Object.keys(item)[0] === `chiller${chillerNumber}`,
    );
    return chillerData ? Object.values(chillerData)[0] : null;
  };

  return (
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
                <span>{formatDate(getChillerTime(number))}</span>
              </div>
            ))}
          </div>
        </CCardBody>
      </CCard>
    </CCol>
  );
};

export default SwitchTimeDisplay;
