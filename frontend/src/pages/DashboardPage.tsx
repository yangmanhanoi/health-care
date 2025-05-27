import React from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Heart,
  User,
  LogOut,
  Calendar,
  Plus,
  Clock,
  Stethoscope,
  TestTube,
  Pill,
} from "lucide-react";

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    window.location.href = "/login";
  };

  const handleBookAppointment = () => {
    navigate("/book-appointment");
  };

  const handleManageSchedule = () => {
    navigate("/doctor/schedule");
  };

  const handleViewAppointments = () => {
    if (isDoctor) {
      navigate("/doctor/appointments");
    } else {
      navigate("/appointments");
    }
  };

  const handleDoctorAppointments = () => {
    navigate("/doctor/appointments");
  };

  const handleLabTestManagement = () => {
    navigate("/lab/tests");
  };

  const handlePrescriptionManagement = () => {
    navigate("/prescriptions");
  };

  const isDoctor = user?.roles?.includes("DOCTOR");
  const isPatient = user?.roles?.includes("PATIENT");
  const isLabTechnician =
    user?.roles?.includes("LAB_TECHNICIAN") || user?.roles?.includes("ADMIN");

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
              <Heart className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Healthcare Dashboard
              </h1>
              <p className="text-gray-600">Welcome back, {user?.username}!</p>
            </div>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="flex flex-wrap gap-4">
            {isPatient && (
              <>
                <Button
                  onClick={handleBookAppointment}
                  className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
                >
                  <Plus className="w-4 h-4" />
                  <span>Book Appointment</span>
                </Button>
                <Button
                  onClick={handlePrescriptionManagement}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                >
                  <Pill className="w-4 h-4" />
                  <span>My Prescriptions</span>
                </Button>
              </>
            )}
            {isDoctor && (
              <>
                <Button
                  onClick={handleManageSchedule}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                >
                  <Clock className="w-4 h-4" />
                  <span>Manage Schedule</span>
                </Button>
                <Button
                  onClick={handleDoctorAppointments}
                  className="flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600"
                >
                  <Stethoscope className="w-4 h-4" />
                  <span>Patient Appointments</span>
                </Button>
              </>
            )}
            {isLabTechnician && (
              <Button
                onClick={handleLabTestManagement}
                className="flex items-center space-x-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
              >
                <TestTube className="w-4 h-4" />
                <span>Lab Test Management</span>
              </Button>
            )}
            <Button
              onClick={handleViewAppointments}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Calendar className="w-4 h-4" />
              <span>View Appointments</span>
            </Button>
          </div>
        </div>

        {/* User Info Card */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="w-5 h-5 text-blue-500" />
                <span>Profile Information</span>
              </CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium text-gray-700">Username:</span>
                  <p className="text-gray-900">{user?.username}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Role:</span>
                  <p className="text-gray-900">{user?.roles?.join(", ")}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">User ID:</span>
                  <p className="text-gray-900">{user?.user_id}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-green-600">Welcome!</CardTitle>
              <CardDescription>You have successfully logged in</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">
                This is a simple dashboard to demonstrate the authentication
                system. Your login was successful and you can now access the
                healthcare platform.
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-blue-600">Next Steps</CardTitle>
              <CardDescription>What you can do now</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-gray-700">
                {isPatient && (
                  <>
                    <li>• Book appointments</li>
                    <li>• View medical records</li>
                    <li>• Manage prescriptions</li>
                    <li>• Contact healthcare providers</li>
                  </>
                )}
                {isDoctor && (
                  <>
                    <li>• Manage your schedule</li>
                    <li>• View and manage patient appointments</li>
                    <li>• Update availability</li>
                    <li>• Review patient records and lab results</li>
                    <li>• Diagnose and conclude appointments</li>
                  </>
                )}
                {isLabTechnician && (
                  <>
                    <li>• Manage lab test orders</li>
                    <li>• Upload and update test results</li>
                    <li>• Review test order status</li>
                    <li>• Process sample collections</li>
                  </>
                )}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
