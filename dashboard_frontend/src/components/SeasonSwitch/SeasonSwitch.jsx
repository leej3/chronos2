import React, { useState, useEffect } from 'react';

import { CTooltip, CAlert } from '@coreui/react';
import { parseISO } from 'date-fns';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';

import { switchSeason } from '../../api/switchSeason';
import { setSeason, setSystemStatus, setManualOverride } from '../../features/state/seasonSlice';

import './SeasonSwitch.css';

const SeasonSwitch = () => {
  const dispatch = useDispatch();
  const season = useSelector((state) => state.chronos.season);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const manualOverride = useSelector((state) => state.chronos.manual_override);
  const [lockoutInfo, setLockoutInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [switchDirection, setSwitchDirection] = useState(null);
  const [alertColor, setAlertColor] = useState('danger');
  const [alertMessage, setAlertMessage] = useState('');
  const unlockTime = useSelector((state) => state.chronos.unlock_time);

  const winterTooltip = (lockoutInfo || manualOverride)
    ? `Locked${lockoutInfo ? ` - ${countdown} remaining` : ''}${manualOverride ? ' (Manual override active)' : ''}`
    : (season === 0 ? 'Currently in Winter mode' : 'Switch to Winter mode');

  const summerTooltip = (lockoutInfo || manualOverride)
    ? `Locked${lockoutInfo ? ` - ${countdown} remaining` : ''}${manualOverride ? ' (Manual override active)' : ''}`
    : (season === 1 ? 'Currently in Summer mode' : 'Switch to Summer mode');

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

    // Clear any previous manual override flag for a new switch attempt
    dispatch(setManualOverride(false));

    // Store previous season to revert if needed
    const previousSeason = season;

    // Determine numeric season value: 0 for Winter, 1 for Summer
    const seasonValue = newSeason === 'Winter' ? 0 : 1;

    // Optimistically update the UI immediately
    dispatch(setSeason(seasonValue));

    try {
      setSwitchDirection(newSeason === 'Winter' ? 'toWinter' : 'toSummer');

      const response = await switchSeason(seasonValue);

      // If API indicates success and no manual override issue, continue normally
      if (response?.data?.status === 'success' && !response?.data?.manual_override) {
        dispatch(setSystemStatus('ONLINE'));
        toast.success(response.data.message);

        if (response.data.unlock_time) {
          const unlockTime = parseISO(response.data.unlock_time);
          setLockoutInfo({ unlockTime });
          setSwitchDirection(null);
        }
      } else {
        // If success but manual_override flag is true or status is not 'success', then treat as failure
        toast.error(response?.data?.manual_override ? 'Relay toggle failed due to manual override.' : 'Season switch failed.');
        // Set manual override flag
        dispatch(setManualOverride(true));
        // Revert optimistic update
        dispatch(setSeason(previousSeason));
        setSwitchDirection(null);
      }
    } catch (error) {
      dispatch(setSystemStatus('OFFLINE'));
      toast.error(error?.message || 'Failed to switch season');
      setSwitchDirection(null);
      // Revert optimistic update and set manual override
      dispatch(setSeason(previousSeason));
      dispatch(setManualOverride(true));
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
          content={winterTooltip}
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 0 ? 'active disabled' : ''} ${(lockoutInfo || manualOverride) ? 'locked' : ''}`}
            onClick={() => { if (!lockoutInfo && !manualOverride && season !== 0) { handleSeasonChange('Winter'); }}}
            style={{ cursor: (lockoutInfo || manualOverride) ? 'not-allowed' : 'pointer', opacity: (lockoutInfo || manualOverride) ? 0.5 : 1 }}
          >
            <img
              src={`/images/Icons/WinterSummer/${season === 0 ? 'WOn' : 'WOff'}.png`}
              alt="Winter"
              className="season-icon-img"
            />
            <span>Winter</span>
            {lockoutInfo && <div className="lockout-indicator">{countdown}</div>}
          </div>
        </CTooltip>

        {season === 0 ? (
          <BsArrowRight className={`arrow-icon ${switchDirection ? 'switching' : ''}`} />
        ) : (
          <BsArrowLeft className={`arrow-icon ${switchDirection ? 'switching' : ''}`} />
        )}

        <CTooltip
          content={summerTooltip}
          placement="bottom"
        >
          <div
            className={`season-icon ${season === 1 ? 'active disabled' : ''} ${(lockoutInfo || manualOverride) ? 'locked' : ''}`}
            onClick={() => { if (!lockoutInfo && !manualOverride && season !== 1) { handleSeasonChange('Summer'); }}}
            style={{ cursor: (lockoutInfo || manualOverride) ? 'not-allowed' : 'pointer', opacity: (lockoutInfo || manualOverride) ? 0.5 : 1 }}
          >
            <img
              src={`/images/Icons/WinterSummer/${season === 1 ? 'SOn' : 'SOff'}.png`}
              alt="Summer"
              className="season-icon-img"
            />
            <span>Summer</span>
            {lockoutInfo && <div className="lockout-indicator">{countdown}</div>}
          </div>
        </CTooltip>
      </div>
    </>
  );
};

export default SeasonSwitch;
