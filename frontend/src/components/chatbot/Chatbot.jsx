import React, { useState, useEffect,useRef,useCallback } from 'react';
import { useChatbot } from '../../hooks/useChatbot';
import './Chatbot.css';

const Chatbot = ({ onAssessmentComplete,user }) => {
  const { 
    currentSession,
    currentQuestion,
    isLoading,
    error,
    startNewSession,
    submitAnswer,
    assessmentComplete,
    result
  } = useChatbot();

  const [currentAnswer, setCurrentAnswer] = useState('');
  const [directAnalysis, setDirectAnalysis] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const messagesEndRef = useRef(null);
  const [hasStartedNewSession, setHasStartedNewSession] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  

  const API_BASE_URL = 'http://localhost:8000/api';

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages, directAnalysis, currentQuestion]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleStartNewSession = useCallback(async () => {
    setShowWelcome(true);
    setCurrentAnswer('');
    setDirectAnalysis(null);
    setHasStartedNewSession(true);

    if (onAssessmentComplete) {
      onAssessmentComplete(); // Refresh the assessments list in parent
    }

    await startNewSession();
  }, [startNewSession]);
  
  useEffect(() => {
    if (!currentSession && !isLoading && !hasStartedNewSession) {
      startNewSession();
    }
  }, [currentSession, isLoading, hasStartedNewSession, startNewSession]);

  
  // Validation function
  const validateInput = (text) => {
    // Check if input is empty
    if (!text.trim()) {
      return false;
    }

    // Check for numbers and symbols (only allow letters, spaces, and basic punctuation)
    const invalidChars = /[0-9!@#$%^&*()_+\-=\[\]{};:"\\|<>?/~`]/;
    if (invalidChars.test(text)) {
      return false;
    }

    // Check if input is only spaces
    if (text.trim().length === 0) {
      return false;
    }

    // Check minimum word count
    const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
    if (wordCount < 5) {
      return false;
    }

    return true; // Valid input
  };

  const handleInputChange = (text) => {
    setCurrentAnswer(text);
  };

  const handleSubmit = async () => {
    // Validate input before submission
    if (!validateInput(currentAnswer)) {
      return; // Simply return without submitting
    }

    // Hide welcome message on first interaction
    if (showWelcome) {
      setShowWelcome(false);
    }

     const answerToSubmit = currentAnswer;
      setCurrentAnswer('');
    // If there's a current question in the assessment, submit as answer
    if (currentQuestion && !assessmentComplete) {
      const isLastQuestion = currentQuestion.id === 6;
    
      if (isLastQuestion) {
        setIsAnalyzing(true); // Show analyzing message for last question
      }
      await submitAnswer(currentQuestion.id, answerToSubmit);
    
      if (isLastQuestion) {
        setIsAnalyzing(false);
      }
    }
    else {
      try {
        const response = await fetch(`${API_BASE_URL}/analyze-burnout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: answerToSubmit }),
        });

        if (!response.ok) {
          throw new Error('Failed to analyze message');
        }

        const data = await response.json();
        setDirectAnalysis(data);
        
      } catch (error) {
        console.error('Error:', error);
        setDirectAnalysis({ 
          error: ' Sorry, I encountered an error. Please try again.' 
        });
      }
    }
  };

  const getSeverityIcon = (level) => {
    switch (level) {
      case 'LOW': return '🟢';
      case 'MODERATE': return '🟡';
      case 'HIGH': return '🔴';
      default: return '📊';
    }
  };

 const handleTakeAnotherAssessment = async () => {
  // Call the parent's refresh function to update the assessments list
  if (onAssessmentComplete) {
    onAssessmentComplete(); // This will trigger fetchAssessments in Dashboard
  }
  await handleStartNewSession();
};
  
  const getSeverityDescription = (level) => {
    switch (level) {
      case 'LOW': return 'You are managing well with minimal burnout symptoms';
      case 'MODERATE': return 'You are experiencing some burnout symptoms that need attention';
      case 'HIGH': return 'You are experiencing significant burnout symptoms that require immediate attention';
      default: return 'Assessment complete';
    }
  };

  // Response Formatting for direct analysis
  const formatDirectAnalysis = (data) => {
    if (data.error) return data.error;
    
    return `
🧠 **Instant Burnout Risk Analysis:**
- **Level:** ${data.color || ''} ${data.burnout_level}
- **Score:** ${data.burnout_score?.toFixed(2) || 'N/A'}

**Recommendations:**
${data.llm_recommendations}
    `;
  };

  const getButtonText = () => {
    if (isLoading) return 'Sending...';
    if (!currentQuestion || assessmentComplete) return 'Get Analysis';
    return 'Send Answer';
  };

  // Check if input is valid for button enable/disable
  const isInputValid = () => {
    return validateInput(currentAnswer);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-messages">
        {/* Welcome Message */}
        {showWelcome && (
          <div className="message">
            <div className="message-content">
              <div className="message-avatar assistant">
                🧠
              </div>
              <div className="message-bubble assistant">
                <div className="welcome-message">
                  <h3>Hello!</h3>
                  <p>Welcome to your burnout risk assessment. I'm here to help you understand your current stress levels and provide personalized recommendations.</p>
                  <p>Let's start with a few questions to assess your situation. Take your time and answer honestly.</p>
                  <div className="welcome-tip">
                    <small> <strong>Tip:</strong> Please provide detailed answers with at least 5 words, using only text.</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSession?.messages?.map((message, index) => (
          <div key={index} className={`message ${message.message_type === 'answer' ? 'answer' : ''}`}>
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
        
        {/* Show direct analysis results */}
        {directAnalysis && (
          <div className="message">
            <div className="message-content">
              <div className="message-avatar assistant">
                A
              </div>
              <div className="message-bubble assistant">
                {formatDirectAnalysis(directAnalysis).split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Show assessment result as a chat message */}
        {assessmentComplete && result && (
          <div className="message">
            <div className="message-content">
              <div className="message-avatar assistant">
                🧠
              </div>
              <div className="message-bubble assistant assessment-result-message">
                <div className="result-header">
                  <h3>Assessment Complete!</h3>
                  <p>Here's your burnout risk assessment result</p>
                </div>
                
                <div className="result-summary">
                  <div className="severity-badge">
                    <span className="severity-icon">{getSeverityIcon(result.level)}</span>
                    <span className="severity-level">{result.level} BURNOUT RISK</span>
                  </div>
                  
                  <div className="severity-description">
                    {getSeverityDescription(result.level)}
                  </div>
                  
                  <div className="score-display">
                    <div className="score-value">{(result.score * 100).toFixed(0)}%</div>
                    <div className="score-label">Burnout Risk Score</div>
                  </div>
                </div>
                {/* ADD LLM SUMMARY HERE */}
                {result.detailed_analysis && (
                  <div className="llm-summary-section">
                    <h4>Summary</h4>
                    <div className="llm-summary-content">
                      {result.detailed_analysis}
                    </div>
                  </div>
                )}
                {/* AI-Powered Recommendations */}
                <div className="recommendation-section">
                  <h4>Recommendations</h4>
                  <div className="recommendation-content">
                    {result.llm_recommendations ? (
                      <div className="llm-recommendations">
                        {result.llm_recommendations.split('**').map((section, index) => {
                          if (index % 2 === 1) {
                            // This is a bold section (title)
                            return <strong key={index}>{section.trim()}</strong>;
                          } else {
                            // This is regular text
                            return section.split('\n').map((line, lineIndex) => (
                              <div key={`${index}-${lineIndex}`} className="recommendation-line">
                                {line.trim()}
                              </div>
                            ));
                          }
                        })}
                      </div>
                    ) : (
                      <p>{result.llm_recommendations}</p>
                    )}
                  </div>
                </div>

                <div className="result-actions">
                  <button 
                    className="action-btn primary"
                    onClick={handleTakeAnotherAssessment}
                  >
                    Take Another Assessment
                  </button>
                  
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Show current question */}
        {currentQuestion && !assessmentComplete && !currentSession?.messages?.some(msg => 
          msg.message_type === 'question' && msg.content === currentQuestion.question
        ) && (
          <div className="message">
            <div className="message-content">
              <div className="message-avatar assistant">
                A
              </div>
              <div className="message-bubble assistant">
                {currentQuestion.question}
              </div>
            </div>
          </div>
        )}
        {/* Empty div for auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Show analyzing message for last question */}
      {isAnalyzing && (
        <div className="message">
          <div className="message-content">
            <div className="message-avatar assistant">
              🧠
            </div>
            <div className="message-bubble assistant">
              <div className="analyzing-message">
                <div className="analyzing-spinner"></div>
                <p>Analyzing your responses and generating personalized recommendations...</p>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Input area - only show if not showing final results */}
      {!assessmentComplete && (
        <div className="current-question">
          <div className="answer-input">
            <textarea
              value={currentAnswer}
              onChange={(e) => handleInputChange(e.target.value)}
              placeholder="Type your answer here..."
              rows="3"
              disabled={isLoading}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            
            <button 
              onClick={handleSubmit}
              disabled={!isInputValid() || isLoading}
              className="submit-btn primary"
            >
            </button>
          </div>

          {currentQuestion && (
            <div className="progress-indicator">
              Question {currentQuestion.id} of 6
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isLoading && !currentQuestion && !assessmentComplete && (
        <div className="loading-message">
          Analyzing your responses...
        </div>
      )}
    </div>
  );
};

export default Chatbot;