import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterForm } from '../components/auth/RegisterForm';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const handleRegisterSuccess = () => {
    // Redirect to dashboard or home page after successful registration
    navigate('/dashboard');
  };

  return <RegisterForm onSuccess={handleRegisterSuccess} />;
};
