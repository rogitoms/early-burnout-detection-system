import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Chatbot from './chatbot/Chatbot';
import { chatbotService } from '../services/chatbot';
import './Dashboard.css';
import AdminEmployeeManagement from './AdminEmployeeManagement';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [assessments, setAssessments] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [isLoadingAssessments, setIsLoadingAssessments] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [error, setError] = useState(null);
  const [chatbotKey, setChatbotKey] = useState(0);

  const handleLogout = () => {
    logout();
  };

  const fetchAssessments = async () => {
      if (user.is_admin) return;
      
      setIsLoadingAssessments(true);
      try {
          const response = await chatbotService.getChatHistory();
          console.log('Chat history response:', response); // Debug log
          
          // Handle different response structures
          const sessions = response.sessions || response || [];
          
          // Filter only completed assessments with scores
          const completedAssessments = sessions
              .filter(session => {
                  const isComplete = session.is_complete || session.completed_at;
                  const hasScore = session.burnout_score !== null && session.burnout_score !== undefined;
                  return isComplete && hasScore;
              })
              .map(session => ({
                  id: session.id,
                  date: new Date(session.completed_at || session.started_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                  }),
                  status: 'Completed',
                  level: session.burnout_level,
                  score: session.burnout_score,
                  recommendation: session.recommendation || session.llm_recommendations,
                  timestamp: session.completed_at || session.started_at,
                  messages: session.messages || [],
                  summary: session.detailed_analysis || session.summary
              }))
              .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
          
          setAssessments(completedAssessments);
      } catch (error) {
          console.error('Failed to fetch assessments:', error);
          setAssessments([]);
      } finally {
          setIsLoadingAssessments(false);
      }
  };

  useEffect(() => {
    fetchAssessments();
  }, [user.id, user.is_admin]);


  // In Dashboard.jsx - add this to see what's being returned
  useEffect(() => {
      console.log('Current assessments:', assessments);
      console.log('User:', user);
  }, [assessments, user]);

  const refreshAssessments = () => {
    fetchAssessments();
  };

  const handleAssessmentClick = (assessment) => {
    setSelectedAssessment(assessment);
    setActiveTab('assessment-details');
  };

  const handleBackToChat = () => {
    setSelectedAssessment(null);
    setActiveTab('chat');
  };

  // In Dashboard.jsx - add these with your other useState declarations
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState(null);


  // In Dashboard.jsx - add these functions
  const handleDeleteAssessment = async (assessmentId, event) => {
    event.stopPropagation();
    setSessionToDelete(assessmentId);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!sessionToDelete) return;
    
    try {
      await chatbotService.deleteSession(sessionToDelete);
      setAssessments(prev => prev.filter(assessment => assessment.id !== sessionToDelete));
      
      if (selectedAssessment?.id === sessionToDelete) {
        setSelectedAssessment(null);
        setActiveTab('chat');
      }
      
    } catch (error) {
      console.error('Failed to delete assessment:', error);
      alert('Failed to delete assessment. Please try again.');
    } finally {
      setShowDeleteModal(false);
      setSessionToDelete(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setSessionToDelete(null);
  };
  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showUserMenu && !event.target.closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  // Admin Dashboard View
  if (user.is_admin) {
    return (
      <div className="admin-dashboard">
        <header className="admin-header">
          <div>
            <h1>
              Admin Dashboard
              <span className="admin-badge">Administrator</span>
            </h1>
          </div>
          <button className="admin-logout" onClick={handleLogout}>
            Logout
          </button>
        </header>

        <div className="admin-content">
          <h2>System Overview</h2>
         

          <div className="admin-section">
            <AdminEmployeeManagement />
          </div>
        </div>
      </div>
    );
  }

  // Employee Dashboard
  return (
    <div className="employee-dashboard">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? '' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>
          🧠My Profile
            <button 
              onClick={() => setSidebarOpen(false)}
              className="close-sidebar"
            >
            </button>
          </h2>
          <button 
            className="new-assessment-btn"
            onClick={() => {
              setSelectedAssessment(null);
              setActiveTab('chat');
              setChatbotKey(prev => prev + 1); // Force Chatbot to remount
            }}
          >
            New Assessment
          </button>
        </div>

        {/* Recent Assessments Section */}
        <div className="assessments-section">
          <div className="assessments-header">
            <h3>Recent Assessments</h3>
            <button 
              onClick={fetchAssessments} 
              className="refresh-assessments-btn"
              disabled={isLoadingAssessments}
            >
              
            </button>
          </div>
        <div className="assessment-list">
            {isLoadingAssessments ? (
              <div className="empty-assessments">
                <p>Loading assessments...</p>
              </div>
            ) : assessments.length === 0 ? (
              <div className="empty-assessments">
                <p>No assessments yet</p>
                <small>Complete your first assessment to see history here</small>
              </div>
            ) : (
              assessments.map((assessment) => (
                <div 
                  key={assessment.id} 
                  className={`assessment-item ${selectedAssessment?.id === assessment.id ? 'active' : ''}`}
                  onClick={() => handleAssessmentClick(assessment)}
                >
                  <div className="assessment-header">
                    <div className="assessment-title">
                      Assessment - {assessment.date}
                      {assessment.level && (
                        <div className={`assessment-level ${assessment.level}`}>
                          {assessment.level}
                        </div>
                      )}
                    </div>
                    <button 
                      className="delete-assessment-btn"
                      onClick={(e) => handleDeleteAssessment(assessment.id, e)}
                      title="Delete this assessment"
                    >
                    </button>
                  </div>
                  <div className="assessment-status">
                    Score: {(assessment.score * 100).toFixed(0)}%
                  </div>
                </div>
              ))
            )}
</div>
        </div>

        {/* User Profile Section*/}
        <div className="sidebar-footer">
          <div className="user-menu-container">
            <div className="user-profile-summary" onClick={toggleUserMenu}>
              <div className="user-avatar-small">
                {user.email.charAt(0).toUpperCase()}
              </div>
              <div className="user-info-small">
                <div className="user-name">{user.email.split('@')[0]}</div>
                <div className="user-email">{user.email}</div>
              </div>
              <button className="user-menu-toggle">
                
              </button>
            </div>

            {/* User Dropdown Menu - Only Logout */}
            {showUserMenu && (
              <div className="user-dropdown-menu">
                <div className="user-menu-header">
                  <div className="user-avatar-large">
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div className="user-details">
                    <div className="user-name-large">{user.email.split('@')[0]}</div>
                    <div className="user-email-large">{user.email}</div>
                    {user.department && (
                      <div className="user-department">{user.department}</div>
                    )}
                  </div>
                </div>

                <div className="user-menu-items">
                  <button className="menu-item logout-item" onClick={handleLogout}>
                    <span className="menu-icon"></span>
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="chat-area">
        <div className="chat-header">
          {!sidebarOpen && (
            <button 
              onClick={() => setSidebarOpen(true)}
              className="menu-button"
            >
            </button>
          )}
          <div>
            {selectedAssessment ? (
              <>
                <h1>Assessment Details</h1>
                <p>Completed on {selectedAssessment.date}</p>
              </>
            ) : (
              <>
                <h1>Burnout Risk Assessment</h1>
             
              </>
            )}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          {selectedAssessment ? (
            <AssessmentDetails assessment={selectedAssessment} user={user} />
          ) : (
            <Chatbot 
              key={chatbotKey}
              onAssessmentComplete={refreshAssessments} // Just pass the refresh function
              user={user}
            />
          )}
        </div>
      </div>
        {/* ADD THE MODAL RIGHT HERE */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content delete-modal">
            <h3>Delete chat?</h3>
            <p>Are you sure you want to delete this chat?</p>
            <div className="modal-actions">
              <button className="cancel-btn" onClick={cancelDelete}>
                Cancel
              </button>
              <button className="delete-btn" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// AssessmentDetails component remains the same
const AssessmentDetails = ({ assessment, user }) => {
  const getSeverityIcon = (level) => {
    switch (level) {
      case 'LOW': return '🟢';
      case 'MODERATE': return '🟡';
      case 'HIGH': return '🔴';
      default: return '📊';
    }
  };

  const getSeverityDescription = (level) => {
    switch (level) {
      case 'LOW': return 'You were managing well with minimal burnout symptoms';
      case 'MODERATE': return 'You were experiencing some burnout symptoms that needed attention';
      case 'HIGH': return 'You were experiencing significant burnout symptoms that required immediate attention';
      default: return 'Assessment completed';
    }
  };

  return (
    <div className="assessment-details">
      <div className="result-card">
        <div className="result-badge">
          <span className="result-icon">{getSeverityIcon(assessment.level)}</span>
          <span className="result-level">{assessment.level} BURNOUT RISK</span>
        </div>
        
        <div className="severity-description">
          {getSeverityDescription(assessment.level)}
        </div>
        
        <div className="score-display">
          <div className="score-value">{(assessment.score * 100).toFixed(0)}%</div>
          <div className="score-label">Burnout Risk Score</div>
        </div>
        
        {assessment.summary && (
          <div className="llm-summary-section">
            <h3>Summary</h3>
            <div className="llm-summary-content">
              {assessment.summary}
            </div>
          </div>
        )}
        
        <div className="recommendation-section">
          <h3>Recommendations</h3>
           <div className="recommendation-content">
            {assessment.recommendation ? (
              <div className="llm-recommendations">
                {assessment.recommendation.split('**').map((section, index) => {
                  if (index % 2 === 1) {
                    return <strong key={index}>{section.trim()}</strong>;
                  } else {
                    return section.split('\n').map((line, lineIndex) => (
                      <div key={`${index}-${lineIndex}`} className="recommendation-line">
                        {line.trim()}
                      </div>
                    ));
                  }
                })}
              </div>
            ) : (
              <p>No recommendations available.</p>
            )}
          </div>
        </div>

        <div className="conversation-history">
          <h3>Conversation</h3>
          <div className="messages-list">
            {assessment.messages.map((message, index) => (
              <div key={index} className={`message-row ${message.message_type === 'answer' ? 'user' : 'assistant'}`}>
                <div className="message-content">
                  <div className={`message-avatar ${message.message_type === 'answer' ? 'user' : 'assistant'}`}>
                    {message.message_type === 'answer' ? user?.email?.charAt(0).toUpperCase() : '🧠'}
                  </div>
                  <div className={`message-bubble ${message.message_type === 'answer' ? 'user' : 'assistant'}`}>
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;