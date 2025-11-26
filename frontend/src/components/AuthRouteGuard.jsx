// frontend/src/components/AuthRouteGuard.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AuthRouteGuard = ({ children }) => {
  const { user, loading } = useAuth();

  console.log('AuthRouteGuard - loading:', loading, 'user:', user);

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>;
  }

  // If user is already authenticated, redirect to dashboard
  if (user) {
    console.log('User authenticated, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }

  console.log('User not authenticated, showing auth form');
  return children;
};

export default AuthRouteGuard;