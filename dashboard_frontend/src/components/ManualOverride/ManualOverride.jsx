import React, { useEffect, useState } from 'react';
import {
  CAlert,
  CFormSwitch,
  CRow,
  CCol,
  CTooltip,
  CCard,
  CCardBody,
} from '@coreui/react';
import { useDispatch, useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { updateDeviceState } from '../../api/updateState';
import {
  setOverride,
  setInitialState,
} from '../../features/state/ManualOverrideSlice';
import { getDeviceId } from '../../utils/constant';
import { fetchData } from '../../features/chronos/chronosSlice';
import './ManualOverride.css';

const ManualOverride = ({ data }) => {
  const dispatch = useDispatch();
  const state = useSelector((state) => state.manualOverride);
  const season = useSelector((state) => state.chronos.season);
  const [alertMessage, setAlertMessage] = useState('');
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const [alertColor, setAlertColor] = useState('danger');
  const unlockTime = useSelector((state) => state.chronos.unlock_time);
  const [remainingTime, setRemainingTime] = useState('');
  // const [socket, setSocket] = useState(null);

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

  useEffect(() => {
    if (!unlockTime) {
      setAlertMessage('');
      return;
    }

    const updateRemainingTime = () => {
      const now = new Date();
      const unlockDateTime = new Date(unlockTime);
      const timeDiff = unlockDateTime - now;

      if (timeDiff <= 0) {
        setAlertMessage('');
        return;
      }

      const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

      const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
      setAlertMessage(`System is locked for ${timeStr}`);
      setAlertColor('warning');
    };

    updateRemainingTime();
    const timer = setInterval(updateRemainingTime, 1000);

    return () => clearInterval(timer);
  }, [unlockTime]);

  const isDeviceDisabled = (device) => {
    if (unlockTime) {
      return true;
    }

    if (season === 1) {
      return device === 'boiler';
    }
    if (season === 0) {
      return device.startsWith('chiller');
    }
    return false;
  };

  const handleDeviceStateChange = async (device, newState) => {
    if (isDeviceDisabled(device)) return;

    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }

    setAlertColor('danger');

    const deviceName = device.charAt(0).toUpperCase() + device.slice(1);
    const statusText = newState ? 'ON' : 'OFF';

    try {
      dispatch(setOverride({ name: device, value: newState }));

      const response = await updateDeviceState({
        id: getDeviceId(device),
        state: newState,
      });

      if (!response.status || response.data.error) {
        throw new Error('Failed to switch relay');
      }

      await dispatch(fetchData());

      toast.success(`${deviceName} has been turned ${statusText}`, {
        position: 'top-right',
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      dispatch(setOverride({ name: device, value: !newState }));

      toast.error(
        `Failed to turn ${deviceName} ${statusText}. Please try again.`,
        {
          position: 'top-right',
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        },
      );
      setAlertMessage('Relay switching has failed.');
    }
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
          <span className={`temp-label ${isDisabled ? 'text-muted' : ''}`}>
            {deviceName}
          </span>
        </CTooltip>
        <CTooltip
          content={
            isDisabled
              ? `${deviceName} not available in ${season} mode`
              : 'Click to switch between ON and OFF'
          }
          placement="top"
        >
          <div className={`device-control ${isDisabled ? 'disabled' : ''}`}>
            <span className="temp-label">OFF</span>
            <CFormSwitch
              checked={state[device].state === 1}
              className="temp-label"
              onChange={(e) =>
                handleDeviceStateChange(device, e.target.checked)
              }
              size="xl"
              disabled={isDisabled}
            />
            <span className="temp-label">ON</span>
          </div>
        </CTooltip>
      </CCol>
    );
  };

  return (
    <div>
      <CRow>
        <CCol>
          <CCard className="modbus-card">
            <CCardBody>
              <h2 className="chronous-title m-0">Manual Override</h2>
              <div className="p-3">
                {alertMessage && (
                  <CAlert
                    color={alertColor}
                    dismissible
                    onClose={() => setAlertMessage('')}
                  >
                    <strong>
                      {alertColor === 'danger' ? 'Error!' : 'Warning!'}
                    </strong>{' '}
                    {alertMessage}
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
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </div>
  );
};

export default ManualOverride;
