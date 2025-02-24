import React, { useState, useEffect } from 'react';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';
import { CTooltip, CAlert } from '@coreui/react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';
import { format, parseISO } from 'date-fns';
import { switchSeason } from '../../api/switchSeason';
import { fetchData } from '../../features/chronos/chronosSlice';
import './SeasonSwitch.css';

const SeasonSwitch = () => {
  const dispatch = useDispatch();
  const season = useSelector((state) => state.chronos.season);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const unlockTime = useSelector((state) => state.chronos.unlock_time);
  const [countdown, setCountdown] = useState(null);
  const [switchDirection, setSwitchDirection] = useState(null);
  const [alertColor, setAlertColor] = useState('danger');
  const [alertMessage, setAlertMessage] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    let timer;
    if (unlockTime) {
      const updateCountdown = () => {
        const unlockTimeDate = parseISO(unlockTime);
        const now = new Date();
        const diff = unlockTimeDate.getTime() - now.getTime();

        if (diff <= 0) {
          setCountdown(null);
          setSwitchDirection(null);
          setIsAnimating(false);
          clearInterval(timer);
        } else {
          const minutes = Math.floor(diff / 1000 / 60);
          const seconds = Math.floor((diff / 1000) % 60);
          setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
        }
      };

      updateCountdown();
      timer = setInterval(updateCountdown, 1000);
    } else {
      setCountdown(null);
      setSwitchDirection(null);
      setIsAnimating(false);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [unlockTime]);

  const handleSeasonChange = async (newSeason) => {
    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }

    if (readOnlyMode) {
      setAlertColor('warning');
      setAlertMessage('You are in read only mode');
      return;
    }

    if (isAnimating) return;

    try {
      const seasonValue = newSeason === 'Winter' ? 0 : 1;
      setSwitchDirection(newSeason === 'Winter' ? 'toWinter' : 'toSummer');
      setIsAnimating(true);

      await switchSeason(seasonValue);
      dispatch(fetchData());
    } catch (error) {
      setSwitchDirection(null);
      setIsAnimating(false);
    }
  };

  const getSeasonClassName = (seasonType) => {
    const baseClass = 'season-icon';
    const classes = [
      baseClass,
      season === (seasonType === 'Winter' ? 0 : 1) ? 'active disabled' : '',
      unlockTime ? 'locked' : '',
      switchDirection === `to${seasonType}`
        ? `switching-${seasonType.toLowerCase()}`
        : '',
    ];
    return classes.filter(Boolean).join(' ');
  };

  return (
    <>
      {alertMessage && (
        <CAlert
          className="m-0 text-center"
          color={alertColor}
          dismissible
          onClose={() => setAlertMessage('')}
        >
          <strong>{alertColor === 'danger' ? 'Error!' : 'Warning!'}</strong>{' '}
          {alertMessage}
        </CAlert>
      )}
      <div className="season-toggle-header">
        <CTooltip
          content={
            unlockTime && countdown
              ? `Locked - ${countdown} remaining`
              : season === 0
              ? 'Currently in Winter mode'
              : 'Switch to Winter mode'
          }
          placement="bottom"
        >
          <div
            className={getSeasonClassName('Winter')}
            onClick={() =>
              !unlockTime &&
              !isAnimating &&
              season !== 0 &&
              handleSeasonChange('Winter')
            }
          >
            <img
              src={`/images/Icons/WinterSummer/${
                season === 0 || season === 3 || season === 5 ? 'WOn' : 'WOff'
              }.png`}
              alt="Winter"
              className="season-icon-img"
            />
            <span>Winter</span>
          </div>
        </CTooltip>

        {season === 0 || season === 3 || season === 5 ? (
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
            unlockTime && countdown
              ? `Locked - ${countdown} remaining`
              : season === 1
              ? 'Currently in Summer mode'
              : 'Switch to Summer mode'
          }
          placement="bottom"
        >
          <div
            className={getSeasonClassName('Summer')}
            onClick={() =>
              !unlockTime &&
              !isAnimating &&
              season !== 1 &&
              handleSeasonChange('Summer')
            }
          >
            <img
              src={`/images/Icons/WinterSummer/${
                season === 1 || season === 2 || season === 4 ? 'SOn' : 'SOff'
              }.png`}
              alt="Summer"
              className="season-icon-img"
            />
            <span>Summer</span>
          </div>
        </CTooltip>
      </div>

      {unlockTime && countdown && (
        <div className="countdown-message text-center mt-2">
          <span className="text-warning">
            System locked - {countdown} remaining
          </span>
        </div>
      )}
    </>
  );
};

export default SeasonSwitch;
