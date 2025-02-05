/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useRef } from 'react';

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
import { formatDate } from '../../utils/tranform';

import './Home.css';

const LoadingOverlay = ({ remainingTimeRefresh, error, lastUpdated }) => (
  <div className="loading-overlay">
    <div className="loading-content">
      {lastUpdated && (
        <p className="text-success mb-2 mt-0">
          Last updated data: {formatDate(lastUpdated)}
        </p>
      )}
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
  const { data, status, error, season, lastUpdated } = useSelector(
    (state) => state.chronos,
  );
  const [recallAPITime, setRecallAPITime] = useState(0);
  const [isShowPopupReload, setIsShowPopupReload] = useState(false);
  const [isReCallAPI, setIsReCallAPI] = useState(false);
  const intervalRef = useRef(null);
  const timeoutRef = useRef(null);

  const fetchHomeData = async () => {
    dispatch(fetchData());
  };

  useEffect(() => {
    fetchHomeData();

    intervalRef.current = setInterval(() => {
      setRecallAPITime((prevTime) => (prevTime > 0 ? prevTime - 1 : 0));
    }, 1000);

    return () => clearInterval(intervalRef.current);
  }, []);

  useEffect(() => {
    if (status === 'failed') {
      setIsShowPopupReload(true);
      setRecallAPITime(RETRY_TIME);
      toast.error('Failed to fetch data from edge server');
    } else if (status === 'succeeded') {
      if (isShowPopupReload) {
        toast.success('Data fetched successfully from edge server');
      }
      setIsShowPopupReload(false);
      setRecallAPITime(REFRESH_TIME);
    }
  }, [status]);

  useEffect(() => {
    if (
      recallAPITime === 0 &&
      (status === 'succeeded' || status === 'failed')
    ) {
      setIsReCallAPI(true);
      timeoutRef.current = setTimeout(() => {
        fetchHomeData();
        setIsReCallAPI(false);
      }, 1000);
    }

    return () => clearTimeout(timeoutRef.current);
  }, [recallAPITime, status]);

  return (
    <>
      {isShowPopupReload && (
        <LoadingOverlay
          remainingTimeRefresh={recallAPITime}
          error={error}
          isReCallAPI={isReCallAPI}
          lastUpdated={lastUpdated}
        />
      )}

      <CContainer fluid>
        <CRow>
          <CCol lg={12}>
            <CCard className="item mt-4">
              <CCardBody className="p-0">
                <SystemMap homedata={data} season={season} />
              </CCardBody>
            </CCard>

            <CCard className="item">
              <CCardBody className="p-0">
                <ManualOverride data={data} season={season} />
              </CCardBody>
            </CCard>

            <CCard className="item mt-4">
              <CCardBody className="p-0">
                <TemperatureGraph />
              </CCardBody>
            </CCard>
          </CCol>
        </CRow>
      </CContainer>
    </>
  );
};

export default Home;
