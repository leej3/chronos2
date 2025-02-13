import React, { useEffect, useState } from 'react';
import { CAlert, CFormSwitch, CRow, CCol, CTooltip } from '@coreui/react';
import { useDispatch, useSelector } from 'react-redux';
import { updateDeviceState } from '../../api/updateState';
import {
  setOverride,
  setInitialState,
} from '../../features/state/ManualOverrideSlice';
import { getDeviceId } from '../../utils/constant';
import './ManualOverride.css';

const ManualOverride = ({ data }) => {
  const dispatch = useDispatch();
  const state = useSelector((state) => state.manualOverride);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const season = useSelector((state) => state.chronos?.season);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertColor, setAlertColor] = useState('danger');
  // const [socket, setSocket] = useState(null);

  console.log('Read only mode state:', readOnlyMode);

  useEffect(() => {
    if (!data?.devices) return;

    const devices = data.devices;
    dispatch(
      setInitialState({
        boiler: devices[0],
        chiller1: devices[1],
        chiller2: devices[2],
        chiller3: devices[3],
        chiller4: devices[4],
      }),
    );
  }, [data]);

  const isDeviceDisabled = (device) => {
    if (season === 1) {
      return device === 'boiler';
    }
    if (season === 0) {
      return device.startsWith('chiller');
    }
    return false;
  };

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

  const renderDeviceControl = (device) => {
    const isDisabled = isDeviceDisabled(device);
    const deviceName = device.charAt(0).toUpperCase() + device.slice(1);
    const tooltipContent = isDisabled
      ? `${deviceName} not available in ${season} mode`
      : `Click to toggle ${deviceName} ON/OFF`;

    return (
      <CCol
        xs={6}
        sm={6}
        md={4}
        lg={2.4}
        key={device}
        className="device-column"
      >
        <CTooltip content={tooltipContent} placement="top">
          <p className={`device-name ${isDisabled ? 'text-muted' : ''}`}>
            {deviceName}
          </p>
        </CTooltip>
        <CTooltip
          content={
            isDisabled
              ? `${deviceName} not available in ${season} mode`
              : 'Click to switch between ON and OFF'
          }
          placement="top"
        >
          <label>OFF</label>
          <CFormSwitch
            checked={state[device] === true}
            className="device-switch"
            onChange={(e) => handleRadioChange(device, e.target.checked)}
            size="xl"
            disabled={isDisabled}
          />
          <label>ON</label>
        </CTooltip >
      </CCol >
    );
  };

  return (
    <div className="manual-override">
      <h2 className="section-title px-3 py-2 m-0 text-break">
        Manual Override - {season === 1 ? 'Summer' : 'Winter'} Mode
      </h2>
      <div className="p-3">
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
              <>
                <strong>Error!</strong> {alertMessage}
              </>
            )}
          </CAlert>
        )}
        <CRow className="g-3 mx-0">
          {Object.keys(state)
            .filter(
              (device, index) =>
                index <= 4 &&
                (device === 'boiler' || device.startsWith('chiller')),
            )
            .map(renderDeviceControl)}
        </CRow>
      </div>
    </div>
  );
};

export default ManualOverride;
