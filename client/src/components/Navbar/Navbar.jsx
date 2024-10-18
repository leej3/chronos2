import React, { useState, useEffect } from 'react';
import { FaSun, FaSnowflake } from 'react-icons/fa';
import "./nav.css";
import { useSelector, useDispatch } from 'react-redux';
import { setSeason } from '../../features/state/seasonSlice';

const Navbar = () => {
  const season = useSelector((state) => state.season.season);
  const dispatch = useDispatch();
  
  const [countdown, setCountdown] = useState(null); // State for countdown timer
  const [isSwitching, setIsSwitching] = useState(false); // State for blurring and showing "Please wait..."

  const switchSeason = (newMode, season) => {
    setIsSwitching(true); // Start the blur effect and show the message
    fetch('http://localhost:80/switch_mode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ mode: newMode }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Mode switched:', data);
      startCountdown(); // Start countdown when API response is received
      season === 0 ? dispatch(setSeason('Winter')) : season === 1 ? dispatch(setSeason('Summer')) : dispatch(setSeason('Default'));
      setIsSwitching(false); // Stop the blur effect
    })
    .catch(error => {
      console.error('Error switching mode:', error);
      setIsSwitching(false); // Stop the blur effect if there's an error
    });
  };

  const startCountdown = () => {
    setCountdown(120); // Start the countdown from 120 seconds (2 minutes)
  };

  useEffect(() => {
    if (countdown !== null && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0) {
      setCountdown(null); // Reset countdown when it reaches 0
    }
  }, [countdown]);

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
            className="seasonNicon" 
            onClick={() => {switchSeason(3, 0)}} // 3 is the code for winter, second param 0 is for Winter
          >
            <FaSnowflake className="icon" />
            Winter
          </span>
          <span 
            className="seasonNicon" 
            onClick={() => {switchSeason(2, 1)}} // 2 is the code for summer, 1 for Summer
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
