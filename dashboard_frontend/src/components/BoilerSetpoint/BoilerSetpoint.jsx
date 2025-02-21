import React, { useState, useEffect } from 'react';

import {
  CForm,
  CFormInput,
  CButton,
  CAlert,
  CFormLabel,
  CCol,
  CRow,
} from '@coreui/react';
import { useSelector } from 'react-redux';

import {
  updateBoilerSetpoint,
  getTemperatureLimits,
} from '../../api/updateBoilerSetpoint';

const BoilerSetpoint = () => {
  const [temperature, setTemperature] = useState('');
  const [limits, setLimits] = useState({
    hard_limits: { min_setpoint: 70, max_setpoint: 110 },
    soft_limits: { min_setpoint: 70, max_setpoint: 110 },
  });
  const [alertMessage, setAlertMessage] = useState('');
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const [alertColor, setAlertColor] = useState('danger');

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLimits = async () => {
      try {
        const data = await getTemperatureLimits();
        setLimits(data);
      } catch (err) {
        console.error('Failed to fetch temperature limits:', err);
        setError('Failed to fetch temperature limits. Using default range.');
        setAlertColor('danger');
        setAlertMessage(
          'Failed to fetch temperature limits. Using default range.',
        );
      } finally {
        setLoading(false);
      }
    };

    fetchLimits();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }

    const temp = parseFloat(temperature);
    if (isNaN(temp)) {
      setAlertColor('danger');
      setAlertMessage('Temperature must be a number');
      return;
    }

    if (
      temp < limits.hard_limits.min_setpoint ||
      temp > limits.hard_limits.max_setpoint
    ) {
      setAlertColor('danger');
      setAlertMessage(
        `Temperature must be between ${limits.hard_limits.min_setpoint}°F and ${limits.hard_limits.max_setpoint}°F`,
      );
      return;
    }

    if (
      temp < limits.soft_limits.min_setpoint ||
      temp > limits.soft_limits.max_setpoint
    ) {
      if (
        !window.confirm(
          `Warning: Temperature is outside recommended range (${limits.soft_limits.min_setpoint}°F - ${limits.soft_limits.max_setpoint}°F). Continue?`,
        )
      ) {
        return;
      }
    }

    try {
      await updateBoilerSetpoint(temp);
      setAlertColor('success');
      setAlertMessage('Temperature updated successfully!');
    } catch (err) {
      setAlertColor('danger');
      setAlertMessage(err.message || 'Failed to update temperature');
    }
  };

  if (loading) {
    return <div>Loading temperature limits...</div>;
  }

  return (
    <div>
      <h2 className="chronous-title text-center mb-0">
        Update Boiler Setpoint
      </h2>
      <CForm onSubmit={handleSubmit}>
        <CRow>
          <CFormLabel className="temp-label text-start">
            Temperature (°F)
          </CFormLabel>
          <CCol>
            <CFormInput
              type="number"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder={`Enter temperature (${limits.soft_limits.min_setpoint}-${limits.soft_limits.max_setpoint}°F)`}
              min={limits.hard_limits.min_setpoint}
              max={limits.hard_limits.max_setpoint}
            />
          </CCol>
          <CCol xs="12" className="text-end mt-3">
            <CButton type="submit" color="primary" className="update-btn m-2">
              Update
            </CButton>
          </CCol>
        </CRow>
      </CForm>
      {alertMessage && (
        <CAlert
          color={alertColor}
          className=""
          dismissible
          onClose={() => setAlertMessage('')}
        >
          <strong>
            {alertColor === 'danger' && 'Error!'}
            {alertColor === 'warning' && 'Warning!'}
            {alertColor === 'success' && 'Success!'}
          </strong>{' '}
          {alertMessage}
        </CAlert>
      )}
    </div>
  );
};

export default BoilerSetpoint;
