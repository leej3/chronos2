import React, { useEffect, useState } from 'react';

import {
  CCard,
  CCardBody,
  CAlert,
  CFormSwitch,
  CRow,
  CCol,
} from '@coreui/react';
import { useDispatch, useSelector } from 'react-redux';

// import io from 'socket.io-client';
import { updateDeviceState } from '../../api/updateState';
import {
  setOverride,
  setInitialState,
} from '../../features/state/ManualOverrideSlice';
import { getDeviceId } from '../../utils/constant';

const ManualOverride = ({ data, season }) => {
  const dispatch = useDispatch();
  const state = useSelector((state) => state.manualOverride);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertColor, setAlertColor] = useState('danger');
  // const [socket, setSocket] = useState(null);

  console.log('Read only mode state:', readOnlyMode);

  useEffect(() => {
    if (data?.devices) {
      const devices = data.devices;
      const initialState = {
        boiler: devices[0],
        chiller1: devices[1],
        chiller2: devices[2],
        chiller3: devices[3],
        chiller4: devices[4],
      };
      dispatch(setInitialState(initialState));
    }
  }, [data, dispatch]);

  const handleRadioChange = async (device, state) => {
    console.log('Attempting state change in read-only mode:', readOnlyMode);
    
    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }

    setAlertColor('danger');
    console.log(device, state);
    dispatch(setOverride({ name: device, value: state }));

    const payload = {
      id: getDeviceId(device),
      state: state,
    };

    updateDeviceState(payload)
      .then((response) => {
        if (!response.status) throw new Error('Network response was not ok');
        return response.data;
      })
      .then((data) => {
        if (data.error) setAlertMessage('Relay switching has failed.');
      })
      .catch(() => {
        setAlertMessage('Relay switching has failed.');
      });
  };

  return (
    <CCard className="bgr">
      <h2 className="section-title">Manual Override</h2>
      <CCardBody className="p-0">
        {alertMessage && (
          <CAlert
            color={alertColor}
            dismissible
            onClose={() => {
              setAlertMessage('');
              setAlertColor('danger');
            }}
          >
            {alertColor === 'warning' ? (
              alertMessage
            ) : (
              <><strong>Error!</strong> {alertMessage}</>
            )}
          </CAlert>
        )}
        <CRow className="g-3">
          {Object.keys(state)
            .filter(
              (device, index) =>
                index <= 4 &&
                (device === 'boiler' || device.startsWith('chiller')),
            )
            .map((device) => (
              <CCol
                xs={12}
                sm={6}
                md={4}
                lg={2.4}
                key={device}
                className="d-flex flex-column align-items-center"
              >
                <p className="mb-3 h5 text-center">
                  {device.charAt(0).toUpperCase() + device.slice(1)}
                </p>
                <div className="d-flex gap-2 align-items-center">
                  <label>OFF</label>
                  <CFormSwitch
                    checked={state[device] === true}
                    className="cursor-pointer"
                    onChange={(e) =>
                      handleRadioChange(device, e.target.checked)
                    }
                    size="xl"
                    disabled={
                      (season === 'Winter' && device.startsWith('chiller')) ||
                      (season === 'Summer' && device === 'boiler')
                    }
                  />
                  <label>ON</label>
                </div>
              </CCol>
            ))}
        </CRow>
      </CCardBody>
    </CCard>
  );
};

export default ManualOverride;
