import React, { useState } from 'react';
import axios from '../api/axiosInstance';
import { useNavigate } from 'react-router-dom';

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      await axios.post('/register', { email, password });
      setSuccess(true);
      setTimeout(() => navigate('/vault'), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    }
  };

  return (
    <div className="island" style={{ maxWidth: '400px', margin: 'auto', padding: '2rem' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Register</h2>
      <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ padding: '0.75rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        <input
          type="password"
          placeholder="Master Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ padding: '0.75rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          style={{ padding: '0.75rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        <button
          type="submit"
          style={{
            padding: '0.75rem',
            fontSize: '1rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: 'linear-gradient(to right, #1f1c2c, #928dab)',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Register
        </button>
      </form>
      {error && <p className="error" style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
      {success && <p className="success" style={{ color: 'green', marginTop: '1rem' }}>Registration successful! Redirecting to your vault...</p>}
    </div>
  );
};

export default RegisterPage;
