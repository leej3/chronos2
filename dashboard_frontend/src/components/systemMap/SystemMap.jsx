import React, { useState, memo } from 'react';
import {
  CButton,
  CModal,
  CModalBody,
  CModalFooter,
  CRow,
  CCol,
  CCard,
  CCardBody,
  CModalHeader,
  CModalTitle,
} from '@coreui/react';
import { useSelector } from 'react-redux';

import { formatTemperature } from '../../utils/tranform';
import ManualOverride from '../ManualOverride/ManualOverride';
import './SystemMap.css';

const SystemMap = memo(({ homedata, season }) => {
  const { sensors } = homedata || {};
  const [isModalOpen, setIsModalOpen] = useState(false);
  const manualOverride = useSelector((state) => state.manualOverride);

  const closeModal = () => setIsModalOpen(false);
  const openModal = () => setIsModalOpen(true);

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
                className="d-flex justify-content-md-end align-items-center mb-4 justify-content-center "
              >
                <img
                  src={
                    manualOverride.boiler
                      ? 'images/Icons/Boiler/Boiler-ON.png'
                      : 'images/Icons/Boiler/Boiler-OFF.png'
                  }
                  alt="Boiler"
                  className="responsive-image"
                />
              </CCol>
              <CCol
                xs={12}
                md={6}
                className="d-flex flex-column justify-content-md-center justify-content-center align-items-center align-items-md-start"
              >
                <div className="d-flex flex-column">
                  <img
                    src="/images/Icons/Boiler/arrow4.png"
                    alt="Arrow"
                    className="mb-2 responsive-arrow"
                  />
                  <span className="h4 text-center">
                    Water Out: {formatTemperature(sensors?.water_out_temp)}
                  </span>
                  <img
                    src="/images/Icons/Boiler/arrow3.png"
                    alt="Arrow"
                    className="mb-2 responsive-arrow"
                  />
                  <span className="h4 text-center">
                    Return: {formatTemperature(sensors?.return_temp)}
                  </span>
                </div>
              </CCol>
            </CRow>
            <CRow className="d-flex justify-content-end d-lg-none">
              <CCol xs="auto" className="px-1 mt-2">
                <CButton
                  color="primary"
                  className="mb-2 mt-2"
                  onClick={openModal}
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
              <CCol className="d-flex justify-content-center">
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
              <CCol className="d-flex justify-content-center">
                <img
                  src="/images/Icons/Boiler/arrow3.png"
                  alt="Arrow Up"
                  className="responsive-arrow"
                />
              </CCol>
            </CRow>

            <CRow>
              <CCol className="d-flex justify-content-center align-items-center mb-4">
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
            </CRow>
          </CCardBody>
          <CRow className="d-flex justify-content-end d-lg-none m-2">
            <CCol xs="auto">
              <CButton color="primary" onClick={openModal} block="true">
                Manual Override
              </CButton>
            </CCol>
          </CRow>
        </CCard>
      </CCol>
    </CRow>
  );

  return (
    <>
      {season === 0 ? renderWinterView() : renderSummerView()}

      <CModal
        alignment="center"
        visible={isModalOpen}
        onClose={closeModal}
        aria-labelledby="ManualOverrideModal"
        className="modal-lg"
      >
        <CModalHeader>
          <CModalTitle>Manual Override</CModalTitle>
        </CModalHeader>
        <CModalBody>
          <ManualOverride data={homedata} season={season} />
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" onClick={closeModal}>
            Close
          </CButton>
        </CModalFooter>
      </CModal>
    </>
  );
});

export default SystemMap;
