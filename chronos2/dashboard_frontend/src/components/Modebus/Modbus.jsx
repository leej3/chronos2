import React from "react";
import { CFormLabel, CCol, CRow } from '@coreui/react';
import './Modbus.css'; 

const Modbus = ({ stats }) => {
  const system_supply_temp = stats?.system_supply_temp ?? "N/A";
  const outlet_temp = stats?.outlet_temp ?? "N/A";
  const inlet_temp = stats?.inlet_temp ?? "N/A";
  const cascade_current_power = stats?.cascade_current_power ?? "N/A";
  const lead_firing_rate = stats?.lead_firing_rate ?? "N/A";

  return (
    <div className="modbus" style={{ marginTop: '20px' }}>
      <h2 className="sensor-title text-center">Modbus</h2>
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
            <CFormLabel className="form-label"><strong>Cascade Power:</strong> <span>{`${cascade_current_power} °%`}</span></CFormLabel>
          </div>
        </CCol>

        <CCol sm="12">
          <div className="season-group">
            <CFormLabel className="form-label"><strong>Lead Firing Rate:</strong> <span>{`${lead_firing_rate} °%`}</span></CFormLabel>
          </div>
        </CCol>
      </CRow>
    </div>
  );
};

export default Modbus;
