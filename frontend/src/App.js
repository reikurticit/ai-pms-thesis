import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import VaultPage from './pages/VaultPage';

import './App.css';

function HomePage() {
  const navigate = useNavigate();
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    gap: '1rem'
  };
  const buttonStyle = {
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer'
  };

  return (
    <div style={containerStyle}>
      <button 
        style={{
            padding: '0.75rem',
            fontSize: '1rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: 'linear-gradient(to right, #1f1c2c, #928dab)',
            color: 'white',
            cursor: 'pointer'
          }} onClick={() => navigate('/register')}>Register</button>
      <button 
        style={{
            padding: '0.75rem',
            fontSize: '1rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: 'linear-gradient(to right, #1f1c2c, #928dab)',
            color: 'white',
            cursor: 'pointer'
          }} onClick={() => navigate('/vault')}>Vault</button>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/vault" element={<VaultPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
