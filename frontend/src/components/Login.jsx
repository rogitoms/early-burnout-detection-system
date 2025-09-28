// frontend/src/components/Login.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import TwoFactorVerify from './TwoFactorVerify';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [twoFAEmail, setTwoFAEmail] = useState('');
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      console.log('Sending login request to:', 'http://localhost:8000/api/auth/login/');
      
      const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        if (data.requires_2fa) {
          console.log('2FA required, email:', data.email);
          setRequires2FA(true);
          setTwoFAEmail(data.email);
          setMessage('2FA verification required. Check your email for the verification code.');
          
          // Request 2FA code automatically
          try {
            console.log('Requesting 2FA code for:', data.email);
            const twoFAResponse = await fetch('http://localhost:8000/api/auth/2fa/request/', {
              method: 'POST',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ email: data.email }),
            });
            
            const twoFAData = await twoFAResponse.json();
            console.log('2FA request response:', twoFAData);
            
          } catch (twoFAError) {
            console.error('2FA request failed:', twoFAError);
          }
        } else {
          console.log('Regular login successful');
          // For now, just reload to dashboard
          window.location.href = '/dashboard';
        }
      } else {
        console.log('Login failed with status:', response.status);
        setError(data.message || `Login failed (Status: ${response.status})`);
      }
    } catch (error) {
      console.error('Login network error:', error);
      setError('Cannot connect to server. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  if (requires2FA) {
    return <TwoFactorVerify email={twoFAEmail} onBack={() => setRequires2FA(false)} />;
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Login to Burnout Detection</h2>
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-link">
          <Link to="/signup">Create account</Link> | <Link to="/password-reset">Forgot password?</Link>
        </p>
  
      </div>
    </div>
  );
};

export default Login;