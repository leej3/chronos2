import React from "react";

const Modbus = ({ homedata }) => {
  const returnTemp = homedata?.results?.return_temp || "N/A";
  const waterOutTemp = homedata?.results?.water_out_temp || "N/A";
  const averageTempDifference = homedata?.efficiency?.average_temperature_difference || "N/A";
  const cascadeFireRateAvg = homedata?.efficiency?.cascade_fire_rate_avg || "N/A";

  return (
    <div className="season">
      <h2 className="season-title">Modbus</h2>
      <div className="season-group">
        <label>System Supply Temp</label>
        <input type="string" value='0 F' readOnly />
      </div>
      <div className="season-group">
        <label>Outlet Temp</label>
        <input type="string" value='0 F' readOnly />
      </div>
      <div className="season-group">
        <label>Inlet Temp</label>
        <input type="string" value='0 F' readOnly />
      </div>
      <div className="season-group">
        <label>Cascade Power</label>
        <input type="string" value='0 %' readOnly />
      </div>
      <div className="season-group">
        <label>Lead Firing Rate</label>
        <input type="string" value='0 %' readOnly />
      </div>
    </div>
  );
};

export default Modbus;
