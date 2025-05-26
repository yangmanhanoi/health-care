import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type { Appointment } from "../types/appointment";
import { AppointmentStatus } from "../types/appointment";
import type { Doctor } from "../types/doctor";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import {
  ArrowLeft,
  Calendar,
  Clock,
  User,
  Stethoscope,
  Filter,
  RefreshCw,
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { cn } from "../lib/utils";

export const ViewAppointmentsPage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filteredAppointments, setFilteredAppointments] = useState<
    Appointment[]
  >([]);
  const [doctors, setDoctors] = useState<Record<string, Doctor>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("date");

  // Load appointments on component mount
  useEffect(() => {
    loadAppointments();
  }, []);

  // Filter and sort appointments when filters change
  useEffect(() => {
    filterAndSortAppointments();
  }, [appointments, statusFilter, sortBy, doctors]);

  const loadAppointments = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const appointmentList = await apiService.getPatientAppointments(token);
      setAppointments(appointmentList);

      // Load doctor information for each appointment
      const doctorPromises = appointmentList.map(async (appointment) => {
        try {
          const doctor = await apiService.getDoctorByUserId(
            parseInt(appointment.doctor_id)
          );
          return { doctorId: appointment.doctor_id, doctor };
        } catch (err) {
          console.error(`Failed to load doctor ${appointment.doctor_id}:`, err);
          return null;
        }
      });

      const doctorResults = await Promise.all(doctorPromises);
      const doctorsMap: Record<string, Doctor> = {};

      doctorResults.forEach((result) => {
        if (result) {
          doctorsMap[result.doctorId] = result.doctor;
        }
      });

      setDoctors(doctorsMap);
    } catch (err: any) {
      setError(err.message || "Failed to load appointments. Please try again.");
      console.error("Error loading appointments:", err);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortAppointments = () => {
    let filtered = [...appointments];

    // Apply status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(
        (appointment) => appointment.status === statusFilter
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "date":
          const dateA = new Date(
            `${a.date || "1970-01-01"} ${a.time || "00:00"}`
          );
          const dateB = new Date(
            `${b.date || "1970-01-01"} ${b.time || "00:00"}`
          );
          return dateB.getTime() - dateA.getTime(); // Most recent first
        case "status":
          return a.status.localeCompare(b.status);
        case "doctor":
          const doctorA = doctors[a.doctor_id]?.full_name || a.doctor_id;
          const doctorB = doctors[b.doctor_id]?.full_name || b.doctor_id;
          return doctorA.localeCompare(doctorB);
        default:
          return 0;
      }
    });

    setFilteredAppointments(filtered);
  };

  const getStatusBadgeVariant = (status: AppointmentStatus) => {
    switch (status) {
      case AppointmentStatus.SCHEDULED:
        return "default";
      case AppointmentStatus.CONFIRMED:
        return "secondary";
      case AppointmentStatus.DIAGNOSING:
      case AppointmentStatus.TESTING:
      case AppointmentStatus.CONCLUDING:
        return "outline";
      case AppointmentStatus.FINISHED:
        return "secondary";
      case AppointmentStatus.CANCELED:
      case AppointmentStatus.DENIED:
      case AppointmentStatus.REJECTED:
        return "destructive";
      default:
        return "default";
    }
  };

  const getStatusColor = (status: AppointmentStatus) => {
    switch (status) {
      case AppointmentStatus.SCHEDULED:
        return "text-blue-600 bg-blue-50";
      case AppointmentStatus.CONFIRMED:
        return "text-green-600 bg-green-50";
      case AppointmentStatus.DIAGNOSING:
      case AppointmentStatus.TESTING:
      case AppointmentStatus.CONCLUDING:
        return "text-orange-600 bg-orange-50";
      case AppointmentStatus.FINISHED:
        return "text-emerald-600 bg-emerald-50";
      case AppointmentStatus.CANCELED:
      case AppointmentStatus.DENIED:
      case AppointmentStatus.REJECTED:
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const formatAppointmentDate = (date: string) => {
    if (!date) return "Unknown date";
    try {
      return format(parseISO(date), "EEEE, MMMM d, yyyy");
    } catch {
      return date;
    }
  };

  const formatAppointmentTime = (time: string) => {
    if (!time) return "Unknown time";
    try {
      // Handle both HH:MM and HH:MM:SS formats
      const [hours, minutes] = time.split(":");
      return `${hours}:${minutes}`;
    } catch {
      return time;
    }
  };

  const formatPrice = (price: number) => {
    // Format price in Vietnamese style with dots as thousand separators
    return Math.floor(price).toLocaleString("de-DE"); // German locale uses dots for thousands
  };

  const getUniqueStatuses = () => {
    const statuses = Array.from(new Set(appointments.map((apt) => apt.status)));
    return statuses;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="mb-8">
          {/* Back Button */}
          <Button
            variant="ghost"
            onClick={() => navigate("/dashboard")}
            className="mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>

          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                My Appointments
              </h1>
              <p className="text-gray-600">
                View and manage your healthcare appointments
              </p>
            </div>
            <Button
              onClick={loadAppointments}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Filters */}
        <Card className="mb-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters & Sorting
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Filter by Status
                </label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="All statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    {getUniqueStatuses().map((status) => (
                      <SelectItem key={status} value={status}>
                        {status.replace(/_/g, " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex-1 min-w-[200px]">
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Sort by
                </label>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="date">Date & Time</SelectItem>
                    <SelectItem value="status">Status</SelectItem>
                    <SelectItem value="doctor">Doctor Name</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Appointments List */}
        {loading && (
          <div className="text-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
            <p className="text-gray-500">Loading appointments...</p>
          </div>
        )}

        {!loading && filteredAppointments.length === 0 && (
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-12 text-center">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No appointments found
              </h3>
              <p className="text-gray-500 mb-6">
                {statusFilter !== "all"
                  ? `No appointments with status "${statusFilter.replace(
                      /_/g,
                      " "
                    )}" found.`
                  : "You haven't booked any appointments yet."}
              </p>
              {statusFilter === "all" && (
                <Button
                  onClick={() => navigate("/book-appointment")}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
                >
                  Book Your First Appointment
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {!loading && filteredAppointments.length > 0 && (
          <div className="space-y-4">
            {filteredAppointments.map((appointment) => (
              <Card
                key={appointment.id}
                className="shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-shadow"
              >
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-full">
                        <Stethoscope className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          Appointment #{appointment.id}
                        </h3>
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <User className="h-4 w-4" />
                          {doctors[appointment.doctor_id] ? (
                            <div>
                              <span className="font-medium">
                                Dr. {doctors[appointment.doctor_id].full_name}
                              </span>
                              <span className="text-gray-500 ml-2">
                                ({doctors[appointment.doctor_id].specialty})
                              </span>
                            </div>
                          ) : (
                            <span>Doctor ID: {appointment.doctor_id}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <Badge
                      className={cn(
                        "px-3 py-1 text-sm font-medium",
                        getStatusColor(appointment.status)
                      )}
                    >
                      {appointment.status.replace(/_/g, " ")}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Date</p>
                        <p className="font-medium">
                          {formatAppointmentDate(appointment.date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Time</p>
                        <p className="font-medium">
                          {formatAppointmentTime(appointment.time)}
                        </p>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Price</p>
                      <p className="font-medium text-green-600">
                        {appointment.price
                          ? `${formatPrice(appointment.price)} VND`
                          : "0 VND"}
                      </p>
                    </div>
                  </div>

                  {(appointment.diagnose || appointment.conclusion) && (
                    <div className="border-t pt-4 space-y-2">
                      {appointment.diagnose && (
                        <div>
                          <p className="text-sm font-medium text-gray-700">
                            Diagnosis:
                          </p>
                          <p className="text-sm text-gray-600">
                            {appointment.diagnose}
                          </p>
                        </div>
                      )}
                      {appointment.conclusion && (
                        <div>
                          <p className="text-sm font-medium text-gray-700">
                            Conclusion:
                          </p>
                          <p className="text-sm text-gray-600">
                            {appointment.conclusion}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex justify-between items-center mt-4 pt-4 border-t">
                    <div className="text-sm text-gray-500">
                      Created:{" "}
                      {appointment.created_at
                        ? format(
                            parseISO(appointment.created_at),
                            "MMM d, yyyy 'at' h:mm a"
                          )
                        : "Unknown"}
                    </div>
                    <div className="flex gap-2">
                      {appointment.status === AppointmentStatus.SCHEDULED && (
                        <Button variant="outline" size="sm">
                          Request Cancellation
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {!loading && appointments.length > 0 && (
          <Card className="mt-8 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Appointment Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-blue-600">
                    {appointments.length}
                  </p>
                  <p className="text-sm text-gray-600">Total Appointments</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {
                      appointments.filter(
                        (apt) => apt.status === AppointmentStatus.FINISHED
                      ).length
                    }
                  </p>
                  <p className="text-sm text-gray-600">Completed</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-orange-600">
                    {
                      appointments.filter((apt) =>
                        [
                          AppointmentStatus.SCHEDULED,
                          AppointmentStatus.CONFIRMED,
                        ].includes(apt.status)
                      ).length
                    }
                  </p>
                  <p className="text-sm text-gray-600">Upcoming</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-600">
                    {
                      appointments.filter((apt) =>
                        [
                          AppointmentStatus.CANCELED,
                          AppointmentStatus.DENIED,
                        ].includes(apt.status)
                      ).length
                    }
                  </p>
                  <p className="text-sm text-gray-600">Cancelled</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
