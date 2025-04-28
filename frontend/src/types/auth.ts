export interface RegisterData {
    email: string;
    username: string;
    password: string;
    confirmPassword: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface User {
    id: string;
    email: string;
    username: string;
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
} 