/* eslint-disable react/prop-types */
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import io from 'socket.io-client';
import './ManualOverride.css';
import {
  setOverride,
  setInitialState,
} from '../../features/state/ManualOverrideSlice';
import { updateDeviceState } from '../../api/updateState';
import {
  CCard,
  CCardBody,
  CAlert,
  CFormSwitch,
  CRow,
  CCol,
} from '@coreui/react';
import { getDeviceId } from '../../utils/constant';

const ManualOverride = ({ data, season }) => {
  const dispatch = useDispatch();
  const state = useSelector((state) => state.manualOverride);
  const [alertMessage, setAlertMessage] = useState('');
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    console.log(data);
    if (data?.devices) {
      const devices = data.devices;
      const initialState = {
        boiler: devices[0].state,
        chiller1: devices[1].state,
        chiller2: devices[2].state,
        chiller3: devices[3].state,
        chiller4: devices[4].state,
      };
      dispatch(setInitialState(initialState));
    }
  }, [data, dispatch]);

  const handleRadioChange = async (device, state) => {
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


  // useEffect(() => {
  //   const socketInstance = io('http://localhost', {
  //     path: '/socket.io',
  //     transports: ['websocket'],
  //   });
  //   setSocket(socketInstance);

  //   socketInstance.on('connect', () =>
  //     console.log('Connected to WebSocket server')
  //   );

  //   socketInstance.on('manual_override', (data) => {
  //     const deviceMap = [
  //       'boiler',
  //       'chiller1',
  //       'chiller2',
  //       'chiller3',
  //       'chiller4',
  //     ];
  //     const deviceName = deviceMap[data.device];
  //     const status = getStatus(data.manual_override);
  //     dispatch(setOverride({ name: deviceName, value: status }));
  //   });

  //   socketInstance.on('connect_error', (err) =>
  //     console.error('Connection error:', err)
  //   );

  //   return () => {
  //     socketInstance.disconnect();
  //   };
  // }, [dispatch]);

  return (
    <CCard
      className="manual-override"
      style={{ maxWidth: '100%', padding: '1rem' }}
    >
      <h2 className="section-title">Manual Override</h2>
      <CCardBody className="">
        {alertMessage && (
          <CAlert color="danger"
            dismissible
            onClose={() => {
              setAlertMessage('');
            }}
          >
            <strong>Error!</strong> {alertMessage}
          </CAlert>
        )}
        <CRow className="override-controls" style={{ gap: '1rem' }}>
          {Object.keys(state)
            .filter(
              (device, index) =>
                index <= 4 &&
                (device === 'boiler' || device.startsWith('chiller'))
            )
            .map((device) => (
              <CCol
                xs={12}
                sm={6}
                md={4}
                lg={3}
                key={device}
                className="control-group"
                style={{ minWidth: '200px' }}
              >
                <p className="mb-3 h5">
                  {device.charAt(0).toUpperCase() + device.slice(1)}
                </p>
                <div className="switch-group d-flex gap-2 align-items-center">
                  <label>OFF</label>
                  <CFormSwitch
                    checked={state[device]}
                    className="cursor-pointer"
                    onChange={(e) => handleRadioChange(device, e.target.checked)}
                    size='xl'
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
