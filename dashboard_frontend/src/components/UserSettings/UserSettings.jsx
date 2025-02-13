import React, { useState, useEffect } from 'react';
import {
  CForm,
  CFormInput,
  CButton,
  CRow,
  CCol,
  CCardBody,
  CCard,
} from '@coreui/react';
import { toast } from 'react-toastify';
import { updateSettings } from '../../api/updateSetting';
import './UserSettings.css';
import SeasonSwitch from '../SeasonSwitch/SeasonSwitch';

const UserSettings = ({ data }) => {
  const initialFormData = {
    tolerance: null,
    setpoint_min: null,
    setpoint_max: null,
    setpoint_offset_summer: null,
    setpoint_offset_winter: null,
    mode_change_delta_temp: null,
    mode_switch_lockout_time: null,
    cascade_time: null,
  };

  const [formData, setFormData] = useState(initialFormData);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (data?.results && !isEditing) {
      setFormData({
        tolerance: data.results.tolerance ?? null,
        setpoint_min: data.results.setpoint_min ?? null,
        setpoint_max: data.results.setpoint_max ?? null,
        setpoint_offset_summer: data.results.setpoint_offset_summer ?? null,
        setpoint_offset_winter: data.results.setpoint_offset_winter ?? null,
        mode_change_delta_temp: data.results.mode_change_delta_temp ?? null,
        mode_switch_lockout_time: data.results.mode_switch_lockout_time ?? null,
        cascade_time: data.results.cascade_time ?? null,
      });
      setIsLoading(false);
    }
  }, [data, isEditing]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setIsEditing(true);
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await updateSettings(formData);
      toast.success(response?.data?.message);
      setIsEditing(false);
    } catch (error) {
      toast.error(error?.response?.data?.message || 'An error occurred');
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading user settings...</p>
      </div>
    );
  }

  return (
    <CRow>
      <CCol>
        <CCard className="text-start">
          <CCardBody>
            <h2 className="chronous-title text-center mb-4">User Settings</h2>
            <SeasonSwitch />

            <CForm onSubmit={handleSubmit}>
              <div className="content-container-mobile">
                <CRow className="tab-content-container">
                  {[
                    {
                      label: 'Baseline ',
                      key: 'baseline_setpoint',
                    },
                    { label: 'THA ', key: 'tha_setpoint' },
                    {
                      label: 'Effective',
                      key: 'effective_setpoint',
                    },
                  ].map(({ label, key }) => (
                    <CCol sm="12" key={key}>
                      <div className="temp-item">
                        <span className=" temp-label" htmlFor={key}>
                          {label}:
                        </span>
                        <span className="temp-value">
                          {data.results[key] ?? '0.0'} <span>°F</span>
                        </span>
                      </div>
                    </CCol>
                  ))}
                </CRow>
              </div>
              <h2 className="chronous-title text-center mb-0">Configuration</h2>
              <div className="content-container-mobile">
                <CRow className="tab-content-container">
                  {[
                    { label: 'Tolerance', key: 'tolerance' },
                    { label: 'Min. Setpoint', key: 'setpoint_min' },
                    { label: 'Max. Setpoint', key: 'setpoint_max' },
                    {
                      label: 'Setpoint Offset (Summer)',
                      key: 'setpoint_offset_summer',
                    },
                    {
                      label: 'Setpoint Offset (Winter)',
                      key: 'setpoint_offset_winter',
                    },
                    {
                      label: 'Mode Change Delta Temp',
                      key: 'mode_change_delta_temp',
                    },
                    {
                      label: 'Mode Switch Lockout Time (Minutes)',
                      key: 'mode_switch_lockout_time',
                      unit: 'min.',
                    },
                    {
                      label: 'Cascade Time',
                      key: 'cascade_time',
                      unit: 'min.',
                    },
                  ].map(({ label, key, unit = '' }) => (
                    <CCol xs="12" key={key}>
                      <div style={{ marginBottom: '10px' }}>
                        <span htmlFor={key} className="temp-label ">
                          {label}:
                        </span>
                        <CFormInput
                          type="number"
                          name={key}
                          id={key}
                          value={formData[key] ?? ''}
                          onChange={handleInputChange}
                          placeholder={`${data.results[key] ?? '0.0'} ${unit}`}
                        />
                      </div>
                    </CCol>
                  ))}
                </CRow>
              </div>
              <CCol xs="12" className="text-end">
                <CButton
                  type="submit"
                  color="primary"
                  className="update-btn m-2"
                >
                  Update
                </CButton>
              </CCol>
            </CForm>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default UserSettings;
