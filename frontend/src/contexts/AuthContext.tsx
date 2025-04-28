import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthState, LoginCredentials, RegisterData } from '../types/auth';
import { authService } from '../services/api';

interface AuthContextType extends AuthState {
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [state, setState] = useState<AuthState>({
        user: null,
        token: localStorage.getItem('token'),
        isAuthenticated: false,
        isLoading: true,
        error: null,
    });

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const user = await authService.getCurrentUser();
                    setState(prev => ({
                        ...prev,
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    }));
                } catch (error) {
                    localStorage.removeItem('token');
                    setState(prev => ({
                        ...prev,
                        isLoading: false,
                    }));
                }
            } else {
                setState(prev => ({
                    ...prev,
                    isLoading: false,
                }));
            }
        };

        initAuth();
    }, []);

    const login = async (credentials: LoginCredentials) => {
        try {
            const response = await authService.login(credentials);
            localStorage.setItem('token', response.access_token);
            const user = await authService.getCurrentUser();
            setState(prev => ({
                ...prev,
                user,
                token: response.access_token,
                isAuthenticated: true,
                error: null,
            }));
        } catch (error) {
            setState(prev => ({
                ...prev,
                error: 'Invalid credentials',
            }));
            throw error;
        }
    };

    const register = async (data: RegisterData) => {
        setState(prev => ({
            ...prev,
            error: null,
            isLoading: true
        }));

        try {
            console.log('Starting registration process...');
            
            // Validate password match
            if (data.password !== data.confirmPassword) {
                throw new Error('Passwords do not match');
            }

            // Attempt registration
            const user = await authService.register(data);
            console.log('Registration successful, attempting automatic login...');
            
            try {
                // Attempt automatic login
                await login({ 
                    username: data.username, // Changed from email to username
                    password: data.password 
                });
                console.log('Automatic login successful');
                
                setState(prev => ({
                    ...prev,
                    error: null,
                    isLoading: false
                }));
            } catch (loginError: any) {
                console.error('Automatic login failed:', loginError);
                
                // More descriptive error message
                const errorMessage = loginError.code === 'NETWORK_ERROR' 
                    ? 'Network error during login. Please try logging in manually.'
                    : 'Registration successful but automatic login failed. Please login manually.';
                
                setState(prev => ({
                    ...prev,
                    error: errorMessage,
                    isLoading: false,
                    user: null,
                    token: null,
                    isAuthenticated: false
                }));
            }
        } catch (error: any) {
            console.error('Registration error:', error);
            
            // Enhanced error message handling
            let errorMessage = 'Registration failed';
            
            if (error.code === 'VALIDATION_ERROR') {
                errorMessage = Object.values(error.details || {}).join(', ');
            } else if (error.code === 'DUPLICATE_ERROR') {
                errorMessage = 'An account with this email or username already exists';
            } else if (error.code === 'NETWORK_ERROR') {
                errorMessage = 'Network error. Please check your connection and try again';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            setState(prev => ({
                ...prev,
                error: errorMessage,
                isLoading: false,
                user: null,
                token: null,
                isAuthenticated: false
            }));
            
            throw error;
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
            setState({
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
            });
        } catch (error) {
            setState(prev => ({
                ...prev,
                error: 'Logout failed',
            }));
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{ ...state, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 