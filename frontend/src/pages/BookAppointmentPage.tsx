import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type { Doctor, Availability } from "../types/doctor";
import type { CreateAppointmentRequest } from "../types/appointment";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
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
import { Calendar } from "../components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../components/ui/popover";
import {
  CalendarIcon,
  Search,
  Clock,
  User,
  Stethoscope,
  ArrowLeft,
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "../lib/utils";

export const BookAppointmentPage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [availabilities, setAvailabilities] = useState<Availability[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date>();
  const [selectedTime, setSelectedTime] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSpecialty, setSelectedSpecialty] = useState("all");
  const [loading, setLoading] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Get unique specialties from doctors
  const specialties = Array.from(
    new Set(doctors.map((doctor) => doctor.specialty))
  );

  // Load doctors on component mount
  useEffect(() => {
    loadDoctors();
  }, []);

  // Load doctors with search filters
  const loadDoctors = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        ...(searchTerm && { search: searchTerm }),
        ...(selectedSpecialty &&
          selectedSpecialty !== "all" && { specialty: selectedSpecialty }),
      };
      const doctorList = await apiService.searchDoctors(params);
      setDoctors(doctorList);
    } catch (err: any) {
      setError(err.message || "Failed to load doctors. Please try again.");
      console.error("Error loading doctors:", err);
    } finally {
      setLoading(false);
    }
  };

  // Load doctor availabilities when doctor and date are selected
  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      loadAvailabilities();
    }
  }, [selectedDoctor, selectedDate]);

  const loadAvailabilities = async () => {
    if (!selectedDoctor || !selectedDate) return;

    try {
      setLoading(true);
      setError(null);
      const dateString = format(selectedDate, "yyyy-MM-dd");
      const availabilityList = await apiService.getDoctorAvailabilities({
        doctor_id: selectedDoctor.user_id,
        date: dateString,
      });
      setAvailabilities(availabilityList);
    } catch (err: any) {
      setError(
        err.message || "Failed to load doctor availability. Please try again."
      );
      console.error("Error loading availabilities:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadDoctors();
  };

  const handleDoctorSelect = (doctor: Doctor) => {
    setSelectedDoctor(doctor);
    setAvailabilities([]);
    setSelectedTime("");
    setSelectedDate(undefined);
  };

  const handleBookAppointment = async () => {
    if (!selectedDoctor || !selectedDate || !selectedTime || !token) {
      setError("Please select a doctor, date, and time slot.");
      return;
    }

    try {
      setBookingLoading(true);
      setError(null);
      setSuccess(null);

      // Convert time from HH:MM:SS format to HH:MM format
      const formattedTime = selectedTime.substring(0, 5); // Extract first 5 characters (HH:MM)

      const appointmentData: CreateAppointmentRequest = {
        doctor_id: selectedDoctor.user_id.toString(),
        date: format(selectedDate, "yyyy-MM-dd"),
        time: formattedTime,
      };

      await apiService.createAppointment(appointmentData, token);
      setSuccess("Appointment booked successfully!");

      // Reset form
      setSelectedDoctor(null);
      setSelectedDate(undefined);
      setSelectedTime("");
      setAvailabilities([]);
    } catch (err: any) {
      setError(err.message || "Failed to book appointment. Please try again.");
      console.error("Error booking appointment:", err);
    } finally {
      setBookingLoading(false);
    }
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

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Book an Appointment
          </h1>
          <p className="text-gray-600">
            Find a doctor and schedule your appointment
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Doctor Search Section */}
          <div className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Find a Doctor
                </CardTitle>
                <CardDescription>
                  Search for doctors by name or specialty
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Search by doctor name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="flex-1"
                  />
                  <Button onClick={handleSearch} disabled={loading}>
                    <Search className="h-4 w-4" />
                  </Button>
                </div>

                <Select
                  value={selectedSpecialty}
                  onValueChange={setSelectedSpecialty}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by specialty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Specialties</SelectItem>
                    {specialties.map((specialty) => (
                      <SelectItem key={specialty} value={specialty}>
                        {specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Doctor List */}
            <div className="space-y-3">
              {loading && (
                <div className="text-center py-8">
                  <p className="text-gray-500">Loading doctors...</p>
                </div>
              )}

              {!loading && doctors.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-500">
                    No doctors found. Try adjusting your search.
                  </p>
                </div>
              )}

              {doctors.map((doctor) => (
                <Card
                  key={doctor.id}
                  className={cn(
                    "cursor-pointer transition-all hover:shadow-md shadow-lg border-0 bg-white/80 backdrop-blur-sm",
                    selectedDoctor?.id === doctor.id &&
                      "ring-2 ring-blue-500 bg-blue-50/80"
                  )}
                  onClick={() => handleDoctorSelect(doctor)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-blue-100 rounded-full">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {doctor.full_name}
                        </h3>
                        <div className="flex items-center gap-1 text-sm text-gray-600 mt-1">
                          <Stethoscope className="h-4 w-4" />
                          {doctor.specialty}
                        </div>
                        {doctor.contact && (
                          <p className="text-sm text-gray-500 mt-1">
                            {doctor.contact}
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Appointment Booking Section */}
          <div className="space-y-6">
            {selectedDoctor && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CalendarIcon className="h-5 w-5" />
                    Schedule Appointment
                  </CardTitle>
                  <CardDescription>
                    Book an appointment with Dr. {selectedDoctor.full_name}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Date Selection */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Select Date
                    </label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !selectedDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {selectedDate
                            ? format(selectedDate, "PPP")
                            : "Pick a date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={selectedDate}
                          onSelect={setSelectedDate}
                          disabled={(date) => date < new Date()}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  {/* Time Slot Selection */}
                  {selectedDate && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Available Time Slots
                      </label>
                      {loading ? (
                        <p className="text-gray-500">
                          Loading available times...
                        </p>
                      ) : availabilities.length === 0 ? (
                        <p className="text-gray-500">
                          No available time slots for this date.
                        </p>
                      ) : (
                        <div className="grid grid-cols-2 gap-2">
                          {availabilities.map((availability) => (
                            <Button
                              key={availability.id}
                              variant={
                                selectedTime === availability.start_time
                                  ? "default"
                                  : "outline"
                              }
                              size="sm"
                              onClick={() =>
                                setSelectedTime(availability.start_time)
                              }
                              className="justify-start"
                            >
                              <Clock className="mr-2 h-4 w-4" />
                              {availability.start_time} -{" "}
                              {availability.end_time}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Book Button */}
                  {selectedDate && selectedTime && (
                    <Button
                      onClick={handleBookAppointment}
                      disabled={bookingLoading}
                      className="w-full"
                      size="lg"
                    >
                      {bookingLoading ? "Booking..." : "Book Appointment"}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}

            {!selectedDoctor && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardContent className="p-8 text-center">
                  <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select a Doctor
                  </h3>
                  <p className="text-gray-500">
                    Choose a doctor from the list to view available appointment
                    slots.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
