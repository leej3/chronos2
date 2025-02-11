import React, { memo } from 'react';
import { CRow, CCol, CCard, CCardBody, CButton } from '@coreui/react';
import { useSelector } from 'react-redux';

import { formatTemperature } from '../../utils/tranform';
import './SystemMap.css';

const SystemMap = ({ homedata, season, boiler }) => {
  const { sensors } = homedata || {};
  const {
    cascade_current_power,
    lead_firing_rate,
    outlet_temp,
    inlet_temp,
    system_supply_temp,
  } = boiler?.stats || {};
  const manualOverride = useSelector((state) => state.manualOverride);

  const renderWinterView = () => (
    <CRow>
      <CCol xs={12}>
        <CCard>
          <CCardBody>
            <h2 className="text-center mb-4"></h2>
            <CRow>
              <CCol
                xs={12}
                md={6}
                className="d-flex justify-content-md-end align-items-center mb-4 justify-content-center"
              >
                <div className="position-relative">
                  <img
                    src={
                      manualOverride.boiler
                        ? 'images/Icons/Boiler/Boiler-ON.png'
                        : 'images/Icons/Boiler/Boiler-OFF.png'
                    }
                    alt="Boiler"
                    className="responsive-image"
                  />

                  <div className="boiler-levels d-flex flex-column align-items-center gap-2 mt-2">
                    <span className="level-name">Cascade Fire</span>
                    <span className="level-percentage">
                      {cascade_current_power}%{' '}
                    </span>
                    <span className="level-name">Lead Fire</span>
                    <span className="level-percentage">
                      {lead_firing_rate}%{' '}
                    </span>
                  </div>
                </div>
              </CCol>

              <CCol
                md={6}
                className="d-none d-md-flex flex-column justify-content-md-center justify-content-center align-items-center align-items-md-start temp-value"
              >
                <div className="d-flex flex-column">
                  <div className="d-flex justify-content-between">
                    <span className="text-start">
                      {formatTemperature(outlet_temp)}
                    </span>
                    <span className="text-end">
                      {formatTemperature(system_supply_temp)}
                    </span>
                  </div>

                  <img
                    src="/images/Icons/Boiler/arrow4.png"
                    alt="Arrow"
                    className="responsive-arrow"
                  />
                  <span className="text-center">
                    {formatTemperature(sensors?.return_temp)}
                  </span>

                  <span className="text-start">
                    {formatTemperature(inlet_temp)}
                  </span>

                  <img
                    src="/images/Icons/Boiler/arrow3.png"
                    alt="Arrow"
                    className="responsive-arrow"
                  />
                  <span className="text-center ">
                    {formatTemperature(sensors?.water_out_temp)}
                  </span>
                </div>
              </CCol>

              <CCol sm={12} md={6} className="d-md-none">
                <div className="content-container-mobile">
                  <div className="temp-item">
                    <span className="temp-label">Return Temperature:</span>
                    <span className="temp-value">
                      {formatTemperature(sensors?.return_temp)}
                    </span>
                  </div>

                  <div className="temp-item">
                    <span className="temp-label">Water Out Temperature:</span>
                    <span className="temp-value">
                      {formatTemperature(sensors?.water_out_temp)}
                    </span>
                  </div>
                </div>
              </CCol>
            </CRow>
            <CRow className="d-flex justify-content-end ">
              <CCol xs="auto" className="px-1 mt-2">
                <CButton
                  color="primary"
                  className="mb-2"
                  onClick={() => handleButtonClick('manual')}
                  block="true"
                >
                  Manual Override
                </CButton>
              </CCol>
            </CRow>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );

  const renderSummerView = () => (
    <CRow>
      <CCol xs={12}>
        <CCard>
          <CCardBody className="p-0 overflow-hidden">
            <CRow className="mb-2 mt-2">
              <CCol className="d-flex justify-content-center d-none d-md-flex">
                <img
                  src="/images/Icons/Boiler/arrow4.png"
                  alt="Arrow Down"
                  className="responsive-arrow"
                />
              </CCol>
            </CRow>

            <CRow className="g-0 mb-2">
              <CCol xs={12}>
                <CRow className="g-0">
                  <CCol xs={6} className="d-flex justify-content-end pe-4">
                    <img
                      src={
                        manualOverride[`chiller1`]
                          ? 'images/Icons/Boiler/Chiller-ON.png'
                          : 'images/Icons/Boiler/Chiller-OFF.png'
                      }
                      alt="Chiller 1"
                      className="responsive-image"
                    />
                  </CCol>
                  <CCol xs={6} className="d-flex justify-content-start ps-4">
                    <img
                      src={
                        manualOverride[`chiller2`]
                          ? 'images/Icons/Boiler/Chiller-ON.png'
                          : 'images/Icons/Boiler/Chiller-OFF.png'
                      }
                      alt="Chiller 2"
                      className="responsive-image"
                    />
                  </CCol>
                </CRow>
              </CCol>
            </CRow>

            <CRow className="g-0 mb-2">
              <CCol xs={12}>
                <CRow className="g-0">
                  <CCol xs={6} className="d-flex justify-content-end pe-4">
                    <img
                      src={
                        manualOverride[`chiller3`]
                          ? 'images/Icons/Boiler/Chiller-ON.png'
                          : 'images/Icons/Boiler/Chiller-OFF.png'
                      }
                      alt="Chiller 3"
                      className="responsive-image"
                    />
                  </CCol>
                  <CCol xs={6} className="d-flex justify-content-start ps-4">
                    <img
                      src={
                        manualOverride[`chiller4`]
                          ? 'images/Icons/Boiler/Chiller-ON.png'
                          : 'images/Icons/Boiler/Chiller-OFF.png'
                      }
                      alt="Chiller 4"
                      className="responsive-image"
                    />
                  </CCol>
                </CRow>
              </CCol>
            </CRow>

            <CRow>
              <CCol className="d-flex justify-content-center d-none d-md-flex">
                <img
                  src="/images/Icons/Boiler/arrow3.png"
                  alt="Arrow Up"
                  className="responsive-arrow"
                />
              </CCol>
            </CRow>

            <CRow>
              <CCol className="d-flex justify-content-center align-items-center mb-4 d-none d-md-flex">
                <div className="d-flex align-items-center gap-2">
                  <span className="h4 mb-0">
                    Water Out: {formatTemperature(sensors?.water_out_temp)}
                  </span>
                  <div className="arrow-line mx-2"></div>
                  <span className="h4 mb-0">
                    Return: {formatTemperature(sensors?.return_temp)}
                  </span>
                </div>
              </CCol>
              <CCol sm={12} md={6} className="d-md-none">
                <div className="content-container-mobile  px-4 ">
                  <div className="temp-item">
                    <span className="temp-label">Return Temperature:</span>
                    <span className="temp-value">
                      {formatTemperature(sensors?.return_temp)}
                    </span>
                  </div>

                  <div className="temp-item">
                    <span className="temp-label">Water Out Temperature:</span>
                    <span className="temp-value">
                      {formatTemperature(sensors?.water_out_temp)}
                    </span>
                  </div>
                </div>
              </CCol>
            </CRow>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );

  return <>{season === 0 ? renderWinterView() : renderSummerView()}</>;
};

export default SystemMap;
