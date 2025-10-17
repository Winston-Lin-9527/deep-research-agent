
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
  FormHelperText
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate password match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const response = await fetch('http://localhost:2024/api/v1/auth/register', {
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
        setError(errorData.detail || 'Registration failed');
        console.log(errorData);
      }
    } catch (error) {
      setError('An error occurred during registration');
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleClickShowConfirmPassword = () => {
    setShowConfirmPassword(!showConfirmPassword);
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
          Create your account
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
          onSubmit={handleRegister} 
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
          
          <FormControl 
            variant="outlined" 
            margin="normal" 
            required 
            fullWidth
          >
            <InputLabel htmlFor="confirmPassword">Confirm Password</InputLabel>
            <OutlinedInput
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle confirm password visibility"
                    onClick={handleClickShowConfirmPassword}
                    onMouseDown={handleMouseDownPassword}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Confirm Password"
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
            Sign Up
          </Button>
          
          <Box 
            sx={{ 
              textAlign: 'center', 
              mt: 2 
            }}
          >
            <Typography variant="body2">
              Already have an account?{' '}
              <Link 
                to="/login" 
                style={{ 
                  textDecoration: 'none',
                  color: '#1976d2',
                  fontWeight: 500
                }}
              >
                Sign in
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default RegisterPage;
