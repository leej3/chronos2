import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Modbus from '../Modebus/Modbus';
import TableTemplate from '../Sensor/TableTemplate';
import TypeMode from '../TypeMode/TypeMode';
import UserSetting from '../UserSettings/UserSettings'; 
import {formatNumber} from "../../utils/tranform"

import { CButton, CModal, CModalBody, CModalFooter, CRow, CCol, CCard, CCardBody, CContainer,CModalHeader,CModalTitle } from '@coreui/react';
import './SystemMap.css';

const SystemMap = ({ homedata }) => {
  const { results, sensors, boiler } = homedata || {};
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState(null);
  const season = useSelector((state) => state.season.season);
  const manualOverride = useSelector((state) => state.manualOverride);

  const handleButtonClick = (contentType) => {
    setModalContent(contentType);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const renderWinterView = () => (
    <CContainer fluid className='p-0'>
      <CRow>
        <CCol xs={12}>
          <CCard className="mb-4 bgr p-0">
            <CCardBody>
              <h2 className="text-center mb-4">{season === 'Winter' ? 'System Map - Winter' : 'System Map - Summer'}</h2>
              <CRow className="mb-4">
                <CCol xs={12} md={6} className="d-flex justify-content-center justify-content-md-end align-items-center mb-4">
                  <img
                    src={manualOverride.boiler ? "images/Icons/Boiler/Boiler-ON.png" : "images/Icons/Boiler/Boiler-OFF.png"}
                    alt="Boiler"
                    className="responsive-image"
                  />
                </CCol>
                <CCol xs={12} md={6} className="d-flex justify-content-center justify-content-md-start align-items-center">
                  <div className="d-flex flex-column justify-content-center align-items-start">
                    <img src="/images/Icons/Boiler/arrow4.png" alt="Arrow" className="mb-2 responsive-arrow" />
                    <span className="h4 w-100 text-center">{formatNumber(sensors?.water_out_temp)}°F</span>
                    <img src="/images/Icons/Boiler/arrow3.png" alt="Arrow" className="mb-2 responsive-arrow" />
                    <span className="h4 w-100 text-center">{formatNumber(sensors?.return_temp)}°F</span>
                  </div>
                </CCol>
              </CRow>
              <CRow className="d-flex justify-content-center mb-4 w-100">
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('advanced')} block>
                  Advanced
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('table')} block>
                    Sensors
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('typemode')} block>
                    Mode
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('userSetting')} block>
                    User Setting
                  </CButton>
                </CCol>
              </CRow>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  );

  const renderSummerView = () => (
    <CContainer fluid>
      <CRow>
        <CCol xs={12}>
          <CCard className="mb-4">
            <CCardBody>
              <h2 className="text-center mb-4">System Map - Summer</h2>
              <CRow className="mb-4">
                {[...Array(4)].map((_, index) => (
                  <CCol key={index} xs={6} md={3} className="d-flex justify-content-center align-items-center">
                    <img
                      src={manualOverride[`chiller${index + 1}`] ? "images/Icons/Boiler/Chiller-ON.png" : "images/Icons/Boiler/Chiller-OFF.png"}
                      alt={`Chiller ${index + 1}`}
                      className="responsive-image"
                    />
                  </CCol>
                ))}
              </CRow>
              <CRow className="d-flex align-items-center mb-3">
                <CCol xs="auto">
                  <span className="h5">{results?.return_temp}°F</span>
                </CCol>
                <CCol className="mx-2">
                  <div className="border-bottom" style={{ height: '2px', backgroundColor: '#000' }}></div>
                </CCol>
                <CCol xs="auto">
                  <span className="h4">{results?.water_out_temp || 'N/A'}°F</span>
                </CCol>
              </CRow>
              <CRow className="d-flex justify-content-center mb-4 w-100">
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('advanced')} block>
                  Advanced
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('table')} block>
                    Sensors
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('typemode')} block>
                    Mode
                  </CButton>
                </CCol>
                <CCol xs="auto" className="px-1">
                  <CButton color="primary" onClick={() => handleButtonClick('userSetting')} block>
                    User Setting
                  </CButton>
                </CCol>
              </CRow>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  );

  const renderLoadingView = () => (
    <CContainer fluid>
      <CRow>
        <CCol xs={12} className="d-flex justify-content-center">
          <div className="spinner-border text-primary" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </CCol>
      </CRow>
    </CContainer>
  );

  return (
    <>
      {season === 'Winter' ? renderWinterView() : season === 'Summer' ? renderSummerView() : renderLoadingView()}
    
      <CModal alignment="center" visible={isModalOpen} onClose={closeModal} aria-labelledby="ModbusModal"  className="modal-lg">
      <CModalHeader>
    <CModalTitle>
      {modalContent === 'advanced' && 'Advanced Boiler'}
      {modalContent === 'table' && 'Sensors'}
      {modalContent === 'typemode' && 'Type Mode Settings'}
      {modalContent === 'userSetting' && 'User Settings'}
    </CModalTitle>
  </CModalHeader>
        <CModalBody>
          {modalContent === 'advanced' && <Modbus boiler={boiler} />}
          {modalContent === 'table' && <TableTemplate homedata={homedata} />}
          {modalContent === 'typemode' && <TypeMode homedata={homedata} />}
          {modalContent === 'userSetting' && <UserSetting  data={homedata} />}
        </CModalBody>
        {modalContent !== 'userSetting' && (
          <CModalFooter>
            <CButton color="secondary" onClick={closeModal}>
              Close
            </CButton>
          </CModalFooter>
        )}
      </CModal>
    </>
  );
};

export default SystemMap;
