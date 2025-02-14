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

import { updateBoilerSetpoint, getTemperatureLimits } from '../../api/updateBoilerSetpoint';

const BoilerSetpoint = () => {
  const [temperature, setTemperature] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [limits, setLimits] = useState({ min_setpoint: 70, max_setpoint: 110 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLimits = async () => {
      try {
        const data = await getTemperatureLimits();
        setLimits(data);
      } catch (err) {
        console.error('Failed to fetch temperature limits:', err);
        setError('Failed to fetch temperature limits. Using default range.');
      } finally {
        setLoading(false);
      }
    };

    fetchLimits();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    const temp = parseFloat(temperature);
    if (isNaN(temp)) {
      setError('Temperature must be a number');
      return;
    }

    if (temp < limits.min_setpoint || temp > limits.max_setpoint) {
      setError(`Temperature must be between ${limits.min_setpoint}°F and ${limits.max_setpoint}°F`);
      return;
    }

    try {
      await updateBoilerSetpoint(temp);
      setSuccess(true);
      setTemperature('');
    } catch (err) {
      setError(err.message || 'Failed to update temperature');
    }
  };

  if (loading) {
    return <div>Loading temperature limits...</div>;
  }

  return (
    <div>
      <h2>Update Boiler Setpoint</h2>
      <CForm onSubmit={handleSubmit}>
        <CRow className="mb-3">
          <CCol>
            <CFormLabel>Temperature (°F)</CFormLabel>
            <CFormInput
              type="number"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder={`Enter temperature (${limits.min_setpoint}-${limits.max_setpoint}°F)`}
              min={limits.min_setpoint}
              max={limits.max_setpoint}
            />
          </CCol>
        </CRow>
        <CButton type="submit" color="primary" className="mt-3">Update Temperature</CButton>
      </CForm>
      {error && <CAlert color="danger" className="mt-3">{error}</CAlert>}
      {success && <CAlert color="success" className="mt-3">Temperature updated successfully!</CAlert>}
    </div>
  );
};

export default BoilerSetpoint; 