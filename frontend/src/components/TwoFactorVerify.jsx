import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const TwoFactorVerify = ({ email, onBack }) => {
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { complete2FALogin } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('Verifying 2FA token:', token, 'for email:', email);
      
      const response = await fetch('http://localhost:8000/api/auth/2fa/verify/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, email }),
      });

      const data = await response.json();
      console.log('2FA verify response:', data);

      if (response.ok) {
        setMessage('2FA verification successful!');
        
        // Complete the 2FA login process
        console.log('Completing 2FA login...');
        const result = await complete2FALogin();
        console.log('Complete 2FA result:', result);
        
        if (result.success) {
          console.log('Navigating to dashboard...');
          navigate('/dashboard');
        } else {
          console.log('2FA completion failed:', result.message);
          setError(result.message || 'Authentication failed after 2FA verification');
        }
        
      } else {
        console.log('2FA verification failed:', data);
        setError(data.message || 'Invalid verification code');
      }
    } catch (error) {
      console.error('2FA verification network error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      setError('');
      setMessage('');
      
      console.log('Requesting new 2FA code for:', email);
      
      const response = await fetch('http://localhost:8000/api/auth/2fa/request/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setMessage('New verification code sent to your email.');
      } else {
        setError(data.message || 'Failed to send new code');
      }
    } catch (error) {
      console.error('Resend code error:', error);
      setError('Network error. Please try again.');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Two-Factor Authentication</h2>
        <p>Enter the verification code sent to: <strong>{email}</strong></p>
        
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Verification Code:</label>
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
              required
              placeholder="Enter 6-digit code"
              maxLength="6"
              pattern="\d{6}"
              autoFocus
            />
          </div>

          <button type="submit" disabled={loading || token.length !== 6}>
            {loading ? 'Verifying...' : 'Verify Code'}
          </button>
          
          <button 
            type="button" 
            onClick={handleResendCode}
            className="secondary-btn"
            style={{ marginTop: '0.5rem' }}
            disabled={loading}
          >
            Resend Code
          </button>
          
          <button 
            type="button" 
            onClick={onBack}
            className="secondary-btn"
            style={{ marginTop: '0.5rem' }}
          >
            Back to Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default TwoFactorVerify;