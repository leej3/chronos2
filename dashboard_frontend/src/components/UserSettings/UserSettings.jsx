import React, { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';

import {
  CForm,
  CFormInput,
  CButton,
  CRow,
  CCol,
  CCardBody,
  CCard,
  CTooltip,
} from '@coreui/react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';

import { updateSettings } from '../../api/updateSetting';
import { setSeason } from '../../features/state/seasonSlice';
import { switchSeason } from '../../api/switchSeason';

import './UserSettings.css';

const UserSettings = ({ data }) => {
  const dispatch = useDispatch();
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
  const [showForm, setShowForm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const season = useSelector((state) => state.season.season);
  const [lockoutInfo, setLockoutInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [switchDirection, setSwitchDirection] = useState(null);

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
      toast.error(error?.response?.data?.message || 'Something went wrong');
    }
  };

  const handleSeasonChange = async (newSeason) => {
    try {
      const seasonValue = newSeason === 'Winter' ? 0 : 1;
      setSwitchDirection(newSeason === 'Winter' ? 'toWinter' : 'toSummer');

      const response = await switchSeason(seasonValue);

      if (response?.data?.status === 'success') {
        dispatch(setSeason(newSeason));
        toast.success(response.data.message);

        const unlockTime = parseISO(response.data.unlock_time);
        setLockoutInfo({
          lockoutTime: response.data.mode_switch_lockout_time,
          unlockTime: unlockTime,
        });
      }
    } catch (error) {
      setSwitchDirection(null);
      toast.error(error?.response?.data?.message || 'Failed to switch season');
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
        <CCard className=" text-start">
          <CCardBody>
            <CRow className="mb-4">
              <CCol className="d-flex justify-content-center">
                <div className="season-toggle w-100 justify-content-evenly">
                  <CTooltip
                    content={
                      lockoutInfo
                        ? `Locked - ${countdown} remaining`
                        : season === 'Winter'
                        ? 'Currently in Winter mode'
                        : 'Click to switch to Winter mode'
                    }
                    placement="top"
                  >
                    <div
                      className={`season-icon ${
                        season === 'Winter' ? 'active' : ''
                      } ${lockoutInfo ? 'locked' : ''}`}
                      onClick={() =>
                        !lockoutInfo && handleSeasonChange('Winter')
                      }
                    >
                      <span className="season-emoji">❄️</span>
                      <span>Winter</span>
                      {lockoutInfo && (
                        <div className="lockout-overlay">
                          <span className="lock-icon">🔒</span>
                          <span className="countdown">{countdown}</span>
                        </div>
                      )}
                    </div>
                  </CTooltip>

                  <div className="season-arrow">
                    {switchDirection ? (
                      <>
                        {switchDirection === 'toWinter' ? (
                          <BsArrowLeft
                            className={`arrow-icon switching`}
                            size={24}
                          />
                        ) : (
                          <BsArrowRight
                            className={`arrow-icon switching`}
                            size={24}
                          />
                        )}
                        <div className="switch-status">
                          <span>
                            Switching to{' '}
                            {switchDirection === 'toWinter'
                              ? 'Winter'
                              : 'Summer'}
                          </span>
                          <span className="countdown">{countdown}</span>
                        </div>
                      </>
                    ) : (
                      <BsArrowRight className="arrow-icon" size={24} />
                    )}
                  </div>

                  <CTooltip
                    content={
                      lockoutInfo
                        ? `Locked - ${countdown} remaining`
                        : season === 'Summer'
                        ? 'Currently in Summer mode'
                        : 'Click to switch to Summer mode'
                    }
                    placement="top"
                  >
                    <div
                      className={`season-icon ${
                        season === 'Summer' ? 'active' : ''
                      } ${lockoutInfo ? 'locked' : ''}`}
                      onClick={() =>
                        !lockoutInfo && handleSeasonChange('Summer')
                      }
                    >
                      <span className="season-emoji">☀️</span>
                      <span>Summer</span>
                      {lockoutInfo && (
                        <div className="lockout-overlay">
                          <span className="lock-icon">🔒</span>
                          <span className="countdown">{countdown}</span>
                        </div>
                      )}
                    </div>
                  </CTooltip>
                </div>
              </CCol>
            </CRow>
            <CForm onSubmit={handleSubmit}>
              <CRow>
                <CRow className="position-relative mb-2">
                  {[
                    {
                      label: 'Baseline Setpoint',
                      key: 'baseline_setpoint',
                    },
                    { label: 'THA Setpoint', key: 'tha_setpoint' },
                    {
                      label: 'Effective Setpoint',
                      key: 'effective_setpoint',
                    },
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
                      { label: 'Min. Setpoint', key: 'setpoint_min' },
                      { label: 'Max. Setpoint', key: 'setpoint_max' },
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
                        label: 'Mode Switch Lockout Time (Minutes)',
                        key: 'mode_switch_lockout_time',
                        unit: 'min.',
                      },
                      {
                        label: 'Cascade Time',
                        key: 'cascade_time',
                        unit: 'min.',
                      },
                    ]
                      .filter(Boolean)
                      .map(({ label, key, unit = '' }) => (
                        <CCol xs="12" key={key}>
                          <div style={{ marginBottom: '10px' }}>
                            <label
                              htmlFor={key}
                              style={{
                                fontWeight: 'bold',
                                display: 'block',
                                marginBottom: '5px',
                              }}
                            >
                              {label}:
                            </label>
                            <CFormInput
                              type="number"
                              name={key}
                              id={key}
                              value={formData[key] ?? ''}
                              onChange={handleInputChange}
                              placeholder={`${
                                data.results[key] ?? '0.0'
                              } ${unit}`}
                            />
                          </div>
                        </CCol>
                      ))}
                    <CCol xs="12" className="text-end">
                      <CButton
                        type="submit"
                        color="primary"
                        className="update-btn"
                      >
                        Update
                      </CButton>
                    </CCol>
                  </CRow>
                </div>
              </CRow>
            </CForm>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
};

export default UserSettings;
