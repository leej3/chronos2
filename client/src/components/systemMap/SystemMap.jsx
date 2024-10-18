import React from "react";
import "./SystemMap.css";
import { useSelector } from "react-redux";

const SystemMap = ({ homedata }) => {
  const results = homedata?.results;
  const season = useSelector((state)=> state.season.season)
   console.log(season);
   
  return (
    <>
      {season === 'Winter' ? (
          <div className="system-map">
            <h2 className="section-title">System Map</h2>
            <div className="tank-container">
              <div className="tank">
                <div className="tank-image">
                  <img src="images/Icons/Boiler/Boiler-ON.png" alt="Tank" />
                </div>
                {/* <div className="temperature">{results?.water_out_temp} °F</div> */}
              </div>
              <div className="tankRight">
                <div className="tankRightArrow-wrapper">
                  <div className="arrowUpTemp">
                    <span>0 F</span>
                    <span>0 F</span>
                  </div>
                  <img src="/images/Icons/Boiler/arrow4.png" alt="" srcSet=""/>
                  <span>32.3 F</span>
                </div>
                
                <div className="tankRightArrow-wrapper">
                  <div className="arrowUpTemp">
                    <span>0 F</span>
                  </div>
                  <img src="/images/Icons/Boiler/arrow3.png" alt="" srcSet="" />
                  <span>32.3 F</span>
                </div>
                

              </div>


            {/* <div className="arrow">
              <span>{results?.return_temp || "N/A"} °F</span>
              <div className="arrow-line"></div>
              <span>{results?.water_out_temp} °F</span>
            </div> */}
          </div>
        </div>
      ) : season === 'Summer' ? (
        <div>
          <div className="system-map">
            <h2 className="section-title">System Map</h2>
            <div className="tank-container1">
              <div className="tank">
                <div className="tank-image">
                  <img src="images/Icons/Boiler/Chiller-OFF.png" alt="Tank" />
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  <img src="images/Icons/Boiler/Chiller-OFF.png" alt="Tank" />
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  <img src="images/Icons/Boiler/Chiller-OFF.png" alt="Tank" />
                </div>
              </div>
              <div className="tank">
                <div className="tank-image">
                  <img src="images/Icons/Boiler/Chiller-OFF.png" alt="Tank" />
                </div>
              </div>
            </div>
            <div className="arrow">
            <span>{results?.return_temp} °F</span>
              <div className="arrow-line"></div>
              <span>{results?.water_out_temp || "N/A"} °F</span>

            </div>
          </div>
        </div>
      ):(
        <div>
          <span>Something Wrong</span>
        </div>
      )}
    </>
  );
};

export default SystemMap;
