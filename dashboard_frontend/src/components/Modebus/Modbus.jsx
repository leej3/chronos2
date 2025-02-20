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
  const [activeTab, setActiveTab] = useState('statsTab');

  const system_supply_temp =
    formatNumber(boiler?.stats?.system_supply_temp) ?? 'N/A';
  const outlet_temp = formatNumber(boiler?.stats?.outlet_temp) ?? 'N/A';
  const inlet_temp = formatNumber(boiler?.stats?.inlet_temp) ?? 'N/A';
  const cascade_current_power =
    formatNumber(boiler?.stats?.cascade_current_power) ?? 'N/A';
  const lead_firing_rate =
    formatNumber(boiler?.stats?.lead_firing_rate) ?? 'N/A';

  const operating_mode = boiler?.status?.operating_mode_str ?? 'N/A';
  const cascade_mode = boiler?.status?.cascade_mode_str ?? 'N/A';
  const current_setpoint =
    formatNumber(boiler?.status?.current_setpoint) ?? 'N/A';

  const menuItems = [
    { tab: 'statsTab', label: 'Boiler Stats' },
    { tab: 'statusTab', label: 'Boiler Status' },
  ];

  const renderStatsTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>System Supply Temp:</strong>{' '}
            <span>{`${system_supply_temp} °F`}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Outlet Temp:</strong> <span>{`${outlet_temp} °F`}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Inlet Temp:</strong> <span>{`${inlet_temp} °F`}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Cascade Current Power:</strong>{' '}
            <span>{`${cascade_current_power} %`}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Lead Firing Rate:</strong>{' '}
            <span>{`${lead_firing_rate} %`}</span>
          </CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  const renderStatusTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Operating Mode:</strong> <span>{operating_mode}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Cascade Mode:</strong> <span>{cascade_mode}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Current Setpoint:</strong>{' '}
            <span>{`${current_setpoint} °F`}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12" className="mt-4">
        <BoilerSetpoint currentSetpoint={current_setpoint} />
      </CCol>
    </CRow>
  );

  return (
    <div className="modbus">
      <CDropdown className="d-md-none">
        <CDropdownToggle color="primary">Select Tab</CDropdownToggle>
        <CDropdownMenu>
          {menuItems.map((item) => (
            <CDropdownItem
              key={item.tab}
              onClick={() => setActiveTab(item.tab)}
              active={activeTab === item.tab}
            >
              {item.label}
            </CDropdownItem>
          ))}
        </CDropdownMenu>
      </CDropdown>

      <CNav variant="tabs" className="d-none d-md-flex">
        {menuItems.map((item) => (
          <CNavItem key={item.tab}>
            <CNavLink
              active={activeTab === item.tab}
              onClick={() => setActiveTab(item.tab)}
            >
              {item.label}
            </CNavLink>
          </CNavItem>
        ))}
      </CNav>

      <CTabContent>
        <CTabPane visible={activeTab === 'statsTab'}>
          {renderStatsTab()}
        </CTabPane>
        <CTabPane visible={activeTab === 'statusTab'}>
          {renderStatusTab()}
        </CTabPane>
      </CTabContent>
    </div>
  );
};

export default Modbus;
