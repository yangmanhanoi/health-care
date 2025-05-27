import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RegisterDoctorPage } from "./pages/RegisterDoctorPage";
import { DashboardPage } from "./pages/DashboardPage";
import { BookAppointmentPage } from "./pages/BookAppointmentPage";
import { ViewAppointmentsPage } from "./pages/ViewAppointmentsPage";
import { DoctorSchedulePage } from "./pages/DoctorSchedulePage";
import { DoctorAppointmentsPage } from "./pages/DoctorAppointmentsPage";
import { DoctorAppointmentDetailPage } from "./pages/DoctorAppointmentDetailPage";
import { LabTestManagementPage } from "./pages/LabTestManagementPage";
import { PrescriptionManagementPage } from "./pages/PrescriptionManagementPage";
import { Toaster } from "./components/ui/sonner";

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, token } = useAuth();

  if (!user || !token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirect to dashboard if already logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, token } = useAuth();

  if (user && token) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register/doctor"
        element={
          <PublicRoute>
            <RegisterDoctorPage />
          </PublicRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/book-appointment"
        element={
          <ProtectedRoute>
            <BookAppointmentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/appointments"
        element={
          <ProtectedRoute>
            <ViewAppointmentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctor/schedule"
        element={
          <ProtectedRoute>
            <DoctorSchedulePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctor/appointments"
        element={
          <ProtectedRoute>
            <DoctorAppointmentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctor/appointments/:appointmentId"
        element={
          <ProtectedRoute>
            <DoctorAppointmentDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/lab/tests"
        element={
          <ProtectedRoute>
            <LabTestManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/prescriptions"
        element={
          <ProtectedRoute>
            <PrescriptionManagementPage />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
          <Toaster />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
