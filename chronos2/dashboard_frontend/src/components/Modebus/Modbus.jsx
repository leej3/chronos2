import React from "react";
import { CFormInput, CFormLabel, CCol, CRow } from '@coreui/react';
import './Modbus.css'; 

const Modbus = ({ stats }) => {
  const system_supply_temp = stats?.system_supply_temp ?? "N/A";
  const outlet_temp = stats?.outlet_temp ?? "N/A";
  const inlet_temp = stats?.inlet_temp ?? "N/A";
  const cascade_current_power = stats?.cascade_current_power ?? "N/A";
  const lead_firing_rate = stats?.lead_firing_rate ?? "N/A";

  return (
    <div className="modbus" style={{ marginTop: '20px' }}>
      <CRow>
        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label">System Supply Temp</CFormLabel>
            <CFormInput
              type="text"
              value={`${system_supply_temp} °F`}
              readOnly
              className="form-input"
            />
          </div>
        </CCol>

        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label">Outlet Temp</CFormLabel>
            <CFormInput
              type="text"
              value={`${outlet_temp} °F`}
              readOnly
              className="form-input"
            />
          </div>
        </CCol>

        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label">Inlet Temp</CFormLabel>
            <CFormInput
              type="text"
              value={`${inlet_temp} °F`}
              readOnly
              className="form-input"
            />
          </div>
        </CCol>

        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label">Cascade Power</CFormLabel>
            <CFormInput
              type="text"
              value={`${cascade_current_power} °%`}
              readOnly
              className="form-input"
            />
          </div>
        </CCol>

        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label">Lead Firing Rate</CFormLabel>
            <CFormInput
              type="text"
              value={`${lead_firing_rate} °%`}
              readOnly
              className="form-input"
            />
          </div>
        </CCol>
      </CRow>
    </div>
  );
};

export default Modbus;
