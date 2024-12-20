/* eslint-disable react/prop-types */
import React, { useState, useEffect } from "react";
import "./UserSettings.css";
import { updateSettings } from "../../api/updateSetting";
import { toast } from "react-toastify";

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

  useEffect(() => {
    if (data && data.results) {
      setFormData({
        tolerance: data.results.tolerance || null,
        setpoint_min: data.results.setpoint_min || null,
        setpoint_max: data.results.setpoint_max || null,
        setpoint_offset_summer: data.results.setpoint_offset_summer || null,
        setpoint_offset_winter: data.results.setpoint_offset_winter || null,
        mode_change_delta_temp: data.results.mode_change_delta_temp || null,
        mode_switch_lockout_time: data.results.mode_switch_lockout_time || null,
        cascade_time: data.results.cascade_time || null,
      });
    }
  }, [data]);

  if (!data || !data.results) {
    return <div>Loading...</div>;
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

    updateSettings(JSON.stringify(formData))
      .then((response) => response.data)
      .then((data) => {
        console.log("Settings updated:", data);
        toast.success('User settings updated successfully');
      })
      .catch((error) => {
        console.error("Error updating settings:", error);
        toast.error('Some thing went wrong!');
      });
  };

  return (
    <div className="user-settings">
      <h2 className="section-title">User Settings</h2>
      <form onSubmit={handleSubmit}>
        <div className="settings-group">
          <label>Baseline Setpoint</label>
          <input
            type="number"
            value={data.results.baseline_setpoint || "0.0"}
            readOnly
            placeholder={`${data.results.baseline_setpoint} °F`}
          />
        </div>
        <div className="settings-group">
          <label>THA Setpoint</label>
          <input
            type="number"
            value={data.results.tha_setpoint || "0.0"}
            readOnly
            placeholder={`${data.results.tha_setpoint} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Effective Setpoint</label>
          <input
            type="number"
            value={data.results.effective_setpoint || "0.0"}
            readOnly
            placeholder={`${data.results.effective_setpoint} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Tolerance</label>
          <input
            type="number"
            name="tolerance"
            value={formData.tolerance}
            onChange={handleInputChange}
            placeholder={`${data.results.tolerance} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Min. Setpoint</label>
          <input
            type="number"
            name="setpoint_min"
            value={formData.setpoint_min}
            onChange={handleInputChange}
            placeholder={`${data.results.setpoint_min} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Max. Setpoint</label>
          <input
            type="number"
            name="setpoint_max"
            value={formData.setpoint_max}
            onChange={handleInputChange}
            placeholder={`${data.results.setpoint_max} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Setpoint Offset (Summer)</label>
          <input
            type="number"
            name="setpoint_offset_summer"
            value={formData.setpoint_offset_summer}
            onChange={handleInputChange}
            placeholder={`${data.results.setpoint_offset_summer} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Setpoint Offset (Winter)</label>
          <input
            type="number"
            name="setpoint_offset_winter"
            value={formData.setpoint_offset_winter}
            onChange={handleInputChange}
            placeholder={`${data.results.setpoint_offset_winter} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Mode Change Delta Temp</label>
          <input
            type="number"
            name="mode_change_delta_temp"
            value={formData.mode_change_delta_temp}
            onChange={handleInputChange}
            placeholder={`${data.results.mode_change_delta_temp} °F`}
          />
        </div>
        <div className="settings-group">
          <label>Mode Switch Lockout Time</label>
          <input
            type="number"
            name="mode_switch_lockout_time"
            value={formData.mode_switch_lockout_time}
            onChange={handleInputChange}
            placeholder={`${data.results.mode_switch_lockout_time} min.`}
          />
        </div>
        <div className="settings-group">
          <label>Cascade Time</label>
          <input
            type="number"
            name="cascade_time"
            value={formData.cascade_time}
            onChange={handleInputChange}
            placeholder="0.0 min"
          />
        </div>
        <button type="submit" className="update-btn">Update</button>
      </form>
    </div>
  );
};

export default UserSettings;
