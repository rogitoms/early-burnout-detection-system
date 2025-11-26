// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('AuthProvider: Initializing...');
    checkAuthStatus()
      .then(() => {
        console.log('AuthProvider: Initial auth check completed');
      })
      .finally(() => {
        console.log('AuthProvider: Setting loading to false');
        setLoading(false);
      });
  }, []);

  const checkAuthStatus = async () => {
    try {
      console.log('AuthContext: Checking auth status...');
      // Use a simple endpoint that returns user info if authenticated
      const response = await api.get('/api/auth/user/');
      console.log('AuthContext: Auth check successful, user data:', response.data);
      setUser(response.data);
      return response.data; // Return the user data
    } catch (error) {
      console.log('AuthContext: Auth check failed:', error.response?.status, error.response?.data);
      setUser(null);
      return null;
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login/', { email, password });
      
      if (response.data.requires_2fa) {
        return { 
          success: true, 
          requires2FA: true,
          email: response.data.email,
          message: response.data.message 
        };
      } else {
        setUser(response.data.user);
        return { success: true, data: response.data };
      }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const complete2FALogin = async () => {
    try {
      console.log('Completing 2FA login...');
      
      // Fetch user data after 2FA verification
      const userData = await checkAuthStatus();
      console.log('User data after 2FA:', userData);
      
      if (userData) {
        console.log('2FA login successful, user:', userData);
        return { success: true, user: userData };
      } else {
        console.log('No user data found after 2FA verification');
        return { success: false, message: 'Session not established after 2FA' };
      }
    } catch (error) {
      console.error('Complete 2FA login error:', error);
      return { success: false, message: '2FA verification failed' };
    }
  };

  const signup = async (email, password) => {
    try {
      const response = await api.post('/api/auth/signup/', { email, password });
      setUser(response.data.user);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Signup failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout/');
      setUser(null);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, message: 'Logout failed' };
    }
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    checkAuthStatus, 
    complete2FALogin
  };

  return (
    <AuthContext.Provider value={value}>
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          Loading application...
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
}