import React, { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar/Navbar';
import UserSettings from '../../components/UserSettings/UserSettings';
import SummerMode from '../../components/SummerMode/SummerMode';
import SystemMap from '../../components/systemMap/SystemMap';
import './Home.css';
import TableTemplate from '../../components/Sensor/TableTemplate';
import ManualOverride from '../../components/ManualOverride/ManualOverride';
import TemperatureGraph from '../../components/TemperatureGraph/TemperatureGraph';
import { useDispatch, useSelector } from 'react-redux';
import { fetchSummerData } from '../../features/summer/summerSlice';
import Modbus from '../../components/Modebus/Modbus';
import { setSeason } from '../../features/state/seasonSlice';
import Ontime from '../../components/OnTime/Ontime';

const Home = () => {
    const [homedata, setHomeData] = useState()
    const dispatch = useDispatch();
    const season = useSelector((state) => state.season.season);




    useEffect(() => {
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
    
        fetchData();
    
        // Re-check every second until season is 'Winter' or 'Summer'
        const interval = setInterval(() => {
            if (season !== 'Winter' && season !== 'Summer') {
                fetchData();
                
            } else {
                clearInterval(interval);  // Stop the interval when season is 'Winter' or 'Summer'
            }
        }, 2000);
    
        return () => clearInterval(interval);  // Cleanup interval on unmount
    }, [season]);
    


    return (
        <>
            <Navbar />
            <div className="home-container">
                <div className="left">
                    <div className="item1n2">
                        <div className="item1">
                            <SummerMode homedata={homedata} />
                            <TableTemplate homedata={homedata} />
                            {
                                season === 'Summer' ?  <Ontime homedata={homedata}/> : season === 'Winter'?  <Modbus homedata={homedata} /> :''
                            }
                           

                        </div>
                        <div className="item2">
                            <SystemMap homedata={homedata} />
                        </div>
                    </div>

                    <ManualOverride data={homedata} season={season}/>
                    <TemperatureGraph />
                </div>
                <div className="right">
                    <UserSettings data={homedata} />
                </div>
            </div>
        </>
    );
};

export default Home;
