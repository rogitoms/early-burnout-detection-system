// frontend/src/components/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminEmployeeManagement from './AdminEmployeeManagement';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [adminStats, setAdminStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' or 'employees'

  // Fetch admin data if user is admin
  useEffect(() => {
    if (user && user.is_admin) {
      fetchAdminData();
    }
  }, [user]);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/auth/admin/dashboard/', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setAdminStats(data.stats);
      } else {
        console.error('Failed to fetch admin data');
      }
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Welcome, {user.email}!</h1>
          <span className="role-badge" style={{ 
            backgroundColor: user.is_admin ? '#dc3545' : '#28a745', 
            color: 'white', 
            padding: '4px 12px', 
            borderRadius: '16px', 
            fontSize: '12px',
            fontWeight: 'bold'
          }}>
            {user.role_display}
          </span>
          {user.department && (
            <span style={{ marginLeft: '10px', color: '#666', fontSize: '14px' }}>
              {user.department}
            </span>
          )}
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </header>
      
      <div className="dashboard-content">
        <h2>Burnout Detection System</h2>
        
        {/* Admin Navigation Tabs */}
        {user.is_admin && (
          <div style={{ 
            display: 'flex', 
            gap: '10px', 
            marginBottom: '20px',
            borderBottom: '2px solid #dee2e6'
          }}>
            <button
              onClick={() => setActiveTab('overview')}
              style={{
                padding: '10px 20px',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'overview' ? '3px solid #dc3545' : '3px solid transparent',
                color: activeTab === 'overview' ? '#dc3545' : '#666',
                fontWeight: activeTab === 'overview' ? 'bold' : 'normal',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('employees')}
              style={{
                padding: '10px 20px',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === 'employees' ? '3px solid #dc3545' : '3px solid transparent',
                color: activeTab === 'employees' ? '#dc3545' : '#666',
                fontWeight: activeTab === 'employees' ? 'bold' : 'normal',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Employee Management
            </button>
          </div>
        )}
        
        {/* Admin-specific content */}
        {user.is_admin && activeTab === 'overview' && (
          <div className="admin-section" style={{ 
            border: '2px solid #dc3545', 
            borderRadius: '8px', 
            padding: '20px', 
            marginBottom: '20px',
            backgroundColor: '#fff5f5'
          }}>
            <h3 style={{ color: '#dc3545', marginTop: '0' }}>Admin Dashboard</h3>
            
            {loading ? (
              <p>Loading admin statistics...</p>
            ) : adminStats ? (
              <div className="admin-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div className="stat-card" style={{ 
                  padding: '15px', 
                  backgroundColor: 'white', 
                  border: '1px solid #ddd', 
                  borderRadius: '6px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>Total Users</h4>
                  <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0', color: '#007bff' }}>
                    {adminStats.total_users}
                  </p>
                </div>
                
                <div className="stat-card" style={{ 
                  padding: '15px', 
                  backgroundColor: 'white', 
                  border: '1px solid #ddd', 
                  borderRadius: '6px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>Employees</h4>
                  <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0', color: '#28a745' }}>
                    {adminStats.total_employees}
                  </p>
                </div>
                
                <div className="stat-card" style={{ 
                  padding: '15px', 
                  backgroundColor: 'white', 
                  border: '1px solid #ddd', 
                  borderRadius: '6px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>Admins</h4>
                  <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0', color: '#dc3545' }}>
                    {adminStats.total_admins}
                  </p>
                </div>
              </div>
            ) : (
              <p style={{ color: '#dc3545' }}>Failed to load admin statistics.</p>
            )}
          </div>
        )}

        {/* Employee Management Tab */}
        {user.is_admin && activeTab === 'employees' && (
          <div style={{ 
            border: '2px solid #dc3545', 
            borderRadius: '8px', 
            padding: '20px', 
            marginBottom: '20px',
            backgroundColor: 'white'
          }}>
            <AdminEmployeeManagement />
          </div>
        )}
        
        {/* Employee-specific content */}
        {user.is_employee && (
          <div className="employee-section" style={{ 
            border: '2px solid #28a745', 
            borderRadius: '8px', 
            padding: '20px', 
            marginBottom: '20px',
            backgroundColor: '#f8fff8'
          }}>
            <h3 style={{ color: '#28a745', marginTop: '0' }}>Employee Dashboard</h3>
            
            <div className="employee-info" style={{ marginBottom: '20px' }}>
              <p><strong>Email:</strong> {user.email}</p>
              {user.department && <p><strong>Department:</strong> {user.department}</p>}
              {user.employee_id && <p><strong>Employee ID:</strong> {user.employee_id}</p>}
              <p><strong>2FA Status:</strong> {user.is_2fa_enabled ? 'Enabled' : 'Disabled'}</p>
            </div>
          </div>
        )}
        
        {/* Common content for all users - only show on overview tab or for employees */}
        {(user.is_employee || activeTab === 'overview') && (
          <div className="coming-soon" style={{ 
            textAlign: 'center', 
            padding: '40px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            border: '1px solid #dee2e6'
          }}>
            <h3>Burnout Detection Chatbot</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Our AI-powered chatbot is coming soon to help assess and prevent employee burnout.
            </p>
            <div style={{ 
              padding: '20px', 
              backgroundColor: '#e9ecef', 
              borderRadius: '6px',
              color: '#495057'
            }}>
              <p>Features coming soon:</p>
              <ul style={{ textAlign: 'left', maxWidth: '300px', margin: '0 auto' }}>
                <li>Burnout risk assessment</li>
                <li>Personalized recommendations</li>
                <li>Mental health resources</li>
                <li>Progress tracking</li>
                {user.is_admin && <li>Employee analytics dashboard</li>}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;