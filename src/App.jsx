import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [winner, setWinner] = useState('');

  const handlePredict = async () => {
    try {
      const res = await axios.post('http://localhost:5000/predict', {
        team1,
        team2,
      });
      setWinner(res.data.winner);
    } catch (error) {
      setWinner(error.response?.data?.error || 'An error occurred');
    }
  };

  const teams = [
    "Chennai Super Kings", "Mumbai Indians", "Gujarat Titans",
    "Kolkata Knight Riders", "Royal Challengers Bengaluru", "Delhi Capitals",
    "Sunrisers Hyderabad", "Punjab Kings", "Rajasthan Royals", "Lucknow Super Giants"
  ];

  return (
    <div className="container">
      <h1>IPL WINNER PREDICTOR</h1>

      <select value={team1} onChange={(e) => setTeam1(e.target.value)}>
        <option value="">Select Team 1</option>
        {teams.map((team) => (
          <option key={team} value={team}>{team}</option>
        ))}
      </select>

      <select value={team2} onChange={(e) => setTeam2(e.target.value)}>
        <option value="">Select Team 2</option>
        {teams.map((team) => (
          <option key={team} value={team}>{team}</option>
        ))}
      </select>

      <button onClick={handlePredict} disabled={!team1 || !team2 || team1 === team2}>
        Predict Winner
      </button>

      {winner && <h2>{winner}</h2>}
    </div>
  );
}

export default App;

