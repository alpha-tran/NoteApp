import axios from 'axios';
import { LoginCredentials, RegisterData, AuthResponse, User } from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const authService = {
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        
        const response = await api.post<AuthResponse>('/auth/login', formData);
        return response.data;
    },

    async register(data: RegisterData): Promise<User> {
        const response = await api.post<User>('/auth/register', data);
        return response.data;
    },

    async getCurrentUser(): Promise<User> {
        const response = await api.get<User>('/auth/me');
        return response.data;
    },

    async logout(): Promise<void> {
        await api.post('/auth/logout');
        localStorage.removeItem('token');
    }
}; 