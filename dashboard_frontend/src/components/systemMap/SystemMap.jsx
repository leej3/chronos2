import React, { useState, useEffect, memo } from 'react';

import {
  CButton,
  CModal,
  CModalBody,
  CModalFooter,
  CRow,
  CCol,
  CCard,
  CCardBody,
  CContainer,
  CModalHeader,
  CModalTitle,
} from '@coreui/react';
import { useSelector } from 'react-redux';

import { formatTemperature } from '../../utils/tranform';
import Modbus from '../Modebus/Modbus';
import TableTemplate from '../Sensor/TableTemplate';
import TypeMode from '../TypeMode/TypeMode';
import UserSetting from '../UserSettings/UserSettings';

import './SystemMap.css';
import ManualOverride from '../ManualOverride/ManualOverride';

const MODAL_CONTENTS = {
  advanced: {
    title: 'Advanced Boiler',
    component: ({ boiler }) => <Modbus boiler={boiler} />,
  },
  sensors: {
    title: 'Sensors',
    component: ({ homedata }) => <TableTemplate homedata={homedata} />,
  },
  mode: {
    title: 'Type Mode Settings',
    component: ({ homedata }) => <TypeMode homedata={homedata} />,
  },
  usersetting: {
    title: 'User Settings',
    component: ({ data }) => <UserSetting data={data} />,
  },
};

const BUTTONS = ['Advanced', 'Sensors', 'Mode', 'User Setting'];

const SystemMap = memo(({ homedata, season }) => {
  const { results, sensors, boiler } = homedata || {};
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState(null);

  const manualOverride = useSelector((state) => state.manualOverride);
  const handleButtonClick = (contentType) => {
    setModalContent(contentType);
    setIsModalOpen(true);
  };
  const closeModal = () => setIsModalOpen(false);

  const renderButtons = () => (
    <CRow className="d-flex justify-content-center mb-4 w-100">
      {BUTTONS.map((btn, idx) => (
        <CCol xs="auto" key={idx} className="px-1">
          <CButton
            color="primary"
            onClick={() =>
              handleButtonClick(btn.toLowerCase().replace(' ', ''))
            }
            block="true"
          >
            {btn}
          </CButton>
        </CCol>
      ))}
    </CRow>
  );

  const renderWinterView = () => (
    <CContainer fluid className="p-0">
      <CRow>
        <CCol xs={12}>
          <CCard className="mb-4 bgr p-0">
            <CCardBody>
              <h2 className="text-center mb-4">
                System Map - {season === 0 ? 'Winter' : 'Summer'}
              </h2>
              <CRow className="mb-4">
                <CCol
                  xs={12}
                  md={6}
                  className="d-flex justify-content-md-end align-items-center mb-4 justify-content-center "
                >
                  <img
                    src={`images/Icons/Boiler/Boiler-${
                      manualOverride.boiler ? 'ON' : 'OFF'
                    }.png`}
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
                      {formatTemperature(sensors?.water_out_temp)}
                    </span>
                    <img
                      src="/images/Icons/Boiler/arrow3.png"
                      alt="Arrow"
                      className="mb-2 responsive-arrow"
                    />
                    <span className="h4 text-center">
                      {formatTemperature(sensors?.return_temp)}
                    </span>
                  </div>
                </CCol>
              </CRow>
              {renderButtons()}
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  );

  const renderSummerView = () => (
    <CContainer fluid>
      <CRow>
        <CCol>
          <CCard>
            <CCardBody className="pb-0">
              <CRow>
                {[...Array(4)].map((_, index) => (
                  <CCol
                    key={index}
                    xs={6}
                    md={3}
                    className="d-flex justify-content-center align-items-center"
                  >
                    <img
                      src={`images/Icons/Boiler/Chiller-${
                        manualOverride[`chiller${index + 1}`] ? 'ON' : 'OFF'
                      }.png`}
                      alt={`Chiller ${index + 1}`}
                      className="responsive-image"
                    />
                  </CCol>
                ))}
              </CRow>
              <CCol>
                <div className="d-flex mt-2 justify-content-center align-items-center mt-4">
                  <span className="h4 text-center ">
                    {formatTemperature(sensors?.water_out_temp)}
                  </span>
                  <div className="arrow-line"></div>
                  <span className="h4 text-center">
                    {formatTemperature(sensors?.return_temp)}
                  </span>
                  </div>
              </CCol>
              {renderButtons()}
            </CCardBody>
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
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  );

  const ModalComponent =
    modalContent && MODAL_CONTENTS[modalContent]?.component;

  return (
    <>
      {season === 0 ? renderWinterView() : renderSummerView()}

      <CModal
        alignment="center"
        visible={isModalOpen}
        onClose={closeModal}
        aria-labelledby="ModbusModal"
        className="modal-lg"
      >
        <CModalHeader>
          <CModalTitle>
            {modalContent && MODAL_CONTENTS[modalContent].title}
          </CModalTitle>
        </CModalHeader>
        <CModalBody>
          {ModalComponent && (
            <ModalComponent
              boiler={boiler}
              homedata={homedata}
              data={homedata}
            />
          )}
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
