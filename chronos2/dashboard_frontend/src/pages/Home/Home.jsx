import React, { useState, useEffect } from 'react';
import UserSettings from '../../components/UserSettings/UserSettings';
import SystemMap from '../../components/systemMap/SystemMap';
import ManualOverride from '../../components/ManualOverride/ManualOverride';
import TemperatureGraph from '../../components/TemperatureGraph/TemperatureGraph';
import { useDispatch, useSelector } from 'react-redux';
import { fetchSummerData } from '../../features/summer/summerSlice';
import { setSeason } from '../../features/state/seasonSlice';
import { CContainer, CRow, CCol, CCard, CCardBody } from '@coreui/react';
import "./Home.css"
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

  return (
    <CContainer fluid>
      <CRow>
        <CCol lg={12}>
          <CCard className="item mt-4">
            <CCardBody className='p-0'>
              <SystemMap homedata={homedata} />
            </CCardBody>
          </CCard>

          <CCard className="item ">
            <CCardBody className='p-0'>
              <ManualOverride data={homedata} season={season} />
            </CCardBody>
          </CCard>
          <CCard className="item mt-4">
            <CCardBody className='p-0'>
              <TemperatureGraph />
            </CCardBody>
          </CCard> 
        </CCol>
      </CRow>
    </CContainer>
  );
};

export default Home;
