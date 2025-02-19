import React, { useState, useEffect } from 'react';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';
import { CTooltip } from '@coreui/react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';
import { format, parseISO } from 'date-fns';
import { setSeason, setSystemStatus } from '../../features/state/seasonSlice';
import { switchSeason } from '../../api/switchSeason';
import { CAlert } from '@coreui/react';
import './SeasonSwitch.css';

const SeasonSwitch = () => {
  const dispatch = useDispatch();
  const season = useSelector((state) => state.chronos.season);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const [lockoutInfo, setLockoutInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [switchDirection, setSwitchDirection] = useState(null);
  const [alertColor, setAlertColor] = useState('danger');
  const [alertMessage, setAlertMessage] = useState('');
  const unlockTime = useSelector((state) => state.chronos.unlock_time);

  useEffect(() => {
    if (unlockTime) {
      const unlockTimeDate = parseISO(unlockTime);
      const now = new Date();
      if (unlockTimeDate > now) {
        setLockoutInfo({
          unlockTime: unlockTimeDate,
        });
      } else {
        setLockoutInfo(null);
      }
    } else {
      setLockoutInfo(null);
    }
  }, [unlockTime]);

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

  const handleSeasonChange = async (newSeason) => {
    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }
    try {
      const seasonValue = newSeason === 'Winter' ? 0 : 1;
      setSwitchDirection(newSeason === 'Winter' ? 'toWinter' : 'toSummer');

      const response = await switchSeason(seasonValue);

      if (response?.data?.status === 'success') {
        dispatch(setSeason(newSeason));
        dispatch(setSystemStatus('ONLINE'));
        toast.success(response.data.message);

        if (response.data.unlock_time) {
          const unlockTime = parseISO(response.data.unlock_time);
          setLockoutInfo({
            unlockTime: unlockTime,
          });
          setSwitchDirection(null);
        }
      }
    } catch (error) {
      dispatch(setSystemStatus('OFFLINE'));
      setSwitchDirection(null);
      toast.error(error?.message || 'Failed to switch season');
    }
  };

  return (
    <>
      {alertMessage && (
        <CAlert
          className="mb-0 text-center"
          color={alertColor}
          dismissible
          onClose={() => {
            setAlertMessage('');
            setAlertColor('danger');
          }}
        >
          {alertColor === 'warning' ? (
            alertMessage
          ) : (
            <>
              <strong>Error!</strong> {alertMessage}
            </>
          )}
        </CAlert>
      )}
      <div className="season-toggle-header">
        <CTooltip
          content={
            lockoutInfo
              ? `Locked - ${countdown} remaining`
              : season === 0
              ? 'Currently in Winter mode'
              : 'Switch to Winter mode'
          }
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 0 ? 'active disabled' : ''} ${
              lockoutInfo ? 'locked' : ''
            }`}
            onClick={() =>
              !lockoutInfo && season !== 0 && handleSeasonChange('Winter')
            }
          >
            <img
              src={`/images/Icons/WinterSummer/${
                season === 0 ? 'WOn' : 'WOff'
              }.png`}
              alt="Winter"
              className="season-icon-img"
            />
            <span>Winter</span>
          </div>
        </CTooltip>

        {season === 0 ? (
          <BsArrowRight
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        ) : (
          <BsArrowLeft
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        )}

        <CTooltip
          content={
            lockoutInfo
              ? `Locked - ${countdown} remaining`
              : season === 1
              ? 'Currently in Summer mode'
              : 'Switch to Summer mode'
          }
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 1 ? 'active disabled' : ''} ${
              lockoutInfo ? 'locked' : ''
            }`}
            onClick={() =>
              !lockoutInfo && season !== 1 && handleSeasonChange('Summer')
            }
          >
            <img
              src={`/images/Icons/WinterSummer/${
                season === 1 ? 'SOn' : 'SOff'
              }.png`}
              alt="Summer"
              className="season-icon-img"
            />
            <span>Summer</span>
          </div>
        </CTooltip>
      </div>

      {lockoutInfo && (
        <div className="season-switch-overlay">
          <div className="switch-message">
            <h3>System Locked</h3>
            <p>Time remaining until next switch: {countdown}</p>
            <div className="lock-icon">🔒</div>
          </div>
        </div>
      )}
    </>
  );
};

export default SeasonSwitch;
