import React from "react";

const Ontime = ({ homedata }) => {
  const chiller1 = homedata?.actStream[1].timeStamp || "N/A";
  const chiller2 = homedata?.actStream[2].timeStamp || "N/A";
  const chiller3 = homedata?.actStream[3].timeStamp || "N/A";
  const chiller4 = homedata?.actStream[4].timeStamp || "N/A";
  const waterOutTemp = homedata?.results?.water_out_temp || "N/A";
  const averageTempDifference = homedata?.efficiency?.average_temperature_difference || "N/A";
  const cascadeFireRateAvg = homedata?.efficiency?.cascade_fire_rate_avg || "N/A";

  return (
    <div className="season">
      <h2 className="season-title">Ontime</h2>
      <div className="season-group">
        <label>Chiller 1</label>
        <p>{chiller1}</p>
      </div>
      <div className="season-group">
        <label>Chiller 2</label>
        <p>{chiller2}</p>
      </div>
      <div className="season-group">
        <label>Chiller 3</label>
        <p>{chiller3}</p>
      </div>
      <div className="season-group">
        <label>Chiller 4</label>
        <p>{chiller4}</p>
      </div>
    </div>
  );
};

export default Ontime;









