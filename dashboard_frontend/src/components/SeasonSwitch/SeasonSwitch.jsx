import React, { useState, useEffect } from 'react';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';
import { CTooltip } from '@coreui/react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';
import { format, parseISO } from 'date-fns';
import { setSeason, setSystemStatus } from '../../features/state/seasonSlice';
import { switchSeason } from '../../api/switchSeason';
import './SeasonSwitch.css';

const SeasonSwitch = () => {
  const dispatch = useDispatch();
  const season = useSelector((state) => state.season.season);
  const [lockoutInfo, setLockoutInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [switchDirection, setSwitchDirection] = useState(null);

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
    try {
      const seasonValue = newSeason === 'Winter' ? 0 : 1;
      setSwitchDirection(newSeason === 'Winter' ? 'toWinter' : 'toSummer');

      const response = await switchSeason(seasonValue);

      if (response?.data?.status === 'success') {
        dispatch(setSeason(newSeason));
        dispatch(setSystemStatus('ONLINE'));
        toast.success(response.data.message);

        const unlockTime = parseISO(response.data.unlock_time);
        setLockoutInfo({
          lockoutTime: response.data.mode_switch_lockout_time,
          unlockTime: unlockTime,
        });
      }
    } catch (error) {
      dispatch(setSystemStatus('OFFLINE'));
      setSwitchDirection(null);
      toast.error(error?.response?.data?.message || 'Failed to switch season');
    }
  };

  return (
    <>
      <div className="season-toggle-header">
        <CTooltip
          content={
            lockoutInfo
              ? `Locked - ${countdown} remaining`
              : season === 'Winter'
              ? 'Currently in Winter mode'
              : 'Click to switch to Winter mode'
          }
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 'Winter' ? 'active' : ''} ${
              lockoutInfo ? 'locked' : ''
            }`}
            onClick={() => !lockoutInfo && handleSeasonChange('Winter')}
          >
            <span className="season-emoji">❄️</span>
            <span>Winter</span>
          </div>
        </CTooltip>

        <BsArrowRight
          className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
        />

        <CTooltip
          content={
            lockoutInfo
              ? `Locked - ${countdown} remaining`
              : season === 'Summer'
              ? 'Currently in Summer mode'
              : 'Click to switch to Summer mode'
          }
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 'Summer' ? 'active' : ''} ${
              lockoutInfo ? 'locked' : ''
            }`}
            onClick={() => !lockoutInfo && handleSeasonChange('Summer')}
          >
            <span className="season-emoji">☀️</span>
            <span>Summer</span>
          </div>
        </CTooltip>
      </div>

      {lockoutInfo && (
        <div className="season-switch-overlay">
          <div className="switch-message">
            <h3>
              Switching to{' '}
              {switchDirection === 'toWinter' ? 'Winter' : 'Summer'} Mode
            </h3>
            <p>Time remaining: {countdown}</p>
            <div className="lock-icon">🔒</div>
          </div>
        </div>
      )}
    </>
  );
};

export default SeasonSwitch;
