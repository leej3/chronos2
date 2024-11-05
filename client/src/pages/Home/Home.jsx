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
                data?.results?.mode === 0 ? dispatch(setSeason('Winter')) : data?.results?.mode === 1 ? dispatch(setSeason('Summer')) : data?.results?.mode === 2 ? dispatch(setSeason('Winter to summer')) : data?.results?.mode === 3 ? dispatch(setSeason('Summer to Winter')) : dispatch(setSeason('Default'));
            } else {
                console.error('Failed to fetch summer data');
            }
        };

        fetchData();
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
