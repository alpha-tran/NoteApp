import axios from 'axios';
import { LoginCredentials, RegisterData, AuthResponse, User } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

console.log('API URL:', API_URL); // Debug log

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Cho phép gửi credentials (cookies) với các yêu cầu CORS
});

// Xử lý lỗi global
api.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
            console.error('Response status:', error.response.status);
        }
        return Promise.reject(error);
    }
);

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('Request config:', config); // Debug log
    return config;
});

export const authService = {
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        
        console.log('Login with:', credentials.username); // Debug log
        try {
            const response = await api.post<AuthResponse>('/api/auth/login', formData);
            return response.data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async register(data: RegisterData): Promise<User> {
        console.log('Registering with:', data.email); // Debug log
        try {
            const response = await api.post<User>('/api/auth/register', data);
            return response.data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    async getCurrentUser(): Promise<User> {
        const response = await api.get<User>('/api/auth/me');
        return response.data;
    },

    async logout(): Promise<void> {
        await api.post('/api/auth/logout');
        localStorage.removeItem('token');
    }
};