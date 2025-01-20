import { CCardBody, CRow, CCol, CWidgetStatsD } from "@coreui/react";
import PropTypes from 'prop-types';

import "./tabletemplate.css";
import {formatNumber} from "../../utils/tranform"

const HVACIcon = (props) => {
  return (
    <div className="hvac-icon" style={{ width: '130px', height: '119px', marginBottom: '20px' }}>
      <svg
        id="Layer_1"
        data-name="Layer 1"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 122.88 111.86"
        {...props}
      >
        <defs>
          <style>{`.cls-1{fill-rule:evenodd; fill: #ffffff;}`}</style>
        </defs>
        <title>hvac</title>
        <path
          className="cls-1"
          d="M60.58,82.84a26.92,26.92,0,0,0,6.35,12.64c2.1,2.33,3.14,4.66,3.14,7a9,9,0,0,1-2.8,6.63,9.48,9.48,0,0,1-13.37,0,9,9,0,0,1-2.79-6.63q0-3.5,3.13-7a26.67,26.67,0,0,0,6.34-12.64ZM71.09,49.52a21.45,21.45,0,0,1,2.53.14c3.79.43,6.1,2.15,9.41,3,4,1,5.54-3,5.19-6.31a15.73,15.73,0,0,0-1.49-4.84,19,19,0,0,0-2.41-3.8c-6.55-8.13-14.87-6-19.25,3.41a6.4,6.4,0,0,0-.56,2.14A7.78,7.78,0,0,0,63,43.08a8.4,8.4,0,0,0-2.2.3,22.48,22.48,0,0,1,.13-3c.43-3.79,2.15-6.11,3-9.42,1-4-3-5.54-6.32-5.17a15.41,15.41,0,0,0-4.83,1.49,18.64,18.64,0,0,0-3.79,2.42c-8.12,6.57-6,14.88,3.44,19.25a6.82,6.82,0,0,0,2.49.57,8.76,8.76,0,0,0-.2,1.86,7.79,7.79,0,0,0,.17,1.68A21.79,21.79,0,0,1,51.49,53c-3.8-.37-6.13-2.06-9.46-2.81-4-.92-5.49,3.09-5.08,6.39a15.87,15.87,0,0,0,1.56,4.81A19.12,19.12,0,0,0,41,65.18c6.68,8,15,5.8,19.19-3.72a6.25,6.25,0,0,0,.51-2,8.28,8.28,0,0,0,2.29.32,8.57,8.57,0,0,0,2.1-.27,25.21,25.21,0,0,1-.25,2.59c-.6,3.77-2.43,6-3.39,9.27-1.16,4,2.75,5.67,6.08,5.46a15.68,15.68,0,0,0,4.9-1.27,18.81,18.81,0,0,0,3.9-2.24C84.73,67.1,83,58.7,73.76,53.9a6.74,6.74,0,0,0-2.64-.7,8.74,8.74,0,0,0,.19-1.78,8.45,8.45,0,0,0-.22-1.9ZM7.62,35a2,2,0,1,1,3.55-1.68L12.47,36l1.33-3.27a2,2,0,0,1,3.64,1.48l-2.69,6.6,2.06,4.34,4.32-2,2-6.62a2,2,0,0,1,3.75,1.13l-1,3.21,2.77-1.31a2,2,0,1,1,1.67,3.55l-2.5,1.19,2.95,1.2a2,2,0,0,1-1.48,3.64l-6.28-2.56L18.5,48.71l2.09,4.41,6.8,2.08A2,2,0,0,1,26.26,59l-3.39-1,1.27,2.67a2,2,0,1,1-3.55,1.68l-1.18-2.49-1.14,2.77a2,2,0,1,1-3.64-1.47L17.12,55,15,50.39l-4.39,2.09L8.58,59a2,2,0,1,1-3.76-1.14l.94-3.05L3.06,56a2,2,0,0,1-1.67-3.56l2.93-1.39L1.23,49.83A2,2,0,1,1,2.7,46.19l6.43,2.62,4.13-2-2.14-4.51L4.83,40.41A2,2,0,0,1,6,36.65l2.88.88L7.62,35Zm93.12,5c.53,3.93,1.36,6.9,2.77,8a22.17,22.17,0,0,1,.4-3.92c.82-4.21,2.12-4.43,3.38-7.54a8.17,8.17,0,0,0,.41-4.92c4.51.81,8.69,7.83,9.74,16.75a9.73,9.73,0,0,0,1.92-5.29,12.79,12.79,0,0,1,3.34,7.35c.74,5.25-.82,8.65-4.94,10a6.93,6.93,0,0,0-.25-6.08,8.14,8.14,0,0,0-1.61-2.45c-.3,2.16-.75,3.79-1.52,4.4a13,13,0,0,0-.23-2.16c-.44-2.3-1.16-2.42-1.85-4.13a4.56,4.56,0,0,1-.23-2.7c-2.47.44-4.76,4.29-5.34,9.19a5.29,5.29,0,0,1-1-2.9,7.06,7.06,0,0,0-1.84,4,6.17,6.17,0,0,0,.36,3.56A8.07,8.07,0,0,1,97.56,56c-1.93-4.22-1.58-7.37.24-11.59A14.32,14.32,0,0,1,100.74,40ZM99.13,83.8A3.37,3.37,0,0,0,104.38,88a54.91,54.91,0,0,0,4.16-5.86,3.37,3.37,0,0,0-5.76-3.51,48.63,48.63,0,0,1-3.65,5.13ZM84.63,95.69a3.37,3.37,0,1,0,3.16,6,52.84,52.84,0,0,0,6.13-3.78,3.38,3.38,0,0,0-2.71-6,3.57,3.57,0,0,0-1.24.56,44.31,44.31,0,0,1-5.34,3.3Zm-53-6.09a3.37,3.37,0,0,0-4.39,5.12A58.93,58.93,0,0,0,33,99.05a3.38,3.38,0,0,0,4.39-5,3.13,3.13,0,0,0-.7-.61,47.7,47.7,0,0,1-5-3.8ZM13.83,75.79q0,.3,0,.63a3.53,3.53,0,0,0,.34,1.31A55.18,55.18,0,0,0,17.74,84a3.37,3.37,0,1,0,5.59-3.77,44.73,44.73,0,0,1-2.8-4.79,20.44,20.44,0,0,1-4.51.5,19.82,19.82,0,0,1-2.19-.12ZM27.84,22a3.37,3.37,0,0,0-5-4.55,53.12,53.12,0,0,0-4.14,5.11,20.45,20.45,0,0,1,6.81,2.15c.74-.93,1.5-1.83,2.31-2.71ZM43,11a3.37,3.37,0,0,0-1.72-6.42,3.21,3.21,0,0,0-1.1.3,54.11,54.11,0,0,0-6.32,3.4A3.37,3.37,0,0,0,36,14.45a3.28,3.28,0,0,0,1.51-.51A50.13,50.13,0,0,1,43,11ZM61.31,6.74a3.37,3.37,0,0,0,.87-6.6A3.46,3.46,0,0,0,61.11,0a46.79,46.79,0,0,0-7.17.69,3.38,3.38,0,0,0-.06,6.64,3.6,3.6,0,0,0,1.18,0,39.72,39.72,0,0,1,6.25-.6ZM79.79,10A3.37,3.37,0,0,0,82.23,3.7a52.94,52.94,0,0,0-6.85-2.18,3.38,3.38,0,0,0-2.65,6.1,3.45,3.45,0,0,0,1.06.46,48.64,48.64,0,0,1,6,1.91ZM95.55,20.16a3.38,3.38,0,0,0,5.35-4,3.29,3.29,0,0,0-.65-.88,54,54,0,0,0-5.47-4.66,3.37,3.37,0,0,0-4,5.42,46.67,46.67,0,0,1,4.79,4.08Zm-28.35,27a6,6,0,1,0,0,8.5l0,0a6,6,0,0,0,0-8.45Zm-12.9,53.9a1,1,0,1,1,1.92-.18,9.31,9.31,0,0,0,.93,3.47,6.23,6.23,0,0,0,2.39,2.48,1,1,0,0,1,.35,1.31,1,1,0,0,1-1.32.35,8.06,8.06,0,0,1-3.12-3.24,11.27,11.27,0,0,1-1.15-4.19Z"
        />
      </svg>
    </div>
  );
};

const TableTemplate = ({ homedata }) => {
  const intelTemp = formatNumber(homedata?.sensors?.return_temp) || "N/A";
  const outletTemp = formatNumber(homedata?.sensors?.water_out_temp) || "N/A";

  return (
    <CRow className="sensor-table">
      <CCol xs={12}>
        <CCardBody>
          <CRow>
            <CCol xs={12}>
              <CWidgetStatsD
                icon={<HVACIcon />}
                style={{ '--cui-card-cap-bg': 'none' }}
                values={[
                  { title: 'Intel Temp', value: `${intelTemp} °F` },
                  { title: 'Outlet Temp', value: `${outletTemp} °F` },
                ]}
              />
            </CCol>
          </CRow>
        </CCardBody>
      </CCol>
    </CRow>
  );
};

TableTemplate.propTypes = {
  homedata: PropTypes.shape({
    sensors: PropTypes.shape({
      return_temp: PropTypes.number,
      water_out_temp: PropTypes.number
    })
  })
};

export default TableTemplate;
