import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    // Redirect to dashboard or home page after successful login
    navigate('/dashboard');
  };

  return <LoginForm onSuccess={handleLoginSuccess} />;
};
