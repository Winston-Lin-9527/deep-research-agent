
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Paper, 
  Typography, 
  Button, 
  Box, 
} from '@mui/material';
import { useAuth } from '../context/AuthContext';

const WelcomePage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  
  // If already authenticated, redirect to chat
  React.useEffect(() => {
    if (token) {
      navigate('/');
    }
  }, [token, navigate]);

  return (
    <Container 
      component="main" 
      maxWidth="md"
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        py: 4
      }}
    >
      <Paper 
        elevation={6} 
        sx={{ 
          padding: 6, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          width: '100%',
          textAlign: 'center'
        }}
      >
        <Typography 
          component="h1" 
          variant="h3" 
          gutterBottom
          sx={{
            fontWeight: 'bold',
            color: 'primary.main',
            mb: 3
          }}
        >
          Welcome to Deep Research
        </Typography>
        
        <Typography 
          variant="h6" 
          color="textSecondary" 
          gutterBottom
          sx={{ mb: 4, maxWidth: '600px' }}
        >
          Your AI-powered research assistant that helps you dive deep into complex topics with intelligent analysis.
        </Typography>
        
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' }, 
            gap: 2, 
            width: '100%', 
            maxWidth: 400,
            mt: 2
          }}
        >
          <Button
            component={Link}
            to="/login"
            variant="outlined"
            size="large"
            fullWidth
            sx={{ 
              py: 1.5,
              fontSize: '1.1rem'
            }}
          >
            Sign In
          </Button>
          
          <Button
            component={Link}
            to="/register"
            variant="contained"
            size="large"
            fullWidth
            sx={{ 
              py: 1.5,
              fontSize: '1.1rem'
            }}
          >
            Create Account
          </Button>
        </Box>
      </Paper>
      
      <Box 
        sx={{ 
          mt: 4, 
          textAlign: 'center', 
          color: 'text.secondary',
          maxWidth: '600px'
        }}
      >
        <Typography variant="body2">
          Winston Lin © 2025. All rights reserved.
        </Typography>
      </Box>
    </Container>
  );
};

export default WelcomePage;
