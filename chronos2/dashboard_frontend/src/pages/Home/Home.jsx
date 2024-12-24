import React, { useState, useEffect } from 'react';
import UserSettings from '../../components/UserSettings/UserSettings';
import SystemMap from '../../components/systemMap/SystemMap';
import './Home.css';
import ManualOverride from '../../components/ManualOverride/ManualOverride';
import TemperatureGraph from '../../components/TemperatureGraph/TemperatureGraph';
import { useDispatch, useSelector } from 'react-redux';
import { fetchSummerData } from '../../features/summer/summerSlice';
import { setSeason } from '../../features/state/seasonSlice';
import { CContainer, CRow, CCol, CCardBody } from '@coreui/react';

const Home = () => {
  const [homedata, setHomeData] = useState();
  const dispatch = useDispatch();
  const season = useSelector((state) => state.season.season);
  const fetchData = async () => {
    const resultAction = await dispatch(fetchSummerData());

    if (fetchSummerData.fulfilled.match(resultAction)) {
      const data = resultAction.payload;
      setHomeData(data);

      // Set season based on data results
      const mode = data?.results?.mode;
      switch (mode) {
        case 0:
          dispatch(setSeason('Winter'));
          break;
        case 1:
          dispatch(setSeason('Summer'));
          break;
        case 2:
          dispatch(setSeason('Winter to summer'));
          break;
        case 3:
          dispatch(setSeason('Summer to Winter'));
          break;
        default:
          dispatch(setSeason('Default'));
          break;
      }
    } else {
      console.error('Failed to fetch summer data');
    }
  };
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, [season]);
  
  // useEffect(() => {
  //   fetchData();

  //   const interval = setInterval(() => {
  //     if (season !== 'Winter' && season !== 'Summer') {
  //       fetchData();
  //     } else {
  //       clearInterval(interval); // Stop the interval when season is 'Winter' or 'Summer'
  //     }
  //   }, 2000);

  //   return () => clearInterval(interval); // Cleanup interval on unmount
  // }, [season]);

  return (
    <CContainer fluid className="home-container">
      <CRow>
        <CCol lg={9}>
          <div className="mb-3 p-0 border-0">
            <CCardBody>
              <SystemMap homedata={homedata} />
            </CCardBody>
          </div>
          <div className="mb-3 p-0 border-0">
            <ManualOverride data={homedata} season={season} />
          </div>
          <div className="mb-3 p-0 border-0">
            <TemperatureGraph className="p-0" />
          </div>
        </CCol>
        <CCol lg={3}>
          <div className="mb-3 p-0 border-0">
            <UserSettings data={homedata} />
          </div>
        </CCol>
      </CRow>
    </CContainer>
  );
};

export default Home;
