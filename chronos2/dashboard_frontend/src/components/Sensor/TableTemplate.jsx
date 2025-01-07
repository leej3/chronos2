import React from "react";
import { CCard, CCardBody, CRow, CCol } from "@coreui/react";
import "./tabletemplate.css";

const TableTemplate = ({ homedata }) => {
  const intelTemp = homedata?.sensors?.return_temp || "N/A";
  const outletTemp = homedata?.sensors?.water_out_temp || "N/A";

  return (
    <CRow className="sensor-table">
      <CCol xs={12}>
          <CCardBody>
            <h2 className="sensor-title text-center">Sensors</h2>
            <CRow>
              <CCol xs={6} className="d-flex justify-content-center align-items-center">
                <div className="sensor-group">
                  <h5>Intel Temp</h5>
                  <div className="sensor-value">{intelTemp}°F</div>
                </div>
              </CCol>
              <CCol xs={6} className="d-flex justify-content-center align-items-center">
                <div className="sensor-group">
                  <h5>Outlet Temp</h5>
                  <div className="sensor-value">{outletTemp}°F</div>
                </div>
              </CCol>
            </CRow>
          </CCardBody>
      </CCol>
    </CRow>
  );
};

export default TableTemplate;
