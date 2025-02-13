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

  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const season = useSelector((state) => state.season.season);

  // Only fetch limits once on mount
  useEffect(() => {
    if (data?.results && !isEditing) {
    const fetchLimits = async () => {
      try {
        const limits = await getTemperatureLimits();
        setTempLimits(limits);
      } catch (error) {
        console.error('Failed to fetch temperature limits:', error);
      }
    };
    fetchLimits();
  }
  },[]); 

  // Initialize form data only once when data is first received
  useEffect(() => {
    if (data?.results && !isInitialized) {
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
    setIsInitialized(true);
  };

  useEffect(() => {
    if (data?.results?.lockout_info) {
      const unlockTime = parseISO(data.results.lockout_info.unlock_time);
      const now = new Date();

      if (unlockTime > now) {
        setLockoutInfo({
          lockoutTime: data.results.lockout_info.mode_switch_lockout_time,
          unlockTime: unlockTime,
        });

        const currentMode = data.results.mode;
        setSwitchDirection(currentMode === 0 ? 'toWinter' : 'toSummer');
      } else {
        setLockoutInfo(null);
        setSwitchDirection(null);
      }
    }
  }, [data]);

  useEffect(() => {
    let timer;
    if (lockoutInfo?.unlockTime) {
      timer = setInterval(() => {
        const now = new Date();
        const diff = lockoutInfo.unlockTime.getTime() - now.getTime();

        if (diff <= 0) {
          setLockoutInfo(null);
          setSwitchDirection(null);
          setCountdown(null);
          clearInterval(timer);
        } else {
          const minutes = Math.floor(diff / 1000 / 60);
          const seconds = Math.floor((diff / 1000) % 60);
          setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
        }
      }, 1000);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [lockoutInfo]);

  


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
      toast.error(error?.response?.data?.message || 'Đã có lỗi xảy ra');
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
                          {help && (
                            <small
                              className="text-muted ms-2"
                              style={{ fontWeight: 'normal' }}
                            >
                              {help}
                            </small>
                          )}
                        </span>
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
