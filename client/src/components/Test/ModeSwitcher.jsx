import React, { useEffect, useState } from "react";
import io from "socket.io-client";

const socket = io("http://localhost"); // Replace with your server URL

const ModeSwitcher = () => {
    const [mode, setMode] = useState(null);
    const [data, setData] = useState({});

    // useEffect(() => {
    //     // Listening for 'misc' event from socket
    //     socket.on("backend", (receivedData) => {
    //         setData((prevData) => ({
    //             ...prevData,
    //             ...receivedData,
    //         }));

    //         if (receivedData.mode !== undefined) {
    //             switchSeason(receivedData.mode);
    //         }
    //     });

    //     return () => {
    //         socket.off("misc");
    //     };
    // }, []);

    // const switchSeason = (mode) => {
    //     const parsedMode = parseInt(mode, 10);
    //     setMode(parsedMode);

    //     switch (parsedMode) {
    //         case 0:
    //             handleSeasonChange("Winter mode", "WOn.png", [0, 1, 2], "Switching to winter mode in ");
    //             break;
    //         case 1:
    //             handleSeasonChange("Summer mode", "SOn.png", [3, 4, 5], "Switching to summer mode in ");
    //             break;
    //         case 2:
    //             setSeasonSwitchState("WOff.png", "SOff.png", "Chiller-OFF.png", "Switching to winter mode in ");
    //             break;
    //         case 3:
    //             setSeasonSwitchState("WOff.png", "SOff.png", "Boiler-OFF.png", "Switching to summer mode in ");
    //             break;
    //         default:
    //             break;
    //     }
    // };

    // const handleSeasonChange = (headerText, statusImage, radioIndices, timerText) => {
    //     // Example of handling UI updates; replace with your own logic
    //     document.getElementById("mode-header").textContent = headerText;
    //     document.getElementById("winterStatus").src = `static/images/Icons/WinterSummer/${statusImage}`;
    //     // Enable or disable radio buttons
    //     const radios = document.querySelectorAll(":radio");
    //     radios.forEach((radio, index) => {
    //         radio.disabled = !radioIndices.includes(index);
    //     });
    //     // Update system map, stats, and form (replace with actual data)
    // };

    // const setSeasonSwitchState = (winterStatus, summerStatus, chillerOrBoilerStatus, headerText) => {
    //     document.getElementById("mode-header").textContent = headerText;
    //     document.getElementById("winterStatus").src = `static/images/Icons/WinterSummer/${winterStatus}`;
    //     document.getElementById("summerStatus").src = `static/images/Icons/WinterSummer/${summerStatus}`;
    //     document.querySelectorAll("img[id^='chillerStatus'], #boilerStatus").forEach(img => {
    //         img.src = `static/images/Icons/Boiler/${chillerOrBoilerStatus}`;
    //     });
    //     // Disable all radio buttons
    //     document.querySelectorAll(":radio").forEach(radio => {
    //         radio.disabled = true;
    //     });
    // };

    // Rendering the component
    return (
        <div>
            {/* <h1 id="mode-header">Mode: {mode !== null ? mode : "Not set"}</h1>
            <div id="timer"></div>
            <img id="winterStatus" alt="Winter Status" />
            <img id="summerStatus" alt="Summer Status" /> */}
            {/* Add more elements as per your requirement */}
        </div>
    );
};

export default ModeSwitcher;
