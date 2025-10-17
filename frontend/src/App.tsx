import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ChatApp } from './components/ChatApp';
import WelcomePage from './pages/WelcomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppRoutes />
      </div>
    </AuthProvider>
  );
}

function AppRoutes() {
  const { token } = useAuth();
  const isAuthenticated = !!token;

  return (
    <Routes>
      {isAuthenticated ? (
        <>
          <Route path="/" element={<ChatApp />} />
          <Route path="*" element={<Navigate to="/" />} />
        </>
      ) : (
        <>
          <Route path="/welcome" element={<WelcomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<Navigate to="/welcome" />} />
        </>
      )}
    </Routes>
  );
}

export default App;
