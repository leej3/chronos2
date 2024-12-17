import React, { useState, useEffect } from 'react';
import { FaSun, FaSnowflake } from 'react-icons/fa';
import "./nav.css";
import { useSelector, useDispatch } from 'react-redux';
import { setSeason } from '../../features/state/seasonSlice';
import { API_BASE_URL } from '../../utils/constant';

const Navbar = () => {
  const season = useSelector((state) => state.season.season);
  const dispatch = useDispatch();
  
  const [countdown, setCountdown] = useState(null);
  const [isSwitching, setIsSwitching] = useState(false); 
  const [isTimerOn, setIsTimeron] = useState(false); 
  const [nextMode, setNextMode] = useState(null);

  const switchSeason = (newMode) => {
    setIsSwitching(true);

    fetch(`${API_BASE_URL}/switch_mode`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ mode: newMode }),
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log('Mode switched:', data);
        startCountdown();

        setNextMode(newMode);
      } else {
        console.error("Error: Mode switching is restricted.");
      }

      setIsSwitching(false);
    })
    .catch(error => {
      console.error('Error switching mode:', error);
      setIsSwitching(false);
    });
  };

  const startCountdown = () => {
    setIsTimeron(true);
    setCountdown(121);
  };

  useEffect(() => {
    if (countdown !== null && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0 && nextMode !== null) {
     
      setCountdown(null);
      setIsTimeron(false);
      setNextMode(null);
        if (nextMode === 2) { // TO_WINTER
          dispatch(setSeason('Winter'));
        } else if (nextMode === 3) { 
          dispatch(setSeason('Summer'));
        } else {
          dispatch(setSeason('Default'));
        }
  
    }
  }, [countdown, dispatch, nextMode]);

  return (
    <>
      {isSwitching && (
        <div className="overlay">
          <div className="message">
            Please wait...
          </div>
        </div>
      )}
      <div className={`nav ${isSwitching ? 'blurred' : ''}`}>
        <div className="left">
          <h2>Chronos</h2>
          {countdown !== null && (
            <h3>Mode switching in: {Math.floor(countdown / 60)}:{('0' + countdown % 60).slice(-2)} minutes</h3>
          )}
        </div>
        <div className="middle">
          <h3>--- {season} ---</h3>
        </div>
        <div className="right">
          <span 
            className={`seasonNicon ${isTimerOn ? 'disabled' : ''}`} 
            onClick={!isTimerOn ? () => { switchSeason(2); } : null} // TO_WINTER
          >
            <FaSnowflake className="icon" />
            Winter
          </span>
          <span 
            className={`seasonNicon ${isTimerOn ? 'disabled' : ''}`} 
            onClick={!isTimerOn ? () => { switchSeason(3); } : null} // TO_SUMMER
          >
            <FaSun className="icon" />
            Summer
          </span>
        </div>
      </div>
    </>
  );
};

export default Navbar;
