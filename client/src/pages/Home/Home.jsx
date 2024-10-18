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
import ModeSwitcher from '../../components/Test/ModeSwitcher';

const Home = () => {
    const [homedata, setHomeData] = useState()
    const dispatch = useDispatch();
  
    

    useEffect(() => {
        const fetchData = async () => {
            const resultAction = await dispatch(fetchSummerData());

            if (fetchSummerData.fulfilled.match(resultAction)) {
                const data = resultAction.payload;
                setHomeData(data);
                data?.results?.mode === 0 ? dispatch(setSeason('Winter')) :data?.results?.mode === 1 ? dispatch(setSeason('Summer')):dispatch(setSeason('Default'));
            } else {
                console.error('Failed to fetch summer data');
            }
        };

        fetchData();
    }, []);

    console.log(homedata);



    return (
        <>
            <Navbar />
            <div className="home-container">
                <div className="left">
                    <div className="item1n2">
                        <div className="item1">
                            <SummerMode homedata={homedata} />
                            <TableTemplate homedata={homedata} />
                            <Modbus homedata={homedata} />

                        </div>
                        <div className="item2">
                            <SystemMap homedata={homedata} />
                        </div>
                    </div>

                    <ManualOverride data = {homedata}/> 
                    <TemperatureGraph />
                    <ModeSwitcher/>
                </div>


                <div className="right">
                    <UserSettings data = {homedata}/>
                </div>


            </div>



        </>
    );
};

export default Home;
