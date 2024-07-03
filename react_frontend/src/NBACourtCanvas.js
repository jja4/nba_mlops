import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import nbaLogo from './nba_logo.png';



const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function getToken(username, password) {
  const loginData = new URLSearchParams({
    grant_type: '',
    username: username,
    password: password,
    scope: '',
    client_id: '',
    client_secret: ''
  });

  try {
    const response = await axios.post(`${API_URL}/login`, loginData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json'
      }
    });
    return response.data.access_token;
  } catch (error) {
    console.error('Error during login:', error.response ? error.response.data : error.message);
    throw error;
  }
}

const NBACourtCanvas = () => {
  const [token, setToken] = useState(null);
  const [coordinates, setCoordinates] = useState({ x: 0, y: 0 });
  const [selectedPlayer, setSelectedPlayer] = useState('Stephen Curry');
  const canvasRef = useRef(null);

  
  // List of NBA player names
  const playerNames = [
    'LeBron James',
    'Stephen Curry',
    'Kevin Durant',
    'Giannis Antetokounmpo',
    'James Harden',
    'Kawhi Leonard',
    'Luka Doncic',
    'Damian Lillard',
    'Kyrie Irving',
    'Joel Embiid',
    'Nikola Jokic',
    'Jayson Tatum',
    'Devin Booker',
    'Trae Young',
    'Donovan Mitchell',
    'Zion Williamson',
    'Ja Morant',
    'Bam Adebayo',
    'Jaylen Brown',
    'Domantas Sabonis',
  ];

  useEffect(() => {

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Load the background image
    const img = new Image();
    img.onload = () => {
      const scaleX = canvas.width / img.width;
      const scaleY = canvas.height / img.height;

      // Maintain aspect ratio while fitting the image within the canvas
      const scale = Math.min(scaleX, scaleY);
      const imageWidth = img.width * scale;
      const imageHeight = img.height * scale;

      // Center the image on the canvas
      const xOffset = (canvas.width - imageWidth) / 2;
      const yOffset = (canvas.height - imageHeight) / 2;

      ctx.drawImage(img, xOffset, yOffset, imageWidth, imageHeight);
    };
    img.src = '/basketball_court.jpg';
  }, []);

  const handleLogin = async () => {
    try {
      const accessToken = await getToken('johndoe', 'secret');
      setToken(accessToken);
      console.log('Login successful');
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      console.log('Login finished');
    }
  };

  useEffect(() => {
    handleLogin();
  }, []);

  const handleClick = (e) => {
    // if (!token) {
    //   console.error('No token available. Please login first.');
    //   return;
    // }

    const rect = canvasRef.current.getBoundingClientRect();
  
    // Adjust click coordinates based on the desired range (-250 to 250, -50 to 900)
    const x = ((e.clientX - rect.left) / canvasRef.current.width) * 500 - 250;
    const y = -((e.clientY - rect.top) / canvasRef.current.height) * 950 + 900;
  
    setCoordinates({ x, y });
  
    

    const data = {
      Period: -0.4,
      Minutes_Remaining: 1.4,
      Seconds_Remaining: -1.3,
      Shot_Distance: 0.3,
      X_Location: x/100,
      Y_Location: y/100,
      Action_Type_Frequency: 0.5,
      Team_Name_Frequency: 0.5,
      Home_Team_Frequency: 0.4,
      Away_Team_Frequency: 0.6,
      ShotType_2PT_Field_Goal: 1,
      ShotType_3PT_Field_Goal: 0,
      ShotZoneBasic_Above_the_Break_3: 0,
      ShotZoneBasic_Backcourt: 0,
      ShotZoneBasic_In_The_Paint_Non_RA: 0,
      ShotZoneBasic_Left_Corner_3: 0,
      ShotZoneBasic_Mid_Range: 0,
      ShotZoneBasic_Restricted_Area: 1,
      ShotZoneBasic_Right_Corner_3: 0,
      ShotZoneArea_Back_Court_BC: 1,
      ShotZoneArea_Center_C: 0,
      ShotZoneArea_Left_Side_Center_LC: 0,
      ShotZoneArea_Left_Side_L: 0,
      ShotZoneArea_Right_Side_Center_RC: 1,
      ShotZoneArea_Right_Side_R: 0,
      ShotZoneRange_16_24_ft: 0,
      ShotZoneRange_24_ft: 1,
      ShotZoneRange_8_16_ft: 0,
      ShotZoneRange_Back_Court_Shot: 1,
      ShotZoneRange_Less_Than_8_ft: 0,
      SeasonType_Playoffs: 1,
      SeasonType_Regular_Season: 0,
      Game_ID_Frequency: 0.8,
      Game_Event_ID_Frequency: 0.7,
      Player_ID_Frequency: 0.9,
      Year: 2022,
      Month: 6,
      Day: 11,
      Day_of_Week: 5
      }
  
    // Convert data object to JSON
    const jsonData = JSON.stringify(data);
  
    // Send coordinates to the FastAPI backend
    axios
      .post(`${API_URL}/predict`, jsonData, {
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
      .then((response) => {
        // Handle the response from the backend
        const prediction = response.data.prediction;
        const predictionText = prediction === 1 ? 'Make' : 'Miss';
        console.log(`Prediction: ${predictionText}`);

        // Check if a prediction element already exists
        const existingPredictionElement = document.querySelector('.prediction-element');

        if (existingPredictionElement) {
          // Update the existing prediction element's text content
          existingPredictionElement.textContent = `Prediction: ${predictionText}`;
        } else {
          // Create a new prediction element
          const predictionElement = document.createElement('p');
          predictionElement.classList.add('prediction-element'); // Add a class for easy selection
          predictionElement.style.fontWeight = 'bold';
          predictionElement.textContent = `Prediction: ${predictionText}`;

          // Insert the new prediction element beneath the Selected Coordinates line
          const coordinatesElement = document.querySelector('p:last-child');
          coordinatesElement.parentNode.insertBefore(predictionElement, coordinatesElement.nextSibling);
        }
      })
      .catch((error) => {
        console.error('Error:', error);
  
        let errorMessage = 'An error occurred';
  
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          if (error.response.status === 401) {
            errorMessage = 'Not Authorized';
          } else {
            errorMessage = `Error: ${error.response.status} ${error.response.statusText}`;
          }
        } else if (error.request) {
          // The request was made but no response was received
          errorMessage = 'No response received from server';
        } else {
          // Something happened in setting up the request that triggered an Error
          errorMessage = error.message;
        }
  
        // Display the error message
        const existingPredictionElement = document.querySelector('.prediction-element');
  
        if (existingPredictionElement) {
          // Update the existing prediction element's text content
          existingPredictionElement.textContent = errorMessage;
        } else {
          // Create a new prediction element
          const predictionElement = document.createElement('p');
          predictionElement.classList.add('prediction-element');
          predictionElement.style.fontWeight = 'bold';
          predictionElement.style.color = 'red';  // Make error messages red
          predictionElement.textContent = errorMessage;
  
          // Insert the new prediction element beneath the Selected Coordinates line
          const coordinatesElement = document.querySelector('p:last-child');
          coordinatesElement.parentNode.insertBefore(predictionElement, coordinatesElement.nextSibling);
        }
      });
  };

  const handlePlayerSelect = (player) => {
    setSelectedPlayer(player);
  };

  // const getPlayerIndex = (player) => {
  //   return playerNames.indexOf(player);
  // };


  return (
<div style={{ display: 'flex', marginTop: '50px', justifyContent: 'center', alignItems: 'center' }}>
  <div style={{ marginRight: '20px', maxWidth: '200px' }}>
    <img src={nbaLogo} alt="NBA Logo" style={{ width: '100%', marginBottom: '2px' }} />
    <h2 style={{ textAlign: 'center' }}>NBA MLOps</h2>
    <p style={{ 
      wordWrap: 'break-word', 
      overflowWrap: 'break-word', 
      textAlign: 'left' 
    }}>
      Pick a spot on the court and find out if an NBA player would make that shot on the lower basket
    </p>
  </div>
      <div style={{ marginRight: '20px' }}>
        <canvas
          ref={canvasRef}
          width={250 * 0.85}
          height={375 * 0.85}
          style={{ border: '2px solid black' }}
          onClick={handleClick}
        />
      </div>
      <div>
        <h3>Select a Player</h3>
        <div style={{ display: 'flex' }}>
          <div>
            {playerNames.slice(0, 10).map((name) => (
              <div key={name}>
                <label>
                  <input
                    type="radio"
                    name="player"
                    value={name}
                    checked={selectedPlayer === name}
                    onChange={() => handlePlayerSelect(name)}
                  />
                  {name}
                </label>
              </div>
            ))}
          </div>
          <div style={{ marginLeft: '20px' }}>
            {playerNames.slice(10).map((name) => (
              <div key={name}>
                <label>
                  <input
                    type="radio"
                    name="player"
                    value={name}
                    checked={selectedPlayer === name}
                    onChange={() => handlePlayerSelect(name)}
                  />
                  {name}
                </label>
              </div>
            ))}
          </div>
        </div>
        {selectedPlayer && <p>Selected Player: {selectedPlayer}</p>}
        <p>Selected Coordinates: ({coordinates.x.toFixed(2)}, {coordinates.y.toFixed(2)})</p>
      </div>
    </div>
  );
};

export default NBACourtCanvas;
