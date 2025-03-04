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

const SeasonSwitch = ({ season_mode }) => {
  const dispatch = useDispatch();
  const readOnlyMode = useSelector((state) => state.chronos.read_only_mode);
  const unlockTime = useSelector((state) => state.chronos.unlock_time);
  const isSwitchingSeason = useSelector(
    (state) => state.chronos.is_switching_season,
  );
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
      setSwitchDirection(`to${newSeason}`);
      setIsAnimating(true);
      await switchSeason(newSeason);
      dispatch(fetchData());
    } catch (error) {
      setAlertState({
        color: 'danger',
        message: error?.response?.data?.message || 'Error switching season',
      });
      resetStates();
    }
  };

  const getSeasonClassName = (seasonMode) => {
    const isCurrentSeason = seasonMode === season_mode;
    return [
      'season-icon',
      isCurrentSeason ? 'active disabled' : '',
      unlockTime ? 'locked' : '',
      switchDirection === `to${seasonMode}`
        ? `switching-${seasonMode.toLowerCase()}`
        : '',
    ]
      .filter(Boolean)
      .join(' ');
  };

  const getSeasonImage = (seasonMode) => {
    if (
      seasonMode === 'winter' &&
      !isSwitchingSeason &&
      season_mode === 'winter'
    ) {
      return '/images/Icons/WinterSummer/WOn.png';
    }

    if (
      seasonMode === 'summer' &&
      !isSwitchingSeason &&
      season_mode === 'summer'
    ) {
      return '/images/Icons/WinterSummer/SOn.png';
    }

    if (isSwitchingSeason) {
      if (seasonMode === 'winter' && season_mode === 'summer') {
        return '/images/Icons/WinterSummer/WOn.png';
      }

      if (seasonMode === 'summer' && season_mode === 'winter') {
        return '/images/Icons/WinterSummer/SOn.png';
      }
    }

    return `/images/Icons/WinterSummer/${
      seasonMode === 'winter' ? 'WOff' : 'SOff'
    }.png`;
  };

  const getTooltipContent = (seasonMode) => {
    if (unlockTime && countdown) {
      return `Locked - ${countdown} remaining`;
    }

    const isCurrentSeason = seasonMode === season_mode;
    if (isCurrentSeason) {
      return `Currently in ${seasonMode} mode`;
    }

    if (isAnimating) {
      return `Switching to ${seasonMode} mode...`;
    }

    return `Click to switch to ${seasonMode} mode`;
  };

  const renderSeasonButton = (seasonMode) => (
    <CTooltip content={getTooltipContent(seasonMode)} placement="bottom">
      <div
        className={getSeasonClassName(seasonMode)}
        onClick={() => {
          const canSwitch =
            !unlockTime && !isAnimating && seasonMode !== season_mode;
          if (canSwitch) handleSeasonChange(seasonMode);
        }}
      >
        <img
          src={getSeasonImage(seasonMode)}
          alt={seasonMode}
          className="season-icon-img"
        />
        <span>{seasonMode}</span>
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
        {renderSeasonButton('winter')}

        {((season_mode === 'winter' && isSwitchingSeason) ||
          (season_mode === 'summer' && !isSwitchingSeason)) && (
          <BsArrowLeft
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        )}

        {((season_mode === 'winter' && !isSwitchingSeason) ||
          (season_mode === 'summer' && isSwitchingSeason)) && (
          <BsArrowRight
            className={`arrow-icon ${switchDirection ? 'switching' : ''}`}
          />
        )}

        {renderSeasonButton('summer')}
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
