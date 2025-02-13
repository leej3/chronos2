import React, { useState } from 'react';

import {
  CForm,
  CFormInput,
  CButton,
  CAlert,
  CRow,
  CCol,
} from '@coreui/react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';

import { updateBoilerSetpoint } from '../../api/updateBoilerSetpoint';

const BoilerSetpoint = ({ currentSetpoint }) => {
  const [temperature, setTemperature] = useState(currentSetpoint || '');
  const [alertMessage, setAlertMessage] = useState('');
  const [alertColor, setAlertColor] = useState('danger');
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate temperature range
    const temp = parseFloat(temperature);
    if (isNaN(temp) || temp < 120 || temp > 180) {
      setAlertColor('danger');
      setAlertMessage('Temperature must be between 120°F and 180°F');
      return;
    }

    // Check read-only mode
    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('Cannot update setpoint: System is in read-only mode');
      return;
    }

    try {
      const response = await updateBoilerSetpoint(temp);
      toast.success(response?.data?.message || 'Setpoint updated successfully');
      setAlertMessage('');
    } catch (error) {
      setAlertColor('danger');
      const errorMessage = error?.response?.data?.detail;
      
      // Handle specific error cases
      if (errorMessage?.includes('read-only mode')) {
        setAlertColor('warning');
        setAlertMessage('Cannot update setpoint: System is in read-only mode');
      } else if (errorMessage?.includes('Too many temperature changes')) {
        setAlertMessage('Please wait a few seconds before changing the temperature again');
      } else if (errorMessage?.includes('Service temporarily unavailable')) {
        setAlertMessage('Service is temporarily unavailable due to multiple failures. Please try again later.');
      } else {
        setAlertMessage(errorMessage || 'Failed to update setpoint. Please try again.');
      }
    }
  };

  return (
    <div>
      <h4>Boiler Setpoint</h4>
      <CForm onSubmit={handleSubmit}>
        <CRow className="align-items-center">
          <CCol xs={12} sm={8} md={6}>
            <CFormInput
              type="number"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder="Enter temperature (°F)"
              disabled={readOnlyMode}
            />
          </CCol>
          <CCol xs={12} sm={4} md={6} className="mt-2 mt-sm-0">
            <CButton type="submit" color="primary" disabled={readOnlyMode}>
              Update Setpoint
            </CButton>
          </CCol>
        </CRow>
        {alertMessage && (
          <CAlert
            color={alertColor}
            className="mt-3"
            dismissible
            onClose={() => setAlertMessage('')}
          >
            {alertMessage}
          </CAlert>
        )}
      </CForm>
    </div>
  );
};

export default BoilerSetpoint; 