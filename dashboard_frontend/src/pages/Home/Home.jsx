/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useRef } from 'react';
import { parseISO, differenceInSeconds } from 'date-fns';

import {
  CContainer,
  CRow,
  CCol,
  CCard,
  CCardBody,
  CSpinner,
} from '@coreui/react';
import { useDispatch, useSelector } from 'react-redux';
import { toast } from 'react-toastify';

import ManualOverride from '../../components/ManualOverride/ManualOverride';
import SystemMap from '../../components/systemMap/SystemMap';
import TemperatureGraph from '../../components/TemperatureGraph/TemperatureGraph';
import { fetchData } from '../../features/chronos/chronosSlice';
import { REFRESH_TIME, RETRY_TIME } from '../../utils/constant';
import TypeMode from '../../components/TypeMode/TypeMode';
import UserSettings from '../../components/UserSettings/UserSettings';
import TableTemplate from '../../components/Sensor/TableTemplate';
import SwitchTimeDisplay from '../../components/SwitchTimeDisplay/SwitchTimeDisplay';
import Modbus from '../../components/Modebus/Modbus';
import EfficiencyMetrics from '../../components/EfficiencyMetrics/EfficiencyMetrics';
import { fetchCharData } from '../../features/chronos/temperatureSlice';
import './Home.css';

const LoadingOverlay = ({ remainingTimeRefresh, error }) => (
  <div className="loading-overlay">
    <div className="loading-content">
      <p className="loading-text mb-4 mt-0">{error}</p>
      <CSpinner color="primary" />
      <p className="loading-text mt-2">
        Try to connect again in {remainingTimeRefresh} seconds
      </p>
    </div>
  </div>
);

const Home = () => {
  const dispatch = useDispatch();
  const { data, status, error, season, devices } = useSelector(
    (state) => state.chronos,
  );
  const { data: temperatureData, status: temperatureStatus } = useSelector(
    (state) => state.temperature,
  );
  const [recallAPITime, setRecallAPITime] = useState(0);
  const [recallChartTime, setRecallChartTime] = useState(0);
  const [isShowPopupReload, setIsShowPopupReload] = useState(false);
  const [isReCallAPI, setIsReCallAPI] = useState(false);
  const intervalRef = useRef(null);
  const chartIntervalRef = useRef(null);
  const timeoutRef = useRef(null);
  const unlockTime = useSelector((state) => state.chronos.unlock_time);
  const calculateDelay = () => {
    if (unlockTime) {
      const unlockDate = parseISO(unlockTime);
      const now = new Date();
      const delayInSeconds = differenceInSeconds(unlockDate, now);
      return delayInSeconds > 0 ? delayInSeconds : 1;
    }
    return 1;
  };

  const fetchHomeData = async () => {
    dispatch(fetchData());
  };

  const fetchChartData = async () => {
    dispatch(fetchCharData());
  };

  useEffect(() => {
    fetchHomeData();
    fetchChartData();

    intervalRef.current = setInterval(() => {
      setRecallAPITime((prevTime) => (prevTime > 0 ? prevTime - 1 : 0));
    }, 1000);

    chartIntervalRef.current = setInterval(() => {
      setRecallChartTime((prevTime) => (prevTime > 0 ? prevTime - 1 : 0));
    }, 1000);

    return () => {
      clearInterval(intervalRef.current);
      clearInterval(chartIntervalRef.current);
    };
  }, []);

  useEffect(() => {
    if (recallChartTime === 0) {
      fetchChartData();
      setRecallChartTime(10);
    }
  }, [recallChartTime]);

  useEffect(() => {
    if (status === 'failed' || temperatureStatus === 'failed') {
      setIsShowPopupReload(true);
      setRecallAPITime(RETRY_TIME);
      toast.error('Failed to fetch data from edge server');
    } else if (status === 'succeeded' || temperatureStatus === 'succeeded') {
      if (isShowPopupReload) {
        toast.success('Data fetched successfully from edge server');
      }
      setIsShowPopupReload(false);
      setRecallAPITime(REFRESH_TIME);
    }
  }, [status, temperatureStatus]);

  useEffect(() => {
    if (
      recallAPITime === 0 &&
      (status === 'succeeded' ||
        status === 'failed' ||
        temperatureStatus === 'succeeded' ||
        temperatureStatus === 'failed')
    ) {
      setIsReCallAPI(true);
      timeoutRef.current = setTimeout(() => {
        fetchHomeData();
        setIsReCallAPI(false);
      }, calculateDelay() * 1000);
    }

    return () => clearTimeout(timeoutRef.current);
  }, [recallAPITime, status, temperatureStatus, unlockTime]);

  return (
    <>
      {isShowPopupReload && (
        <LoadingOverlay
          remainingTimeRefresh={recallAPITime}
          error={error}
          isReCallAPI={isReCallAPI}
        />
      )}

      <CContainer fluid>
        <CRow className="d-block d-lg-none mt-4 g-3">
          <CCol xs={12}>
            <CCard>
              <CCardBody className="p-0">
                <TemperatureGraph data={temperatureData} />
              </CCardBody>
            </CCard>
          </CCol>

          <CCol xs={12} className="mt-3">
            <CCard>
              <CCardBody className="p-0">
                <SystemMap
                  homedata={data}
                  season={season}
                  boiler={data?.boiler}
                />
              </CCardBody>
            </CCard>
          </CCol>

          <CCol xs={12} className="mt-3">
            {season === 1 ? (
              <SwitchTimeDisplay devices={devices} />
            ) : (
              <CCard>
                <CCardBody className="p-0">
                  <Modbus boiler={data?.boiler} />
                </CCardBody>
              </CCard>
            )}
          </CCol>

          <CCol xs={12} className="mt-3">
            <UserSettings data={data} />
          </CCol>

          <CCol xs={12} className="mt-3">
            <CCard>
              <CCardBody className="p-0">
                <ManualOverride data={data} season={season} />
              </CCardBody>
            </CCard>
          </CCol>
        </CRow>

        <CRow className="d-none d-lg-flex mt-4 g-3">
          <CCol lg={3}>
            <TypeMode homedata={data} />
            <div className="mt-3">
              <TableTemplate homedata={data} />
            </div>
            <div className="mt-3">
              {season === 1 ? (
                <SwitchTimeDisplay devices={devices} />
              ) : (
                <CCard className="mb-3">
                  <CCardBody className="p-0">
                    <Modbus boiler={data?.boiler} />
                  </CCardBody>
                </CCard>
              )}
            </div>
          </CCol>

          <CCol lg={6}>
            <CCard className="mb-3">
              <CCardBody className="p-0">
                <SystemMap
                  homedata={data}
                  season={season}
                  boiler={data?.boiler}
                />
              </CCardBody>
            </CCard>

            <CCard>
              <CCardBody className="p-0">
                <ManualOverride data={data} season={season} />
              </CCardBody>
            </CCard>
          </CCol>

          <CCol lg={3}>
            <UserSettings data={data} />
          </CCol>

          <CCol lg={12}>
            <CCard className="mt-3">
              <CCardBody className="p-0">
                <TemperatureGraph data={temperatureData} />
              </CCardBody>
            </CCard>
          </CCol>
        </CRow>
      </CContainer>
    </>
  );
};

export default Home;
