import axios, { AxiosError } from 'axios';
import { LoginCredentials, RegisterData, AuthResponse, User } from '../types/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = '/api/v1';

const api = axios.create({
    baseURL: `${API_URL}${API_BASE}`,
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

class ApiError extends Error {
    constructor(message: string, public code: string, public details?: any) {
        super(message);
        this.name = 'ApiError';
    }
}

const logError = (error: any) => {
    if (process.env.NODE_ENV === 'development') {
        console.group('API Error');
        console.error('Timestamp:', new Date().toISOString());
        console.error('Error:', error.name);
        console.error('Message:', error.message);
        
        if (error instanceof ApiError) {
            console.error('Code:', error.code);
            console.error('Details:', error.details);
        }
        
        if (error instanceof AxiosError) {
            if (error.response) {
                console.error('Status:', error.response.status);
                console.error('Data:', error.response.data);
            } else if (error.request) {
                console.error('Request failed:', error.request);
            }
        }
        
        console.error('Stack:', error.stack);
        console.groupEnd();
    }
};

api.interceptors.request.use(
    (config) => {
        if (process.env.NODE_ENV === 'development') {
            console.log('Request:', {
                url: config.url,
                method: config.method,
            });
        }
        
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
    },
    (error) => {
        logError(error);
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    response => response,
    async error => {
        const config = error.config;
        
        if (error.message === 'Network Error' && !config._retry) {
            config._retry = true;
            try {
                return await axios(config);
            } catch (retryError) {
                return Promise.reject(retryError);
            }
        }
        
        return Promise.reject(error);
    }
);

const checkConnection = async () => {
    try {
        await axios.get(`${API_URL}/health`);
        return true;
    } catch (error) {
        return false;
    }
};

export const authService = {
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        try {
            if (!credentials.username || !credentials.password) {
                throw new ApiError('Missing credentials', 'VALIDATION_ERROR');
            }

            const response = await api.post<AuthResponse>('/auth/login', credentials);
            
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                return response.data;
            }
            
            throw new ApiError('Invalid response', 'INVALID_RESPONSE_ERROR');
        } catch (error: any) {
            if (error instanceof ApiError) throw error;
            throw new ApiError('Login failed', 'LOGIN_ERROR');
        }
    },

    async register(data: RegisterData): Promise<User> {
        try {
            const isConnected = await checkConnection();
            if (!isConnected) {
                throw new ApiError(
                    'Unable to connect to server',
                    'CONNECTION_ERROR',
                    { suggestion: 'Please check if the server is running at ' + API_URL }
                );
            }

            const validationErrors: Record<string, string> = {};
            
            if (!data.email) validationErrors.email = 'Email is required';
            if (!data.username) validationErrors.username = 'Username is required';
            if (!data.password) validationErrors.password = 'Password is required';
            if (!data.confirmPassword) validationErrors.confirmPassword = 'Password confirmation is required';
            
            if (Object.keys(validationErrors).length > 0) {
                throw new ApiError('Missing required fields', 'VALIDATION_ERROR', validationErrors);
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(data.email)) {
                throw new ApiError('Invalid email format', 'VALIDATION_ERROR', {
                    email: 'Please enter a valid email address'
                });
            }

            const passwordErrors: string[] = [];
            if (data.password.length < 8) passwordErrors.push('Password must be at least 8 characters long');
            if (!/[A-Z]/.test(data.password)) passwordErrors.push('Password must contain at least one uppercase letter');
            if (!/[a-z]/.test(data.password)) passwordErrors.push('Password must contain at least one lowercase letter');
            if (!/[0-9]/.test(data.password)) passwordErrors.push('Password must contain at least one number');
            if (!/[!@#$%^&*]/.test(data.password)) passwordErrors.push('Password must contain at least one special character (!@#$%^&*)');
            
            if (passwordErrors.length > 0) {
                throw new ApiError('Password requirements not met', 'VALIDATION_ERROR', {
                    password: passwordErrors
                });
            }

            if (data.password !== data.confirmPassword) {
                throw new ApiError('Passwords do not match', 'VALIDATION_ERROR', {
                    confirmPassword: 'Password confirmation does not match'
                });
            }

            const response = await api.post<User>('/auth/register', {
                email: data.email,
                username: data.username,
                password: data.password
            });

            if (!response.data) {
                throw new ApiError('Empty response from server', 'SERVER_ERROR');
            }

            return response.data;
        } catch (error: any) {
            if (error instanceof ApiError) {
                throw error;
            }

            if (axios.isAxiosError(error)) {
                if (!error.response) {
                    throw new ApiError(
                        'Unable to connect to server',
                        'NETWORK_ERROR',
                        { 
                            message: 'Please check your internet connection and ensure the server is running',
                            serverUrl: API_URL
                        }
                    );
                }

                const status = error.response.status;
                const data = error.response.data;

                switch (status) {
                    case 400:
                        throw new ApiError('Invalid registration data', 'VALIDATION_ERROR', data);
                    case 409:
                        throw new ApiError(
                            'Account already exists',
                            'DUPLICATE_ERROR',
                            { message: 'An account with this email or username already exists' }
                        );
                    case 422:
                        throw new ApiError('Invalid data format', 'VALIDATION_ERROR', data);
                    case 429:
                        throw new ApiError('Too many registration attempts', 'RATE_LIMIT_ERROR');
                    case 503:
                        throw new ApiError('Registration service unavailable', 'SERVICE_ERROR');
                    default:
                        throw new ApiError(`Server error (${status})`, 'SERVER_ERROR', data);
                }
            }

            throw new ApiError(
                'Registration failed',
                'UNKNOWN_ERROR',
                { originalError: error.message }
            );
        }
    },

    async getCurrentUser(): Promise<User> {
        try {
            const response = await api.get<User>('/auth/me');
            return response.data;
        } catch (error: any) {
            if (error instanceof ApiError) throw error;
            throw new ApiError('Failed to get user info', 'USER_ERROR');
        }
    },

    async logout(): Promise<void> {
        try {
            await api.post('/auth/logout');
        } catch (error: any) {
            // Continue with logout even if request fails
        } finally {
            localStorage.removeItem('token');
        }
    }
};

export default api;