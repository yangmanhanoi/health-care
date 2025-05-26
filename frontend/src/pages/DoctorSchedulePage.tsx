import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type {
  Availability,
  CreateAvailabilityRequest,
  Doctor,
} from "../types/doctor";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Calendar } from "../components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../components/ui/popover";
import { CalendarIcon, Plus, Trash2, Clock, ArrowLeft } from "lucide-react";
import { format, addDays, startOfDay } from "date-fns";
import { cn } from "../lib/utils";
import { toast } from "sonner";

export const DoctorSchedulePage: React.FC = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [availabilities, setAvailabilities] = useState<Availability[]>([]);
  const [doctorProfile, setDoctorProfile] = useState<Doctor | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date>();
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  // Check if user is a doctor
  const isDoctor = user?.roles.includes("DOCTOR");

  useEffect(() => {
    if (!isDoctor || !token || !user?.user_id) return;
    loadDoctorData();
  }, [isDoctor, token, user?.user_id]);

  const loadDoctorData = async () => {
    if (!token || !user?.user_id) return;

    try {
      setIsLoading(true);

      // First, get the doctor profile to get the doctor table ID
      const profile = await apiService.getDoctorProfile(user.user_id);
      setDoctorProfile(profile);

      // Then load availabilities
      const data = await apiService.getMyAvailabilities(token);
      setAvailabilities(data);
    } catch (error) {
      console.error("Error loading doctor data:", error);
      toast.error("Failed to load your profile and schedule");
    } finally {
      setIsLoading(false);
    }
  };

  const loadAvailabilities = async () => {
    if (!token) return;

    try {
      const data = await apiService.getMyAvailabilities(token);
      setAvailabilities(data);
    } catch (error) {
      console.error("Error loading availabilities:", error);
      toast.error("Failed to load your schedule");
    }
  };

  const handleCreateAvailability = async () => {
    if (!token || !selectedDate || !startTime || !endTime) {
      toast.error("Please fill in all fields");
      return;
    }

    // Get doctor ID from the doctor profile
    if (!doctorProfile?.id) {
      toast.error("Doctor profile not loaded. Please refresh the page.");
      return;
    }

    try {
      setIsCreating(true);

      const createData: CreateAvailabilityRequest = {
        doctor: doctorProfile.id, // Use the doctor table ID, not user_id
        date: format(selectedDate, "yyyy-MM-dd"),
        start_time: startTime,
        end_time: endTime,
      };

      await apiService.createAvailability(createData, token);
      toast.success("Time slot added successfully");

      // Reset form
      setSelectedDate(undefined);
      setStartTime("");
      setEndTime("");

      // Reload availabilities
      await loadAvailabilities();
    } catch (error: any) {
      console.error("Error creating availability:", error);
      toast.error(error.message || "Failed to add time slot");
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteAvailability = async (id: number) => {
    if (!token) return;

    try {
      await apiService.deleteAvailability(id, token);
      toast.success("Time slot deleted successfully");
      await loadAvailabilities();
    } catch (error: any) {
      console.error("Error deleting availability:", error);
      toast.error(error.message || "Failed to delete time slot");
    }
  };

  // Generate time slots from 9:00 to 17:00 in 30-minute intervals
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 9; hour < 17; hour++) {
      slots.push(`${hour.toString().padStart(2, "0")}:00`);
      slots.push(`${hour.toString().padStart(2, "0")}:30`);
    }
    slots.push("17:00"); // Add final slot
    return slots;
  };

  const timeSlots = generateTimeSlots();

  // Group availabilities by date
  const groupedAvailabilities = availabilities.reduce((acc, availability) => {
    const date = availability.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(availability);
    return acc;
  }, {} as Record<string, Availability[]>);

  if (!isDoctor) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              Access denied. This page is only available for doctors.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="container mx-auto px-4 py-8">
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

          <h1 className="text-3xl font-bold text-gray-900">
            Manage Your Schedule
          </h1>
          <p className="text-gray-600 mt-2">
            Add and manage your available time slots for patient appointments.
          </p>
          {doctorProfile && (
            <div className="mt-4 p-4 bg-white/80 backdrop-blur-sm rounded-lg border">
              <h2 className="text-lg font-semibold text-gray-900">
                Dr. {doctorProfile.full_name}
              </h2>
              <p className="text-sm text-gray-600">
                {doctorProfile.specialty} • License:{" "}
                {doctorProfile.license_number}
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Add New Time Slot */}
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Add New Time Slot
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
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
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={setSelectedDate}
                      disabled={(date) => date < startOfDay(new Date())}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start-time">Start Time</Label>
                  <select
                    id="start-time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full px-3 py-2 border border-input bg-background rounded-md"
                  >
                    <option value="">Select start time</option>
                    {timeSlots.slice(0, -1).map((time) => (
                      <option key={time} value={time}>
                        {time}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="end-time">End Time</Label>
                  <select
                    id="end-time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full px-3 py-2 border border-input bg-background rounded-md"
                  >
                    <option value="">Select end time</option>
                    {timeSlots.slice(1).map((time) => (
                      <option key={time} value={time}>
                        {time}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <Button
                onClick={handleCreateAvailability}
                disabled={isCreating || !selectedDate || !startTime || !endTime}
                className="w-full"
              >
                {isCreating ? "Adding..." : "Add Time Slot"}
              </Button>
            </CardContent>
          </Card>

          {/* Current Schedule */}
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Your Current Schedule
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <p className="text-center text-muted-foreground">
                  Loading schedule...
                </p>
              ) : Object.keys(groupedAvailabilities).length === 0 ? (
                <p className="text-center text-muted-foreground">
                  No time slots scheduled yet. Add your first time slot to get
                  started.
                </p>
              ) : (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {Object.entries(groupedAvailabilities)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([date, slots]) => (
                      <div key={date} className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2">
                          {format(new Date(date), "EEEE, MMMM d, yyyy")}
                        </h4>
                        <div className="space-y-2">
                          {slots
                            .sort((a, b) =>
                              a.start_time.localeCompare(b.start_time)
                            )
                            .map((slot) => (
                              <div
                                key={slot.id}
                                className="flex items-center justify-between bg-muted p-2 rounded"
                              >
                                <span className="text-sm">
                                  {slot.start_time} - {slot.end_time}
                                </span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    handleDeleteAvailability(slot.id)
                                  }
                                  className="text-destructive hover:text-destructive"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
