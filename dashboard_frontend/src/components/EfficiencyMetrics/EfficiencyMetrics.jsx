import React from 'react';
import { CCard, CCardBody } from '@coreui/react';
import './EfficiencyMetrics.css';

const EfficiencyMetrics = ({ data }) => {
  const efficiency = data?.efficiency || {};

  return (
    <CCard className="h-100">
      <CCardBody className="efficiency-container">
        <h2 className="chronous-title">
          Efficiency Metrics ({efficiency.hours || 0} hrs)
        </h2>

        <div className="efficiency-metrics">
          <div className="metric-item">
            <span className="metric-label">Boiler Efficiency:</span>
            <span className="metric-value">
              {efficiency.chillers_efficiency?.toFixed(1) || 0}%
            </span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Avg Temp Difference:</span>
            <span className="metric-value">
              {efficiency.average_temperature_difference?.toFixed(1) || 0}°F
            </span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Avg Cascade Fire Rate:</span>
            <span className="metric-value">
              {efficiency.cascade_fire_rate_avg?.toFixed(1) || 0}%
            </span>
          </div>
        </div>
      </CCardBody>
    </CCard>
  );
};

export default EfficiencyMetrics;
