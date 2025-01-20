import React, { useState, useEffect } from 'react';
import {
  CForm,
  CFormInput,
  CButton,
  CRow,
  CCol,
  CCardBody,
} from '@coreui/react';
import { updateSettings } from '../../api/updateSetting';
import { toast } from 'react-toastify';
import { useSelector } from 'react-redux';
import './UserSettings.css';

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
  const [showForm, setShowForm] = useState(false); // State để hiển thị form nhập liệu
  const season = useSelector((state) => state.season.season); // Lấy giá trị mùa từ Redux

  useEffect(() => {
    if (data?.results) {
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
    }
  }, [data]);

  if (!data?.results) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading user settings...</p>
      </div>
    );
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await updateSettings(JSON.stringify(formData));
      toast.success(response?.data?.message);
    } catch (error) {
      toast.error(error?.response?.data?.message || 'Đã có lỗi xảy ra');
    }
  };

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

            {/* Nút Show Settings chỉ hiển thị trên màn hình nhỏ */}
            <CCol xs="12" className="text-center">
              <CButton
                color="primary"
                onClick={() => setShowForm(!showForm)}
                className="show-settings-btn"
              >
                {showForm ? 'Hide Settings' : 'Show Settings'}
              </CButton>
            </CCol>

            {/* Form nhập liệu chỉ hiển thị khi bấm nút Show Settings */}
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
                    label: 'Mode Switch Lockout Time',
                    key: 'mode_switch_lockout_time',
                    unit: 'min.',
                  },
                  { label: 'Cascade Time', key: 'cascade_time', unit: 'min.' },
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
                          placeholder={`${data.results[key] ?? '0.0'} ${unit}`}
                        />
                      </div>
                    </CCol>
                  ))}
                <CCol xs="12" className="text-end">
                  <CButton type="submit" color="primary" className="update-btn">
                    Update
                  </CButton>
                </CCol>
              </CRow>
            </div>
          </CRow>
        </CForm>
      </CCardBody>
    </div>
  );
};

export default UserSettings;
