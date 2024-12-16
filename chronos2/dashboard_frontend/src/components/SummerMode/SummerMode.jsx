import React from "react";
import "./SummerMode.css";

const SummerMode = ({ homedata }) => {
  // Extract the necessary data from homedata
  const mode = homedata?.results?.mode === 1 ? "Summer Mode" : homedata?.results?.mode === 0? "Winter Mode": homedata?.results?.mode === 2? "Summer to Winter": homedata?.results?.mode ===3 ?"Winter to Summer": "Default";
  const outdoorTemp = homedata?.results?.outside_temp || "N/A";
  const avgTemp = homedata?.efficiency?.average_temperature_difference || "N/A";
  const systemStatus = homedata?.chronos_status ? "ONLINE" : "OFFLINE";

  return (
    <div className="winter-mode">
      <div className="mode-header">
        <h2>{mode}</h2>
        <div className="status">System - {systemStatus}</div>
      </div>
      <div className="temperature-display">
        <div className="temp-circle">
          <div className="temp-value">{outdoorTemp}°F</div>
          <div className="temp-label">Outdoor Temp</div>
        </div>
        <div className="temp-circle">
          <div className="temp-value">{avgTemp}°F</div>
          <div className="temp-label">Avg Temp (96 hrs)</div>
        </div>
      </div>
    </div>
  );
};

export default SummerMode;
