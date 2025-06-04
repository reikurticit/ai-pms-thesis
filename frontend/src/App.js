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
      <button style={buttonStyle} onClick={() => navigate('/register')}>Register</button>
      <button style={buttonStyle} onClick={() => navigate('/vault')}>Login</button>
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
