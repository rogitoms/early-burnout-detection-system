// services/chatbot.js 
import api from './api';

export const chatbotService = {
    startSession: async () => {
        try {
            const response = await api.post('/chatbot/start-session/');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to start chat session');
        }
    },

    submitAnswer: async (questionId, answer) => {
        try {
            const response = await api.post('/chatbot/submit-answer/', {
                question_id: questionId,
                answer: answer
            });
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to submit answer');
        }
    },

    getChatHistory: async () => {
        try {
            const response = await api.get('/chatbot/history/');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to get chat history');
        }
    },

    //DELETE METHOD
  deleteSession: async (sessionId) => {
    try {
        const response = await api.delete(`/chatbot/session/${sessionId}/delete/`);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Failed to delete session');
    }
}
};