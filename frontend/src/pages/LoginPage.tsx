
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  Alert,
  FormControl,
  InputLabel,
  OutlinedInput,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:2024/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        login(data.access_token);
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (error) {
      setError('An error occurred during login');
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  return (
    <Container 
      component="main" 
      maxWidth="xs"
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}
    >
      <Paper 
        elevation={6} 
        sx={{ 
          padding: 4, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          width: '100%'
        }}
      >
        <Typography component="h1" variant="h5" gutterBottom>
          Sign in to your account
        </Typography>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              width: '100%', 
              mb: 2 
            }}
          >
            {error}
          </Alert>
        )}
        
        <Box 
          component="form" 
          onSubmit={handleLogin} 
          sx={{ 
            width: '100%', 
            mt: 1 
          }}
        >
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          
          <FormControl 
            variant="outlined" 
            margin="normal" 
            required 
            fullWidth
          >
            <InputLabel htmlFor="password">Password</InputLabel>
            <OutlinedInput
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    onMouseDown={handleMouseDownPassword}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Password"
            />
          </FormControl>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ 
              mt: 3, 
              mb: 2,
              py: 1.5
            }}
          >
            Sign In
          </Button>
          
          <Box 
            sx={{ 
              textAlign: 'center', 
              mt: 2 
            }}
          >
            <Typography variant="body2">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                style={{ 
                  textDecoration: 'none',
                  color: '#1976d2',
                  fontWeight: 500
                }}
              >
                Register here
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage;
