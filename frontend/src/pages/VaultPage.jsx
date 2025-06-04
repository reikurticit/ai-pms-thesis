import React, { useState } from 'react';
import axios from '../api/axiosInstance';

const VaultPage = () => {
  const [email, setEmail] = useState('');
  const [masterPassword, setMasterPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [site, setSite] = useState('');
  const [password, setPassword] = useState('');
  const [useAI, setUseAI] = useState(false);
  const [passwords, setPasswords] = useState([]);
  const [message, setMessage] = useState('');
  const [authError, setAuthError] = useState('');

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
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Login failed.');
    }
  };

  const handleStore = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/store-password', {
        email,
        master_password: masterPassword,
        site,
        password: useAI ? undefined : password,
        use_ai: useAI,
      });
      setMessage('Password stored.');
      if (useAI && res.data.password) setPassword(res.data.password);
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
    <div className="vault-container">
      <h2>Password Vault</h2>
      <form onSubmit={handleStore}>
        <input
          type="text"
          placeholder="Site (e.g. github.com)"
          value={site}
          onChange={(e) => setSite(e.target.value)}
          required
        />
        {!useAI && (
          <input
            type="text"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        )}
        <label>
          <input
            type="checkbox"
            checked={useAI}
            onChange={() => setUseAI(!useAI)}
          />
          Use AI-generated password
        </label>
        <button type="submit">Store Password</button>
      </form>
      {message && <p>{message}</p>}

      <h3>Stored Passwords</h3>
      <ul>
        {passwords.map((entry, index) => (
          <li key={index}>
            <strong>{entry.site}</strong>: {entry.password}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default VaultPage;