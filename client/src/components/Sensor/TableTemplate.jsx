import React from "react";
import "./tabletemplate.css"
const TableTemplate = ({homedata}) => {
  const intelTemp = homedata?.results?.return_temp || "N/A";
  const outletTemp = homedata?.results?.water_out_temp || "N/A";

  return (
    <div className="season">
      <h2 className="season-title">Sensors</h2>
      <div className="season-group">
        <label>Intel</label>
        <input type="number" value={intelTemp} readOnly />
      </div>
      <div className="season-group">
        <label>Outlet</label>
        <input type="number" value={outletTemp} readOnly />
      </div>

     </div>
  );
};

export default TableTemplate;
