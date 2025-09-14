// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// Simple axios configuration - NO CSRF handling needed now
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
    checkAuthStatus().finally(() => setLoading(false));
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await api.get('/api/auth/protected-test/');
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login/', { email, password });
      setUser(response.data.user);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      };
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
      const response = await api.post('/api/auth/logout/');
      setUser(null);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Logout error:', error);
      return { 
        success: false, 
        message: error.response?.data?.message || 'Logout failed' 
      };
    }
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}