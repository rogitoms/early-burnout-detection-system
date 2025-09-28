// frontend/src/components/Signup.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TwoFactorVerify from './TwoFactorVerify';

const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [twoFAEmail, setTwoFAEmail] = useState('');
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      console.log('Sending signup request...');
      
      const response = await fetch('http://localhost:8000/api/auth/signup/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log('Signup response:', data);

      if (response.ok) {
        console.log('Signup successful, 2FA required for new user');
        
        // Logout the user first (since signup auto-logs them in)
        try {
          await fetch('http://localhost:8000/api/auth/logout/', {
            method: 'POST',
            credentials: 'include',
          });
          console.log('User logged out after signup');
        } catch (logoutError) {
          console.error('Logout after signup failed:', logoutError);
        }
        
        setMessage('Account created successfully! 2FA verification is required to complete setup.');
        setRequires2FA(true);
        setTwoFAEmail(email);
        
        // Request 2FA code automatically for the new user
        try {
          console.log('Requesting 2FA code for new user:', email);
          const twoFAResponse = await fetch('http://localhost:8000/api/auth/2fa/request/', {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
          });
          
          const twoFAData = await twoFAResponse.json();
          console.log('2FA request response:', twoFAData);
          
          if (twoFAResponse.ok) {
            setMessage('Account created! Check your email for the 2FA verification code.');
          }
          
        } catch (twoFAError) {
          console.error('2FA request failed:', twoFAError);
          setMessage('Account created but failed to send 2FA code. Please use the resend button.');
        }
      } else {
        setError(data.message || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup network error:', error);
      setError('Cannot connect to server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (requires2FA) {
    return (
      <TwoFactorVerify 
        email={twoFAEmail} 
        onBack={() => {
          setRequires2FA(false);
          setTwoFAEmail('');
          setMessage('');
        }}
        isSignupFlow={true}
      />
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Create Account</h2>
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} autoComplete="off">
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="name@gmail.com"
              autoComplete="new-email"
              name="email"
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Create a password"
              autoComplete="new-password"
              name="password"
            />
          </div>

          <div className="form-group">
            <label>Confirm Password:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm your password"
              autoComplete="new-password"
              name="confirmPassword"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;