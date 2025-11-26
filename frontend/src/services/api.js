import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 60000,
    withCredentials: true, // IMPORTANT: This sends cookies/sessions
});

// Remove the token interceptor since you're using sessions
api.interceptors.request.use(
    (config) => {
        console.log(' Sending request with cookies/session');
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Handle response errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error(' API Error:', error.response?.status, error.response?.data);
        
        if (error.response?.status === 401) {
            console.log(' Redirecting to login...');
            window.location.href = '/login';
        }
        
        return Promise.reject(error);
    }
);

export default api;