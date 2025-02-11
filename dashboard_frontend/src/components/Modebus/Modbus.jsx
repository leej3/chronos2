import React from 'react';
import { CFormLabel, CCol, CRow, CCard, CCardBody } from '@coreui/react';
import React, { useState } from 'react';
import {
  CFormLabel,
  CCol,
  CRow,
  CNav,
  CNavItem,
  CNavLink,
  CTabContent,
  CTabPane,
  CDropdown,
  CDropdownToggle,
  CDropdownMenu,
  CDropdownItem,
  CCard,
  CCardBody,
} from '@coreui/react';
import { formatNumber } from '../../utils/tranform';
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
import BoilerSetpoint from '../BoilerSetpoint/BoilerSetpoint';

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
            <strong>Cascade Power:</strong>{' '}
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

  const renderErrorTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Last Lockout:</strong> <span>{last_lockout_str}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Last Blockout:</strong> <span>{last_blockout_str}</span>
          </CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  const renderInfoTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Model Name:</strong> <span>{model_name}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Firmware Version:</strong> <span>{firmware_version}</span>
          </CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label">
            <strong>Hardware Version:</strong> <span>{hardware_version}</span>
          </CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  return (
    <CRow>
      <CCol>
        <CCard className="modbus-card">
          <CCardBody className="p-0">
            <div className="modbus">
              <CDropdown className="d-md-none mobile-dropdown mb-2">
                <CDropdownToggle caret className="mb-0">
                  {menuItems.find((item) => item.tab === activeTab)?.label ||
                    'Menu'}
                </CDropdownToggle>
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

              <CNav
                variant="tabs"
                role="tablist"
                className="d-none d-md-flex nav-grid"
              >
                {menuItems.map((item) => (
                  <CNavItem key={item.tab} className="nav-grid-item">
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
                  {renderTabContent(boilerData.stats.items)}
                </CTabPane>
                <CTabPane visible={activeTab === 'statusTab'}>
                  {renderTabContent(boilerData.status.items)}
                </CTabPane>
                <CTabPane visible={activeTab === 'errorTab'}>
                  {renderTabContent(boilerData.errors.items)}
                </CTabPane>
                <CTabPane visible={activeTab === 'infoTab'}>
                  {renderTabContent(boilerData.info.items)}
                </CTabPane>
              </CTabContent>
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default Modbus;
