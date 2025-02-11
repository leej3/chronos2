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
    <div className="data-item">
      <CFormLabel className="data-label">
        <strong>{label}</strong>
      </CFormLabel>
      <span className="data-value">
        {value}
        {unit}
      </span>
    </div>
  </CCol>
);

const Modbus = ({ boiler }) => {
  const [activeTab, setActiveTab] = useState('statsTab');

  const boilerData = {
    stats: {
      items: [
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
      ],
    },
    status: {
      items: [
        {
          label: 'Operating Mode',
          value: boiler?.status?.operating_mode_str || 'N/A',
        },
        {
          label: 'Cascade Mode',
          value: boiler?.status?.cascade_mode_str || 'N/A',
        },
        {
          label: 'Current Setpoint',
          value: formatNumber(boiler?.status?.current_setpoint),
          unit: ' °F',
        },
      ],
    },
    errors: {
      items: [
        {
          label: 'Last Lockout',
          value: boiler?.errors?.last_lockout_str || 'N/A',
        },
        {
          label: 'Last Blockout',
          value: boiler?.errors?.last_blockout_str || 'N/A',
        },
      ],
    },
    info: {
      items: [
        { label: 'Model Name', value: boiler?.info?.model_name || 'N/A' },
        {
          label: 'Firmware Version',
          value: boiler?.info?.firmware_version || 'N/A',
        },
        {
          label: 'Hardware Version',
          value: boiler?.info?.hardware_version || 'N/A',
        },
      ],
    },
  };

  const menuItems = [
    { tab: 'statsTab', label: 'Boiler Stats' },
    { tab: 'statusTab', label: 'Boiler Status' },
    { tab: 'errorTab', label: 'Boiler Error' },
    { tab: 'infoTab', label: 'Boiler Info' },
  ];

  const renderTabContent = (items) => (
    <CRow className="tab-content-container">
      {items.map((item, index) => (
        <TabContent
          key={index}
          label={item.label}
          value={item.value}
          unit={item.unit || ''}
        />
      ))}
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
