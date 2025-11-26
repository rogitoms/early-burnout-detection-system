import { useState, useEffect } from 'react';
import { chatbotService } from '../services/chatbot';

export const useChatbot = () => {
    const [currentSession, setCurrentSession] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [assessmentComplete, setAssessmentComplete] = useState(false);
    const [result, setResult] = useState(null);
    const [hasInitialized, setHasInitialized] = useState(false);

    const startNewSession = async () => {
        if (isLoading) return; // Prevent multiple calls
        
        setIsLoading(true);
        setError('');
        try {
            const response = await chatbotService.startSession();
            setCurrentSession(response.session);
            setCurrentQuestion(response.current_question);
            setAssessmentComplete(false);
            setResult(null);
            setHasInitialized(true);
        } catch (err) {
            setError(err.message || 'Failed to start assessment session');
        } finally {
            setIsLoading(false);
        }
    };

    const submitAnswer = async (questionId, answer) => {
        setIsLoading(true);
        setError('');
        
        try {
          if (currentSession) {
            const optimisticSession = {
              ...currentSession,
              messages: [
                ...currentSession.messages,
                {
                  message_type: 'answer',
                  content: answer,
                  timestamp: new Date().toISOString(),
                  question_id: questionId
                }
              ]
            };
            setCurrentSession(optimisticSession);
          }
          
          // THEN make the API call
          const response = await chatbotService.submitAnswer(questionId, answer);
          
          // Update with the real server response
          setCurrentSession(response.session);
          
          if (response.assessment_complete) {
            setAssessmentComplete(true);
            setResult(response.result);
            setCurrentQuestion(null);
          } else {
            setCurrentQuestion(response.current_question);
          }
        } catch (err) {
          setError(err.message || 'Failed to submit answer');
          // Optionally revert the optimistic update on error
        } finally {
          setIsLoading(false);
        }
      };

    // Auto-start session only once
    useEffect(() => {
        if (!hasInitialized && !currentSession && !isLoading) {
            startNewSession();
        }
    }, [hasInitialized, currentSession, isLoading]);

    return {
        currentSession,
        currentQuestion,
        isLoading,
        error,
        assessmentComplete,
        result,
        startNewSession,
        submitAnswer
    };
};