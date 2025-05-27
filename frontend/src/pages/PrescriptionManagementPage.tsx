import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type { Prescription } from "../types/prescription";
import { PrescriptionStatus } from "../types/prescription";
import { PrescriptionView } from "../components/PrescriptionView";
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
  RefreshCw,
  Filter,
  FileText,
  AlertCircle,
  Calendar,
  Pill,
} from "lucide-react";
import { cn } from "../lib/utils";
import { toast } from "sonner";

export const PrescriptionManagementPage: React.FC = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [filteredPrescriptions, setFilteredPrescriptions] = useState<Prescription[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Check if user is a patient
  useEffect(() => {
    if (user && !user.roles.includes("PATIENT") && !user.roles.includes("customer")) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  // Load prescriptions on component mount
  useEffect(() => {
    if (user && token) {
      loadPrescriptions();
    }
  }, [user, token]);

  // Filter prescriptions when status filter changes
  useEffect(() => {
    filterPrescriptions();
  }, [prescriptions, statusFilter]);

  const loadPrescriptions = async () => {
    const userId = user?.id || user?.user_id;
    if (!token || !user || !userId) return;

    try {
      setLoading(true);
      setError(null);
      console.log("Current user:", user);
      console.log("Fetching prescriptions for user ID:", userId);
      const data = await apiService.getPatientPrescriptions(userId, token);
      setPrescriptions(data);
    } catch (err: any) {
      setError(err.message || "Failed to load prescriptions.");
      console.error("Error loading prescriptions:", err);
      console.error("User ID used:", userId);
      toast.error("Failed to load prescriptions");
    } finally {
      setLoading(false);
    }
  };

  const filterPrescriptions = () => {
    let filtered = [...prescriptions];

    if (statusFilter !== "all") {
      filtered = filtered.filter(
        (prescription) => prescription.status === statusFilter
      );
    }

    // Sort by creation date (newest first)
    filtered.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    setFilteredPrescriptions(filtered);
  };

  const getStatusCounts = () => {
    const counts = {
      all: prescriptions.length,
      [PrescriptionStatus.ACTIVE]: 0,
      [PrescriptionStatus.PENDING_DISPENSING]: 0,
      [PrescriptionStatus.DISPENSED]: 0,
      [PrescriptionStatus.CANCELLED]: 0,
      [PrescriptionStatus.EXPIRED]: 0,
    };

    prescriptions.forEach((prescription) => {
      if (counts[prescription.status] !== undefined) {
        counts[prescription.status]++;
      }
    });

    return counts;
  };

  // Show access denied message instead of white screen
  if (!user || (!user.id && !user.user_id) || (!user.roles.includes("PATIENT") && !user.roles.includes("customer"))) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center">
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Access Denied
            </h3>
            <p className="text-gray-500 mb-4">
              Only patients can access this page.
            </p>
            <Button
              onClick={() => navigate("/dashboard")}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-500">Loading your prescriptions...</p>
        </div>
      </div>
    );
  }

  const statusCounts = getStatusCounts();

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
                My Prescriptions
              </h1>
              <p className="text-gray-600">
                View and manage your medical prescriptions
              </p>
            </div>
            <Button
              onClick={loadPrescriptions}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <Card className="text-center">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {statusCounts.all}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {statusCounts[PrescriptionStatus.ACTIVE]}
              </div>
              <div className="text-sm text-gray-600">Active</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-orange-600">
                {statusCounts[PrescriptionStatus.PENDING_DISPENSING]}
              </div>
              <div className="text-sm text-gray-600">Pending</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {statusCounts[PrescriptionStatus.DISPENSED]}
              </div>
              <div className="text-sm text-gray-600">Dispensed</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-gray-600">
                {statusCounts[PrescriptionStatus.CANCELLED] + statusCounts[PrescriptionStatus.EXPIRED]}
              </div>
              <div className="text-sm text-gray-600">Inactive</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Prescriptions</SelectItem>
                    <SelectItem value={PrescriptionStatus.ACTIVE}>Active</SelectItem>
                    <SelectItem value={PrescriptionStatus.PENDING_DISPENSING}>
                      Pending Dispensing
                    </SelectItem>
                    <SelectItem value={PrescriptionStatus.DISPENSED}>Dispensed</SelectItem>
                    <SelectItem value={PrescriptionStatus.CANCELLED}>Cancelled</SelectItem>
                    <SelectItem value={PrescriptionStatus.EXPIRED}>Expired</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error State */}
        {error && (
          <Card className="border-red-200 bg-red-50 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Prescriptions List */}
        {filteredPrescriptions.length > 0 ? (
          <div className="space-y-6">
            {filteredPrescriptions.map((prescription) => (
              <PrescriptionView
                key={prescription.id}
                prescription={prescription}
                showDoctorInfo={true}
              />
            ))}
          </div>
        ) : (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Prescriptions Found
              </h3>
              <p className="text-gray-500 mb-6">
                {statusFilter === "all"
                  ? "You don't have any prescriptions yet."
                  : `No prescriptions found with status "${statusFilter.replace(/_/g, " ")}".`}
              </p>
              {statusFilter !== "all" && (
                <Button
                  variant="outline"
                  onClick={() => setStatusFilter("all")}
                >
                  Show All Prescriptions
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
