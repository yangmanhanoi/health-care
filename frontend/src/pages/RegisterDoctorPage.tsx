import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterDoctorForm } from '../components/auth/RegisterDoctorForm';

export const RegisterDoctorPage: React.FC = () => {
  const navigate = useNavigate();

  const handleRegistrationSuccess = () => {
    // Navigate to dashboard after successful registration
    navigate('/dashboard');
  };

  return (
    <RegisterDoctorForm onSuccess={handleRegistrationSuccess} />
  );
};
