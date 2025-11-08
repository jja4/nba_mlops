import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const NBACourtCanvas = () => {
  const [coordinates, setCoordinates] = useState({ x: 0, y: 0 });
  const [selectedPlayer, setSelectedPlayer] = useState('');
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

    // Set line width and colors
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#000000'; // Black
    ctx.fillStyle = '#ff6600'; // Orange

    // Center circle
    ctx.beginPath();
    ctx.lineWidth = 5;
    ctx.arc(400, 200, 50, 0, 2 * Math.PI, true);
    ctx.stroke();
    ctx.fill();
    ctx.closePath();

    // Center line
    ctx.beginPath();
    ctx.moveTo(400, 0);
    ctx.lineTo(400, 400);
    ctx.stroke();
    ctx.closePath();

    // Left semi-circle
    ctx.beginPath();
    ctx.arc(150, 200, 50, Math.PI / 2, 3 * Math.PI / 2, true);
    ctx.stroke();
    ctx.closePath();

    // Right semi-circle
    ctx.beginPath();
    ctx.arc(650, 200, 50, 3 * Math.PI / 2, Math.PI / 2, true);
    ctx.stroke();
    ctx.closePath();

    // Left three-point line
    ctx.beginPath();
    ctx.arc(50, 200, 180, Math.PI / 2, 3 * Math.PI / 2, true);
    ctx.stroke();
    ctx.closePath();

    // Right three-point line
    ctx.beginPath();
    ctx.arc(746, 200, 180, Math.PI / 2, 3 * Math.PI / 2, false);
    ctx.stroke();
    ctx.closePath();

    // Lines from three-point lines to corners
    ctx.beginPath();
    ctx.moveTo(750, 380);
    ctx.lineTo(800, 380);
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(750, 20);
    ctx.lineTo(800, 20);
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(0, 380);
    ctx.lineTo(50, 380);
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(0, 20);
    ctx.lineTo(50, 20);
    ctx.stroke();
    ctx.closePath();

    // Left rectangles
    ctx.strokeRect(-1, 150, 150, 100);
    ctx.strokeRect(-1, 130, 150, 140);
    ctx.fillRect(-2, 151, 149, 98);

    // Right rectangles
    ctx.strokeRect(650, 150, 151, 100);
    ctx.strokeRect(650, 130, 151, 140);
    ctx.fillRect(652, 151, 149, 98);

    // Left vertical line
    ctx.beginPath();
    ctx.moveTo(40, 175);
    ctx.lineTo(40, 225);
    ctx.stroke();
    ctx.closePath();

    // Left horizontal line
    ctx.beginPath();
    ctx.moveTo(40, 200);
    ctx.lineTo(50, 200);
    ctx.stroke();
    ctx.closePath();

    // Left filled circle
    ctx.beginPath();
    ctx.arc(53, 200, 5, 0, Math.PI * 2, true);
    ctx.stroke();
    ctx.fill();
    ctx.closePath();

    // Right filled circle
    ctx.beginPath();
    ctx.arc(747, 200, 5, 0, Math.PI * 2, true);
    ctx.stroke();
    ctx.fill();
    ctx.closePath();

    // Right vertical line
    ctx.beginPath();
    ctx.moveTo(760, 175);
    ctx.lineTo(760, 225);
    ctx.stroke();
    ctx.closePath();

    // Right horizontal line
    ctx.beginPath();
    ctx.lineWidth = 3;
    ctx.moveTo(750, 200);
    ctx.lineTo(760, 200);
    ctx.stroke();
    ctx.closePath();

    // Left dashed semi-circle
    ctx.beginPath();
    ctx.setLineDash([5, 5]);
    ctx.arc(149, 200, 50, Math.PI / 2, 3 * Math.PI / 2);
    ctx.stroke();
    ctx.closePath();

    // Right dashed semi-circle
    ctx.beginPath();
    ctx.arc(650, 200, 50, 3 * Math.PI / 2, Math.PI / 2);
    ctx.stroke();
    ctx.closePath();
  }, []);

  const handleClick = (e) => {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCoordinates({ x, y });

    // Send coordinates to the FastAPI backend
    axios
      .get(`/predict?x=${x}&y=${y}`)
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };
  
  const handlePlayerSelect = (player) => {
    setSelectedPlayer(player);
  };

  return (
    <div style={{ display: 'flex' }}>
      <div>
        <h2>NBA Court Canvas</h2>
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          style={{ border: '1px solid black' }}
          onClick={handleClick}
        />
        <p>Selected Coordinates: ({coordinates.x}, {coordinates.y})</p>
      </div>
      <div style={{ marginLeft: '20px' }}>
        <h3>Select Player</h3>
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
      </div>
    </div>
  );
};

export default NBACourtCanvas;