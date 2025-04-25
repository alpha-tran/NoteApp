import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Button,
    Paper,
    AppBar,
    Toolbar,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login');
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Dashboard
                    </Typography>
                    <Button color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Paper sx={{ p: 4 }}>
                    <Typography variant="h4" gutterBottom>
                        Welcome, {user?.username}!
                    </Typography>
                    <Typography variant="body1" paragraph>
                        You are now logged in to your account.
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Email: {user?.email}
                    </Typography>
                </Paper>
            </Container>
        </Box>
    );
}; 