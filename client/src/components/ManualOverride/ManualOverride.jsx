import React, { useEffect, useState } from 'react';
import './ManualOverride.css';
import { useDispatch, useSelector } from 'react-redux';
import { setOverride, setInitialState } from '../../features/state/ManualOverrideSlice';

const ManualOverride = ({ data }) => {
  const dispatch = useDispatch();
  const state = useSelector((state) => state.manualOverride);
  const [alertMessage, setAlertMessage] = useState('');

  useEffect(() => {
    if (data?.actStream) {
      const initialState = {
        boiler: getStatus(data.actStream[0].MO),
        chiller1: getStatus(data.actStream[1].MO),
        chiller2: getStatus(data.actStream[2].MO),
        chiller3: getStatus(data.actStream[3].MO),
        chiller4: getStatus(data.actStream[4].MO),
      };
      dispatch(setInitialState(initialState));
    }
  }, [data, dispatch]);

  const getStatus = (value) => (value === 0 ? 'auto' : value === 1 ? 'on' : 'off');

  const handleRadioChange = (device, value) => {
    const deviceNumber = {
      boiler: 0,
      chiller1: 1,
      chiller2: 2,
      chiller3: 3,
      chiller4: 4,
    }[device];

    const overrideValue = value === 'on' ? 1 : value === 'off' ? 2 : 0;

    // Dispatch Redux action to update state
    dispatch(setOverride({ device, value }));

    // Create form data for the API request
    const formData = new URLSearchParams();
    formData.append('device', deviceNumber);
    formData.append('manual_override', overrideValue);

    // Send the update to the backend
    fetch('http://localhost:80/update_state', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
      .then((response) => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then((data) => {
        if (data.error) setAlertMessage('Relay switching has failed.');
      })
      .catch((error) => {
        console.error('Error:', error);
        setAlertMessage('Relay switching has failed.');
      });
  };

  return (
    <div className="manual-override">
      <div className="manual-override-body">
        <h2>Manual Override</h2>
        {alertMessage && (
          <div className="alert alert-danger">
            <a href="#" className="close" data-dismiss="alert" aria-label="close">
              &times;
            </a>
            <strong>Error!</strong> {alertMessage}
          </div>
        )}
        <div className="override-controls">
          {Object.keys(state).map((device) => (
            <div key={device} className="control-group">
              <label>{device.replace(/^\w/, (c) => c.toUpperCase())}</label>
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    name={device}
                    value="auto"
                    checked={state[device] === 'auto'}
                    onChange={() => handleRadioChange(device, 'auto')}
                  />{' '}
                  Auto
                </label>
                <label>
                  <input
                    type="radio"
                    name={device}
                    value="on"
                    checked={state[device] === 'on'}
                    onChange={() => handleRadioChange(device, 'on')}
                  />{' '}
                  On
                </label>
                <label>
                  <input
                    type="radio"
                    name={device}
                    value="off"
                    checked={state[device] === 'off'}
                    onChange={() => handleRadioChange(device, 'off')}
                  />{' '}
                  Off
                </label>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ManualOverride;
