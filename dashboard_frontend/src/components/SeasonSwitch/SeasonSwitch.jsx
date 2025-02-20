import React, { useState, useEffect } from 'react';
import { BsArrowRight, BsArrowLeft } from 'react-icons/bs';
import { CTooltip, CAlert } from '@coreui/react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';
import { format, parseISO } from 'date-fns';
import { switchSeason } from '../../api/switchSeason';
import { fetchData } from '../../features/chronos/chronosSlice';
import './SeasonSwitch.css';
import { SEASON_MODE } from '../../utils/constant';

const SeasonSwitch = () => {
  const dispatch = useDispatch();
  const season = useSelector((state) => state.chronos.season);
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const unlockTime = useSelector((state) => state.chronos.unlock_time);

  const [countdown, setCountdown] = useState(null);
  const [switchDirection, setSwitchDirection] = useState(null);
  const [alertState, setAlertState] = useState({ color: '', message: '' });
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (!unlockTime) {
      resetStates();
      return;
    }

    const updateCountdown = () => {
      const timeRemaining =
        parseISO(unlockTime).getTime() - new Date().getTime();

      if (timeRemaining <= 0) {
        resetStates();
        return;
      }

      const minutes = Math.floor(timeRemaining / 1000 / 60);
      const seconds = Math.floor((timeRemaining / 1000) % 60);
      setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
    };

    const timer = setInterval(updateCountdown, 1000);
    updateCountdown();

    return () => clearInterval(timer);
  }, [unlockTime]);

  const resetStates = () => {
    setCountdown(null);
    setSwitchDirection(null);
    setIsAnimating(false);
  };

  const handleSeasonChange = async (newSeason) => {
    if (readOnlyMode) {
      setAlertState({ color: 'warning', message: 'You are in read only mode' });
      return;
    }

    if (isAnimating) return;

    try {
      const seasonValue = newSeason === 'Winter' ? 0 : 1;
      setSwitchDirection(`to${newSeason}`);
      setIsAnimating(true);

      await switchSeason(seasonValue);
      dispatch(fetchData());
    } catch (error) {
      resetStates();
    }
  };

  const getSeasonClassName = (seasonType) => {
    const isActive = season === (seasonType === 'Winter' ? 0 : 1);
    return [
      'season-icon',
      isActive ? 'active disabled' : '',
      unlockTime ? 'locked' : '',
      switchDirection === `to${seasonType}`
        ? `switching-${seasonType.toLowerCase()}`
        : '',
    ]
      .filter(Boolean)
      .join(' ');
  };

  const getSeasonImage = (seasonType) => {
    const isWinter = seasonType === 'Winter';
    const isWinterMode =
      season === SEASON_MODE.WINTER ||
      season === SEASON_MODE.WAITING_SWITCH_TO_SUMMER ||
      season === SEASON_MODE.SWITCHING_TO_SUMMER;

    return `/images/Icons/WinterSummer/${
      (isWinter && isWinterMode) || (!isWinter && !isWinterMode)
        ? `${isWinter ? 'W' : 'S'}On`
        : `${isWinter ? 'W' : 'S'}Off`
    }.png`;
  };

  const getTooltipContent = (seasonType) => {
    if (unlockTime && countdown) return `Locked - ${countdown} remaining`;
    const isCurrentSeason = season === (seasonType === 'Winter' ? 0 : 1);
    return isCurrentSeason
      ? `Currently in ${seasonType} mode`
      : `Switch to ${seasonType} mode`;
  };

  const renderSeasonButton = (seasonType) => (
    <CTooltip content={getTooltipContent(seasonType)} placement="bottom">
      <div
        className={getSeasonClassName(seasonType)}
        onClick={() => {
          const canSwitch =
            !unlockTime &&
            !isAnimating &&
            season !== (seasonType === 'Winter' ? 0 : 1);
          if (canSwitch) handleSeasonChange(seasonType);
        }}
      >
        <img
          src={getSeasonImage(seasonType)}
          alt={seasonType}
          className="season-icon-img"
        />
        <span>{seasonType}</span>
      </div>
    </CTooltip>
  );

  return (
    <>
      {alertState.message && (
        <CAlert
          className="m-0 text-center"
          color={alertState.color}
          dismissible
          onClose={() => setAlertState({ color: '', message: '' })}
        >
          <strong>
            {alertState.color === 'danger' ? 'Error!' : 'Warning!'}
          </strong>{' '}
          {alertState.message}
        </CAlert>
      )}

      <div className="season-toggle-header">
        {renderSeasonButton('Winter')}

        {season === SEASON_MODE.WINTER ||
        season === SEASON_MODE.WAITING_SWITCH_TO_SUMMER ||
        season === SEASON_MODE.SWITCHING_TO_SUMMER ? (
          <BsArrowRight
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        ) : (
          <BsArrowLeft
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        )}

        {renderSeasonButton('Summer')}
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
