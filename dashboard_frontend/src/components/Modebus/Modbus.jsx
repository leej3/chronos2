import React from 'react';

import { CFormLabel, CCol, CRow, CCard, CCardBody } from '@coreui/react';

import { formatNumber } from '../../utils/tranform';
import BoilerSetpoint from '../BoilerSetpoint/BoilerSetpoint';

import './Modbus.css';

const TabContent = ({ label, value, unit = '' }) => (
  <CCol sm="12">
    <div className="temp-item">
      <CFormLabel>
        <span className="temp-label">{label}</span>
      </CFormLabel>
      <span className="temp-value">
        {value}
        {unit}
      </span>
    </div>
  </CCol>
);

const Modbus = ({ boiler }) => {
  const statsItems = [
    {
      label: 'System Supply Temp',
      value: formatNumber(boiler?.stats?.system_supply_temp),
      unit: ' °F',
    },
    {
      label: 'Outlet Temp',
      value: formatNumber(boiler?.stats?.outlet_temp),
      unit: ' °F',
    },
    {
      label: 'Inlet Temp',
      value: formatNumber(boiler?.stats?.inlet_temp),
      unit: ' °F',
    },
    {
      label: 'Cascade Power',
      value: formatNumber(boiler?.stats?.cascade_current_power),
      unit: ' %',
    },
    {
      label: 'Lead Firing Rate',
      value: formatNumber(boiler?.stats?.lead_firing_rate),
      unit: ' %',
    },
  ];

  return (
    <CRow>
      <CCol>
        <CCard className="modbus-card">
          <CCardBody>
            <h2 className="chronous-title m-0">Modbus</h2>
            <div className="content-container-mobile">
              <CRow className="tab-content-container">
                {statsItems.map((item, index) => (
                  <TabContent
                    key={index}
                    label={item.label}
                    value={item.value}
                    unit={item.unit}
                  />
                ))}
              </CRow>
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default Modbus;