import React, { useState } from "react";
import { CFormLabel, CCol, CRow, CNav, CNavItem, CNavLink, CTabContent, CTabPane } from '@coreui/react';
import './Modbus.css'; 
import { formatNumber } from "../../utils/tranform";

const Modbus = ({ boiler }) => {
  const [activeTab, setActiveTab] = useState('statsTab'); 

  const system_supply_temp = formatNumber(boiler?.stats?.system_supply_temp) ?? "N/A";
  const outlet_temp = formatNumber(boiler?.stats?.outlet_temp) ?? "N/A";
  const inlet_temp = formatNumber(boiler?.stats?.inlet_temp) ?? "N/A";
  const cascade_current_power = formatNumber(boiler?.stats?.cascade_current_power) ?? "N/A";
  const lead_firing_rate = formatNumber(boiler?.stats?.lead_firing_rate) ?? "N/A";
  
  const operating_mode = boiler?.status?.operating_mode_str ?? "N/A";
  const cascade_mode = boiler?.status?.cascade_mode_str ?? "N/A";
  const current_setpoint = formatNumber(boiler?.status?.current_setpoint) ?? "N/A";
  
  const last_lockout_str = boiler?.errors?.last_lockout_str ?? "N/A";
  const last_blockout_str = boiler?.errors?.last_blockout_str ?? "N/A";

  const model_name = boiler?.info?.model_name ?? "N/A";
  const firmware_version = boiler?.info?.firmware_version ?? "N/A";
  const hardware_version = boiler?.info?.hardware_version ?? "N/A";

  const renderStatsTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>System Supply Temp:</strong> <span>{`${system_supply_temp} °F`}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Outlet Temp:</strong> <span>{`${outlet_temp} °F`}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Inlet Temp:</strong> <span>{`${inlet_temp} °F`}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Cascade Power:</strong> <span>{`${cascade_current_power} %`}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Lead Firing Rate:</strong> <span>{`${lead_firing_rate} %`}</span></CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  const renderStatusTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Operating Mode:</strong> <span>{operating_mode}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Cascade Mode:</strong> <span>{cascade_mode}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Current Setpoint:</strong> <span>{`${current_setpoint} °F`}</span></CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  const renderErrorTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Last Lockout:</strong> <span>{last_lockout_str}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Last Blockout:</strong> <span>{last_blockout_str}</span></CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  const renderInfoTab = () => (
    <CRow>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Model Name:</strong> <span>{model_name}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Firmware Version:</strong> <span>{firmware_version}</span></CFormLabel>
        </div>
      </CCol>
      <CCol sm="12">
        <div className="season-group">
          <CFormLabel className="form-label"><strong>Hardware Version:</strong> <span>{hardware_version}</span></CFormLabel>
        </div>
      </CCol>
    </CRow>
  );

  return (
    <div className="modbus">

      <CNav variant="tabs" role="tablist" className="d-flex flex-wrap">
        <CNavItem className="col-3">
          <CNavLink
            active={activeTab === 'statsTab'}
            onClick={() => setActiveTab('statsTab')}
          >
            Boiler Stats
          </CNavLink>
        </CNavItem>
        <CNavItem className="col-3">
          <CNavLink
            active={activeTab === 'statusTab'}
            onClick={() => setActiveTab('statusTab')}
          >
            Boiler Status
          </CNavLink>
        </CNavItem>
        <CNavItem className="col-3">
          <CNavLink
            active={activeTab === 'errorTab'}
            onClick={() => setActiveTab('errorTab')}
          >
            Boiler Error
          </CNavLink>
        </CNavItem>
        <CNavItem className="col-3">
          <CNavLink
            active={activeTab === 'infoTab'}
            onClick={() => setActiveTab('infoTab')}
          >
            Boiler Info
          </CNavLink>
        </CNavItem>
      </CNav>

      <CTabContent>
        <CTabPane visible={activeTab === 'statsTab'}>
          {renderStatsTab()}
        </CTabPane>
        <CTabPane visible={activeTab === 'statusTab'}>
          {renderStatusTab()}
        </CTabPane>
        <CTabPane visible={activeTab === 'errorTab'}>
          {renderErrorTab()}
        </CTabPane>
        <CTabPane visible={activeTab === 'infoTab'}>
          {renderInfoTab()}
        </CTabPane>
      </CTabContent>
    </div>
  );
};

export default Modbus;
