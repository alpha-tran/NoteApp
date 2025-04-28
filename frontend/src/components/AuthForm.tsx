import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    TextField,
    Button,
    Typography,
    Link,
    Alert,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

interface AuthFormProps {
    mode: 'login' | 'register';
}

export const AuthForm: React.FC<AuthFormProps> = ({ mode }) => {
    const navigate = useNavigate();
    const { login, register } = useAuth();
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        
        try {
            setError(null);
            setLoading(true);

            if (mode === 'register') {
                const password = formData.get('password') as string;
                const confirmPassword = formData.get('confirmPassword') as string;

                if (password !== confirmPassword) {
                    setError('Passwords do not match');
                    return;
                }

                await register({
                    username: formData.get('username') as string,
                    email: formData.get('email') as string,
                    password: password,
                    confirmPassword: confirmPassword
                });
            } else {
                await login({
                    username: formData.get('email') as string,
                    password: formData.get('password') as string,
                });
            }

            navigate('/dashboard');
        } catch (err) {
            setError(mode === 'login' ? 'Invalid email or password' : 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Typography component="h1" variant="h5">
                    {mode === 'login' ? 'Sign in' : 'Sign up'}
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}
                    {mode === 'register' && (
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="username"
                            label="Username"
                            name="username"
                            autoComplete="username"
                            autoFocus
                        />
                    )}
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="email"
                        label="Email Address"
                        name="email"
                        autoComplete="email"
                        autoFocus={mode === 'login'}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Password"
                        type="password"
                        id="password"
                        autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                    />
                    {mode === 'register' && (
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="confirmPassword"
                            label="Confirm Password"
                            type="password"
                            id="confirmPassword"
                            autoComplete="new-password"
                        />
                    )}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading}
                    >
                        {loading ? (mode === 'login' ? 'Signing in...' : 'Signing up...') : (mode === 'login' ? 'Sign In' : 'Sign Up')}
                    </Button>
                    <Box sx={{ textAlign: 'center' }}>
                        <Link href={mode === 'login' ? '/register' : '/login'} variant="body2">
                            {mode === 'login' ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
                        </Link>
                    </Box>
                </Box>
            </Box>
        </Container>
    );
}; 