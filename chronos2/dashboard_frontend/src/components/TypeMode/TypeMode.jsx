import React from "react";
import { useSelector } from "react-redux";
import {  CCardBody, CRow, CCol, CBadge,  } from "@coreui/react";
import { FaTemperatureHigh } from "react-icons/fa"; 
import "./TypeMode.css";

const TypeMode = ({ homedata }) => {
  const season = useSelector((state) => state.season.season);

  const outdoorTemp = homedata?.results?.outside_temp || "N/A";
  const avgTemp = homedata?.efficiency?.average_temperature_difference || "N/A";
  const systemStatus = homedata?.chronos_status ? "ONLINE" : "OFFLINE";

  return (
    <div className="text-center">
        <h2 className="sensor-title text-center">{season === "Winter" ? "Winter Mode" : "Summer Mode"}</h2>
        <CBadge color={systemStatus === "ONLINE" ? "success" : "danger"}>
          {systemStatus}
        </CBadge>
      <CCardBody className="mt-4">
        <CRow className="d-flex justify-content-center">
          <CCol xs={12} md={5} className="mb-4">
            <div className="temp-circle">
              <FaTemperatureHigh size={50} color="#FFB600" />
              <div className="temp-value">{outdoorTemp}°F</div>
            </div>
            <div className="temp-label mt-2">Outdoor Temp</div>
          </CCol>
          <CCol xs={12} md={5}>
            <div className="temp-circle">
              <FaTemperatureHigh size={50} color="#FFB600" />
              <div className="temp-value">{avgTemp}°F</div>
            </div>
            <div className="temp-label mt-2">Avg Temp (96 hrs)</div>
          </CCol>
        </CRow>
      </CCardBody>
    </div>
  );
};

export default TypeMode;
