import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthState, LoginCredentials, RegisterData, AuthResponse } from '../types';
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
        try {
            const user = await authService.register(data);
            setState(prev => ({
                ...prev,
                error: null,
            }));
            await login({ username: data.email, password: data.password });
        } catch (error) {
            setState(prev => ({
                ...prev,
                error: 'Registration failed',
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