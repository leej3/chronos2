import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { CCardBody, CRow, CCol, CBadge } from "@coreui/react";
import { FaTemperatureHigh } from "react-icons/fa"; 
import "./TypeMode.css";

const TypeMode = ({ homedata }) => {
  const season = useSelector((state) => state.season.season);

  const outdoorTemp = homedata?.results?.outside_temp || "N/A";
  const avgTemp = homedata?.efficiency?.average_temperature_difference || "N/A";
  const systemStatus = homedata?.status ? "ONLINE" : "OFFLINE";

  // State for screen size and selected dropdown item
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [selectedOption, setSelectedOption] = useState("Outdoor Temp");

  useEffect(() => {
    const handleResize = () => {
      setIsSmallScreen(window.innerWidth <= 768); 
    };

    handleResize(); 
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleDropdownChange = (e) => {
    setSelectedOption(e.target.value);
  };

  const getSelectedValue = () => {
    if (selectedOption === "Outdoor Temp") {
      return outdoorTemp;
    } else if (selectedOption === "Avg Temp") {
      return avgTemp;
    }
    return "N/A";
  };

  return (
    <div className="text-center">
      <h2 className="sensor-title text-center">
        {season === "Winter" ? "Winter Mode" : "Summer Mode"}
      </h2>
      <CBadge color={systemStatus === "ONLINE" ? "success" : "danger"}>
        {systemStatus}
      </CBadge>

      <CCardBody className="mt-4">
        <CRow className="d-flex justify-content-center">
          {isSmallScreen && (
            <CCol xs={12}>
              <select 
                value={selectedOption} 
                onChange={handleDropdownChange} 
                className="form-control mb-4"
              >
                <option value="Outdoor Temp">Outdoor Temp</option>
                <option value="Avg Temp">Avg Temp (96 hrs)</option>
              </select>
            </CCol>
          )}

          <CCol xs={12} md={6} >
            {!isSmallScreen ? (
              <>
                <div className="temp-circle">
                  <FaTemperatureHigh size={50} color="#FFB600" />
                  <div className="temp-value">{outdoorTemp}°F</div>
                </div>
                <div className="temp-label mt-2">Outdoor Temp</div>
              </>
            ) : (
              <div className="temp-circle">
                <FaTemperatureHigh size={50} color="#FFB600" />
                <div className="temp-value">{getSelectedValue()}°F</div>
              </div>
            )}
          </CCol>

          <CCol xs={12} md={6} >
            {!isSmallScreen ? (
              <>
                <div className="temp-circle">
                  <FaTemperatureHigh size={50} color="#FFB600" />
                  <div className="temp-value">{avgTemp}°F</div>
                </div>
                <div className="temp-label mt-2">Avg Temp (96 hrs)</div>
              </>
            ) : null}
          </CCol>
        </CRow>
      </CCardBody>
    </div>
  );
};

export default TypeMode;
