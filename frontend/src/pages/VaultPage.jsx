import React, { useState, useEffect } from 'react';
import axios from '../api/axiosInstance';

const VaultPage = () => {
  const [email, setEmail] = useState('');
  const [masterPassword, setMasterPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [site, setSite] = useState('');
  const [password, setPassword] = useState('');
  const [useAI, setUseAI] = useState(false);
  const [length, setLength] = useState(12);
  const [useSymbols, setUseSymbols] = useState(true);
  const [passwords, setPasswords] = useState([]);
  const [message, setMessage] = useState('');
  const [authError, setAuthError] = useState('');

  // Attempt auto-login from localStorage on mount
  useEffect(() => {
    const storedEmail = localStorage.getItem("email");
    const storedMaster = localStorage.getItem("masterPassword");
    if (storedEmail && storedMaster) {
      setEmail(storedEmail);
      setMasterPassword(storedMaster);
      handleLoginStored(storedEmail, storedMaster);
    }
    // eslint-disable-next-line
  }, []);

  // Helper for logging in with stored credentials
  const handleLoginStored = async (storedEmail, storedMaster) => {
    try {
      const res = await axios.post('/retrieve-passwords', {
        email: storedEmail,
        master_password: storedMaster,
      });
      setPasswords(res.data.passwords);
      setIsAuthenticated(true);
    } catch (err) {
      console.error('Auto-login failed', err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/login', { email, password: masterPassword });
      const res = await axios.post('/retrieve-passwords', {
        email,
        master_password: masterPassword,
      });
      setPasswords(res.data.passwords);
      setIsAuthenticated(true);
      setAuthError('');
      localStorage.setItem("email", email);
      localStorage.setItem("masterPassword", masterPassword);
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Login failed.');
    }
  };

  const handleStore = async (e) => {
    e.preventDefault();
    try {
      let finalPassword = password;
      if (useAI) {
        const aiRes = await axios.get(`/generate-password?length=${length}&use_symbols=${useSymbols}`);
        setPassword(aiRes.data.password);
        finalPassword = aiRes.data.password;
      }
      const res = await axios.post('/store-password', {
        email,
        master_password: masterPassword,
        site,
        password: finalPassword,
        use_ai: false,
      });
      setMessage('Password stored.');
      // Update list
      const updated = await axios.post('/retrieve-passwords', {
        email,
        master_password: masterPassword,
      });
      setPasswords(updated.data.passwords);
    } catch (err) {
      setMessage('Failed to store password.');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="vault-login">
        <h2>Access Your Vault</h2>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Master Password"
            value={masterPassword}
            onChange={(e) => setMasterPassword(e.target.value)}
            required
          />
          <button type="submit">Unlock Vault</button>
        </form>
        {authError && <p className="error">{authError}</p>}
      </div>
    );
  }

  return (
    <div className="vault-container" style={{ maxWidth: '600px', margin: 'auto', padding: '2rem' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Password Vault</h2>
      <form onSubmit={handleStore} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <input
          type="text"
          placeholder="Site (e.g. github.com)"
          value={site}
          onChange={(e) => setSite(e.target.value)}
          required
          style={{ padding: '0.75rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        {!useAI && (
          <input
            type="text"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '0.75rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc' }}
          />
        )}
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="checkbox"
            checked={useAI}
            onChange={() => setUseAI(!useAI)}
          />
          Use AI-generated password
        </label>
        {useAI && (
          <>
            <label style={{ display: 'flex', flexDirection: 'column', fontSize: '0.9rem' }}>
              Length:
              <input
                type="number"
                min="8"
                max="32"
                value={length}
                onChange={(e) => setLength(Number(e.target.value))}
                style={{ padding: '0.5rem', fontSize: '1rem', borderRadius: '5px', border: '1px solid #ccc', marginBottom:'10px', }}
              />
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={useSymbols}
                onChange={() => setUseSymbols(!useSymbols)}
              />
              Use symbols
            </label>
          </>
        )}
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
          Store Password
        </button>
      </form>
      {message && <p style={{ color: 'green', marginTop: '1rem' }}>{message}</p>}

      <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Stored Passwords</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {passwords.map((entry, index) => (
          <div key={index} style={{
            border: '1px solid #ccc',
            borderRadius: '5px',
            padding: '0.75rem 1rem',
            backgroundColor: '#f9f9f9',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <strong>{entry.site}</strong>
            <span>{entry.password}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VaultPage;