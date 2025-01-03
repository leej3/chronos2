import React from 'react';
import './SystemMap.css';
import { useSelector } from 'react-redux';

const SystemMap = ({ homedata }) => {
  const results = homedata?.results;
  const sensors = homedata?.sensors;

  const season = useSelector((state) => state.season.season);
  const manualOverride = useSelector((state) => state.manualOverride);

  console.log(season);

  return (
    <>
      {/* {console.log(manualOverride)} */}
      {season === 'Winter' ? (
        <div className="system-map">
          <h2 className="section-title">System Map</h2>
          <div className="tank-container">
            <div className="tank">
              <div className="tank-image">
                {manualOverride.boiler === true ? (
                  <img src="images/Icons/Boiler/Boiler-ON.png" alt="Tank" />
                ) : (
                  <img src="images/Icons/Boiler/Boiler-OFF.png" alt="Tank" />
                )}
              </div>
            </div>
            <div className="tankRight">
              <div className="tankRightArrow-wrapper">
                <img src="/images/Icons/Boiler/arrow4.png" alt="" srcSet="" />
                <span className="large-temp">{sensors?.water_out_temp}°F</span>
              </div>
              <div className="tankRightArrow-wrapper">
                <img src="/images/Icons/Boiler/arrow3.png" alt="" srcSet="" />
                <span>{sensors?.return_temp}°F</span>
              </div>
            </div>
          </div>
        </div>
      ) : season === 'Summer' ? (
        <div>
          <div className="system-map">
            <h2 className="section-title">System Map</h2>
            <div className="tank-container1">
              <div className="tank">
                <div className="tank-image">
                  {manualOverride.chiller1 === true ? (
                    <img src="images/Icons/Boiler/Chiller-ON.png" alt="Tank" />
                  ) : (
                    <img src="images/Icons/Boiler/Chiller-OFF.png" alt="" />
                  )}
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  {manualOverride.chiller2 === true ? (
                    <img src="images/Icons/Boiler/Chiller-ON.png" alt="Tank" />
                  ) : (
                    <img src="images/Icons/Boiler/Chiller-OFF.png" alt="" />
                  )}{' '}
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  {manualOverride.chiller3 === true ? (
                    <img src="images/Icons/Boiler/Chiller-ON.png" alt="Tank" />
                  ) : (
                    <img src="images/Icons/Boiler/Chiller-OFF.png" alt="" />
                  )}{' '}
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  {manualOverride.chiller4 === true ? (
                    <img src="images/Icons/Boiler/Chiller-ON.png" alt="Tank" />
                  ) : (
                    <img src="images/Icons/Boiler/Chiller-OFF.png" alt="" />
                  )}{' '}
                </div>
              </div>
            </div>
            <div className="arrow">
              <span>{results?.return_temp} °F</span>
              <div className="arrow-line"></div>
              <span className="large-temp">{results?.water_out_temp || 'N/A'} °F</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      )}
    </>
  );
};

export default SystemMap;
