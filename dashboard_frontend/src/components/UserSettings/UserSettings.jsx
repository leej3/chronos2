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

import { getTemperatureLimits } from '../../api/updateBoilerSetpoint';
import { updateSettings } from '../../api/updateSetting';
import './UserSettings.css';
import SeasonSwitch from '../SeasonSwitch/SeasonSwitch';

const UserSettings = ({ data }) => {
  const [formData, setFormData] = useState({
    tolerance: null,
    setpoint_min: null,
    setpoint_max: null,
    setpoint_offset_summer: null,
    setpoint_offset_winter: null,
    mode_change_delta_temp: null,
    mode_switch_lockout_time: null,
    cascade_time: null,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [tempLimits, setTempLimits] = useState({
    hard_limits: { min_setpoint: 70, max_setpoint: 110 },
    soft_limits: { min_setpoint: 70, max_setpoint: 110 },
  });
  const season = useSelector((state) => state.chronos.season);
  const [isEditing, setIsEditing] = useState(false);

  // Only fetch limits once on mount
  useEffect(() => {
    const fetchLimits = async () => {
      try {
        const limits = await getTemperatureLimits();
        setTempLimits(limits);
      } catch (error) {
        console.error('Failed to fetch temperature limits:', error);
      }
    };
    fetchLimits();
  }, []); // Empty dependency array means this only runs once on mount

  // Initialize form data only once when data is first received
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
      setIsEditing(true);
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
      // Convert string values to numbers where needed
      const processedData = Object.entries(formData).reduce(
        (acc, [key, value]) => {
          acc[key] = value === null ? null : Number(value);
          return acc;
        },
        {},
      );

      // Validate setpoint min/max against hard limits
      if (
        processedData.setpoint_min !== null ||
        processedData.setpoint_max !== null
      ) {
        const { hard_limits } = tempLimits;
        if (
          processedData.setpoint_min !== null &&
          (processedData.setpoint_min < hard_limits.min_setpoint ||
            processedData.setpoint_min > hard_limits.max_setpoint)
        ) {
          toast.error(
            `Minimum setpoint must be between ${hard_limits.min_setpoint}°F and ${hard_limits.max_setpoint}°F`,
          );
          return;
        }
        if (
          processedData.setpoint_max !== null &&
          (processedData.setpoint_max < hard_limits.min_setpoint ||
            processedData.setpoint_max > hard_limits.max_setpoint)
        ) {
          toast.error(
            `Maximum setpoint must be between ${hard_limits.min_setpoint}°F and ${hard_limits.max_setpoint}°F`,
          );
          return;
        }
        if (
          processedData.setpoint_min !== null &&
          processedData.setpoint_max !== null &&
          processedData.setpoint_min > processedData.setpoint_max
        ) {
          toast.error('Maximum setpoint must be greater than minimum setpoint');
          return;
        }
      }

      const response = await updateSettings(processedData);
      toast.success(response?.data?.message);
      setIsEditing(false);
    } catch (error) {
      console.error('Error response:', error);
      const errorMessage =
        error?.data?.detail ||
        error?.response?.data?.detail ||
        'Failed to update settings';
      toast.error(errorMessage);
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
    <div className="text-start">
      <CCardBody>
        <CForm onSubmit={handleSubmit}>
          <CRow>
            <CRow className="position-relative mb-2">
              {[
                { label: 'Baseline Setpoint', key: 'baseline_setpoint' },
                { label: 'THA Setpoint', key: 'tha_setpoint' },
                { label: 'Effective Setpoint', key: 'effective_setpoint' },
              ].map(({ label, key }) => (
                <CCol xs="12" key={key} className="mt-2">
                  <label
                    className="font-weight-bold"
                    htmlFor={key}
                    style={{ fontSize: '18px', fontWeight: 'bold' }}
                  >
                    {label}:
                  </label>
                  <span
                    className="font-italic"
                    style={{ fontSize: '16px', marginLeft: '10px' }}
                  >
                    {data.results[key] ?? '0.0'} <span>°F</span>
                  </span>
                </CCol>
              ))}

              <div className="icon_mode">
                {season === 'Summer' ? (
                  <span style={{ color: 'orange', fontSize: '24px' }}>
                    ☀️ Summer
                  </span>
                ) : season === 'Winter' ? (
                  <span style={{ color: 'lightblue', fontSize: '24px' }}>
                    ❄️ Winter
                  </span>
                ) : null}
              </div>
            </CRow>

            <CCol xs="12" className="text-center">
              <CButton
                color="primary"
                onClick={() => setShowForm(!showForm)}
                className="show-settings-btn"
              >
                {showForm ? 'Hide Settings' : 'Show Settings'}
              </CButton>
            </CCol>

            <div className={`show-settings-form ${showForm ? 'show' : ''}`}>
              <CRow>
                {[
                  { label: 'Tolerance', key: 'tolerance' },
                  {
                    label: 'Min. Setpoint',
                    key: 'setpoint_min',
                    min: tempLimits.hard_limits.min_setpoint,
                    max: tempLimits.hard_limits.max_setpoint,
                    help: `Hard limits: ${tempLimits.hard_limits.min_setpoint}°F - ${tempLimits.hard_limits.max_setpoint}°F`,
                  },
                  {
                    label: 'Max. Setpoint',
                    key: 'setpoint_max',
                    min: tempLimits.hard_limits.min_setpoint,
                    max: tempLimits.hard_limits.max_setpoint,
                    help: `Hard limits: ${tempLimits.hard_limits.min_setpoint}°F - ${tempLimits.hard_limits.max_setpoint}°F`,
                  },
                  season === 'Summer' && {
                    label: 'Setpoint Offset (Summer)',
                    key: 'setpoint_offset_summer',
                  },
                  season === 'Winter' && {
                    label: 'Setpoint Offset (Winter)',
                    key: 'setpoint_offset_winter',
                  },
                  {
                    label: 'Mode Change Delta Temp',
                    key: 'mode_change_delta_temp',
                  },
                  {
                    label: 'Mode Switch Lockout Time',
                    key: 'mode_switch_lockout_time',
                    unit: 'min.',
                  },
                  { label: 'Cascade Time', key: 'cascade_time', unit: 'min.' },
                ]
                  .filter(Boolean)
                  .map(({ label, key, unit = '', min, max, help }) => (
                    <CCol xs="12" key={key}>
                      <div style={{ marginBottom: '10px' }}>
                        <label
                          className="font-weight-bold"
                          htmlFor={key}
                          style={{ fontSize: '18px', fontWeight: 'bold' }}
                        >
                          {label}:
                          {help && (
                            <small
                              className="text-muted ms-2"
                              style={{ fontWeight: 'normal' }}
                            >
                              {help}
                            </small>
                          )}
                        </label>
                        <CFormInput
                          type="number"
                          name={key}
                          id={key}
                          value={formData[key] ?? ''}
                          onChange={handleInputChange}
                          placeholder={`${data.results[key] ?? '0.0'} ${unit}`}
                          min={min}
                          max={max}
                        />
                      </div>
                    </CCol>
                  ))}
                <CCol xs="12" className="text-end">
                  <CButton type="submit" color="primary" className="update-btn">
                    Update
                  </CButton>
                </CCol>
              </CRow >
            </div >
          </CRow >
        </CForm >
      </CCardBody >
    </div >
  );
};

export default UserSettings;
