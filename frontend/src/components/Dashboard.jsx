// frontend/src/components/Dashboard.jsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {user?.email}!</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </header>
      
      <div className="dashboard-content">
        <h2>Burnout Detection System</h2>
        <div className="coming-soon">
          <h3>Chatbot Interface Coming Soon...</h3>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;