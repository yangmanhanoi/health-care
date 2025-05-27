import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate, useParams } from "react-router-dom";
import { apiService } from "../services/api";
import type { DetailedAppointment } from "../types/appointment";
import { AppointmentStatus } from "../types/appointment";
import type {
  TestType,
  CreateLabTestOrderRequest,
  LabTestOrderItem,
  TestResult,
  AppointmentTestItemsResponse,
} from "../types/laboratory";
import type {
  PrescriptionItem,
  CreatePrescriptionRequest,
} from "../types/prescription";
import { LabTestSelection } from "../components/LabTestSelection";
import { LabTestResultForm } from "../components/LabTestResultForm";
import { PrescriptionForm } from "../components/PrescriptionForm";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Textarea } from "../components/ui/textarea";
import { Checkbox } from "../components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import {
  ArrowLeft,
  Calendar,
  Clock,
  User,
  Stethoscope,
  RefreshCw,
  Phone,
  Mail,
  MapPin,
  TestTube,
  CheckCircle,
  FileText,
  Activity,
  AlertCircle,
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { cn } from "../lib/utils";
import { toast } from "sonner";

export const DoctorAppointmentDetailPage: React.FC = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const [appointment, setAppointment] = useState<DetailedAppointment | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [diagnoseText, setDiagnoseText] = useState("");
  const [needLabTest, setNeedLabTest] = useState(false);
  const [conclusionText, setConclusionText] = useState("");

  // Prescription states
  const [prescriptionItems, setPrescriptionItems] = useState<PrescriptionItem[]>([]);
  const [needPrescription, setNeedPrescription] = useState(false);

  // Lab test states
  const [selectedTests, setSelectedTests] = useState<TestType[]>([]);
  const [showTestSelection, setShowTestSelection] = useState(false);
  const [creatingLabOrder, setCreatingLabOrder] = useState(false);
  const [labTestItems, setLabTestItems] = useState<LabTestOrderItem[]>([]);
  const [selectedLabTestItem, setSelectedLabTestItem] =
    useState<LabTestOrderItem | null>(null);
  const [labTestDialogOpen, setLabTestDialogOpen] = useState(false);

  // Check if user is a doctor
  useEffect(() => {
    if (user && !user.roles.includes("DOCTOR")) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  // Load appointment details on component mount
  useEffect(() => {
    if (appointmentId) {
      loadAppointmentDetail();
    }
  }, [appointmentId]);

  const loadAppointmentDetail = async () => {
    if (!token || !appointmentId) return;

    try {
      setLoading(true);
      setError(null);
      const detail = await apiService.getDoctorAppointmentDetail(
        parseInt(appointmentId),
        token
      );
      setAppointment(detail);

      // Pre-fill form fields if data exists
      if (detail.diagnose) {
        setDiagnoseText(detail.diagnose);
      }
      if (detail.conclusion) {
        setConclusionText(detail.conclusion);
      }
      setNeedLabTest(detail.need_lab_test || false);

      // Load lab test items if appointment has lab tests
      if (detail.need_lab_test) {
        await loadLabTestItems();
      }
    } catch (err: any) {
      setError(err.message || "Failed to load appointment details.");
      console.error("Error loading appointment detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadLabTestItems = async () => {
    if (!token || !appointmentId) return;

    try {
      const response = await apiService.getAppointmentTestItems(
        parseInt(appointmentId),
        token
      );
      setLabTestItems(response.test_items);
    } catch (err: any) {
      console.error("Error loading lab test items:", err);
      // Don't show error toast for lab test items as it's not critical
    }
  };

  const handleCheckIn = async () => {
    if (!token || !appointmentId) return;

    try {
      setActionLoading("check-in");
      await apiService.checkInAppointment(parseInt(appointmentId), token);
      toast.success("Patient checked in successfully!");
      await loadAppointmentDetail(); // Reload to get updated status
    } catch (err: any) {
      toast.error(err.message || "Failed to check in patient.");
      console.error("Error checking in:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDiagnose = async () => {
    if (!token || !appointmentId || !diagnoseText.trim()) {
      toast.error("Please enter a diagnosis.");
      return;
    }

    // If lab test is needed but no tests selected, show test selection
    if (needLabTest && selectedTests.length === 0) {
      setShowTestSelection(true);
      toast.error("Please select laboratory tests.");
      return;
    }

    try {
      setActionLoading("diagnose");

      // Save diagnosis first
      await apiService.diagnoseAppointment(
        parseInt(appointmentId),
        diagnoseText.trim(),
        needLabTest,
        token
      );

      // If lab tests are needed, create lab test order
      if (needLabTest && selectedTests.length > 0) {
        setCreatingLabOrder(true);
        const labOrderData: CreateLabTestOrderRequest = {
          patient_id: appointment!.patient_id,
          appointment_id: parseInt(appointmentId),
          clinical_notes: diagnoseText.trim(),
          urgency: "routine",
          items: selectedTests.map((test) => ({ test_type: test.id })),
        };

        await apiService.createLabTestOrder(labOrderData, token);
        toast.success("Diagnosis and lab test order created successfully!");
      } else {
        toast.success("Diagnosis saved successfully!");
      }

      await loadAppointmentDetail(); // Reload to get updated status
      setShowTestSelection(false);
    } catch (err: any) {
      toast.error(err.message || "Failed to save diagnosis.");
      console.error("Error diagnosing:", err);
    } finally {
      setActionLoading(null);
      setCreatingLabOrder(false);
    }
  };

  const handleConclude = async () => {
    if (!token || !appointmentId || !conclusionText.trim()) {
      toast.error("Please enter a conclusion.");
      return;
    }

    // If prescription is needed but no items added, show error
    if (needPrescription && prescriptionItems.length === 0) {
      toast.error("Please add medicines to the prescription or uncheck 'Create Prescription'.");
      return;
    }

    try {
      setActionLoading("conclude");

      // Create prescription if needed
      if (needPrescription && prescriptionItems.length > 0) {
        const prescriptionData: CreatePrescriptionRequest = {
          patient_id: appointment!.patient_id,
          diagnose: diagnoseText || conclusionText.trim(),
          items: prescriptionItems.map(item => ({
            medication_id: item.medication_id,
            medication_name: item.medication_name,
            quantity: item.quantity,
            dosage: item.dosage,
            frequency: item.frequency,
            duration: item.duration,
            route: item.route,
            note: item.note,
          })),
        };

        await apiService.createPrescription(prescriptionData, token);
        toast.success("Prescription created successfully!");
      }

      // Conclude the appointment
      await apiService.concludeAppointment(
        parseInt(appointmentId),
        conclusionText.trim(),
        token
      );

      toast.success(
        needPrescription && prescriptionItems.length > 0
          ? "Appointment concluded and prescription created successfully!"
          : "Appointment concluded successfully!"
      );
      await loadAppointmentDetail(); // Reload to get updated status
    } catch (err: any) {
      toast.error(err.message || "Failed to conclude appointment.");
      console.error("Error concluding:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleNeedLabTestChange = (checked: boolean) => {
    setNeedLabTest(checked);
    if (checked) {
      setShowTestSelection(true);
    } else {
      setShowTestSelection(false);
      setSelectedTests([]);
    }
  };

  const handleLabTestResultUpdate = (result: TestResult) => {
    // Reload lab test items to get updated data
    loadLabTestItems();
    setLabTestDialogOpen(false);
    setSelectedLabTestItem(null);
    toast.success("Lab test result updated successfully!");
  };

  const openLabTestResultForm = (labTestItem: LabTestOrderItem) => {
    setSelectedLabTestItem(labTestItem);
    setLabTestDialogOpen(true);
  };

  const handleCompleteLabTest = async () => {
    if (!token || !appointmentId) return;

    try {
      setActionLoading("complete-lab");
      await apiService.completeLabTest(parseInt(appointmentId), token);
      toast.success("Lab test marked as complete!");
      await loadAppointmentDetail(); // Reload to get updated status
    } catch (err: any) {
      toast.error(err.message || "Failed to complete lab test.");
      console.error("Error completing lab test:", err);
    } finally {
      setActionLoading(null);
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

  const formatAppointmentDate = (date: string | null | undefined) => {
    if (!date) return "Unknown date";
    try {
      return format(parseISO(date), "EEEE, MMMM d, yyyy");
    } catch {
      return date;
    }
  };

  const formatAppointmentTime = (time: string | null | undefined) => {
    if (!time) return "Unknown time";
    try {
      const [hours, minutes] = time.split(":");
      return `${hours}:${minutes}`;
    } catch {
      return time;
    }
  };

  const formatPrice = (price: number | string | null | undefined) => {
    if (price == null) return "0";
    const numPrice = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(numPrice)) return "0";
    return Math.floor(numPrice).toLocaleString("de-DE");
  };

  const canCheckIn = () => {
    return (
      appointment?.status === AppointmentStatus.CONFIRMED ||
      appointment?.status === AppointmentStatus.SCHEDULED
    );
  };

  const canDiagnose = () => {
    return appointment?.status === AppointmentStatus.DIAGNOSING;
  };

  const canCompleteLabTest = () => {
    // Can complete lab test if:
    // 1. Appointment is in TESTING status
    // 2. All lab test items have results (are completed)
    if (appointment?.status !== AppointmentStatus.TESTING) {
      return false;
    }

    if (labTestItems.length === 0) {
      return false;
    }

    // Check if all lab test items have results
    return labTestItems.every(
      (item) =>
        item.result_details !== null && item.result_details !== undefined
    );
  };

  const canConclude = () => {
    return appointment?.status === AppointmentStatus.CONCLUDING;
  };

  if (!user || !user.roles.includes("DOCTOR")) {
    return null;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-500">Loading appointment details...</p>
        </div>
      </div>
    );
  }

  if (error || !appointment) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="container mx-auto p-6 max-w-4xl">
          <Button
            variant="ghost"
            onClick={() => navigate("/doctor/appointments")}
            className="mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Appointments
          </Button>

          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-12 text-center">
              <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Error Loading Appointment
              </h3>
              <p className="text-gray-500 mb-6">
                {error || "Appointment not found."}
              </p>
              <Button onClick={() => navigate("/doctor/appointments")}>
                Return to Appointments
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="mb-8">
          {/* Back Button */}
          <Button
            variant="ghost"
            onClick={() => navigate("/doctor/appointments")}
            className="mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Appointments
          </Button>

          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Appointment #{appointment.id} Details
              </h1>
              <p className="text-gray-600">
                Manage appointment status and patient care
              </p>
            </div>
            <Button
              onClick={loadAppointmentDetail}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Status & Actions (Main Column) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
                <CardDescription>
                  Manage appointment status and workflow
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Check In Button */}
                {canCheckIn() && (
                  <Button
                    onClick={handleCheckIn}
                    disabled={actionLoading === "check-in"}
                    className="w-full"
                    size="lg"
                  >
                    {actionLoading === "check-in" ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <CheckCircle className="h-4 w-4 mr-2" />
                    )}
                    Check In Patient
                  </Button>
                )}

                {/* Complete Lab Test Button */}
                {canCompleteLabTest() && (
                  <Button
                    onClick={handleCompleteLabTest}
                    disabled={actionLoading === "complete-lab"}
                    className="w-full"
                    size="lg"
                    variant="outline"
                  >
                    {actionLoading === "complete-lab" ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <TestTube className="h-4 w-4 mr-2" />
                    )}
                    Complete Lab Test
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Diagnosis Form */}
            {canDiagnose() && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Stethoscope className="h-5 w-5" />
                    Diagnosis
                  </CardTitle>
                  <CardDescription>
                    Enter diagnosis and specify if lab test is needed
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Diagnosis
                    </label>
                    <Textarea
                      value={diagnoseText}
                      onChange={(e) => setDiagnoseText(e.target.value)}
                      placeholder="Enter patient diagnosis..."
                      rows={4}
                      className="w-full"
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="needLabTest"
                      checked={needLabTest}
                      onCheckedChange={(checked) =>
                        handleNeedLabTestChange(checked as boolean)
                      }
                    />
                    <label
                      htmlFor="needLabTest"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Lab test required
                    </label>
                  </div>

                  {/* Lab Test Selection */}
                  {showTestSelection && (
                    <div className="mt-4">
                      <LabTestSelection
                        onTestsSelected={setSelectedTests}
                        selectedTests={selectedTests}
                        disabled={actionLoading === "diagnose"}
                      />
                    </div>
                  )}

                  <Button
                    onClick={handleDiagnose}
                    disabled={
                      actionLoading === "diagnose" || !diagnoseText.trim()
                    }
                    className="w-full"
                    size="lg"
                  >
                    {actionLoading === "diagnose" ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <FileText className="h-4 w-4 mr-2" />
                    )}
                    {creatingLabOrder
                      ? "Creating Lab Order..."
                      : needLabTest && selectedTests.length > 0
                      ? "Save Diagnosis & Create Lab Order"
                      : "Save Diagnosis"}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Conclusion Form */}
            {canConclude() && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Conclusion
                  </CardTitle>
                  <CardDescription>
                    Enter final conclusion and create prescription if needed
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Conclusion
                    </label>
                    <Textarea
                      value={conclusionText}
                      onChange={(e) => setConclusionText(e.target.value)}
                      placeholder="Enter appointment conclusion..."
                      rows={4}
                      className="w-full"
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="needPrescription"
                      checked={needPrescription}
                      onCheckedChange={(checked) =>
                        setNeedPrescription(checked as boolean)
                      }
                    />
                    <label
                      htmlFor="needPrescription"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Create prescription for patient
                    </label>
                  </div>

                  {/* Prescription Form */}
                  {needPrescription && (
                    <div className="border-t pt-6">
                      <PrescriptionForm
                        prescriptionItems={prescriptionItems}
                        onItemsChange={setPrescriptionItems}
                        disabled={actionLoading === "conclude"}
                      />
                    </div>
                  )}

                  <Button
                    onClick={handleConclude}
                    disabled={
                      actionLoading === "conclude" ||
                      !conclusionText.trim() ||
                      (needPrescription && prescriptionItems.length === 0)
                    }
                    className="w-full"
                    size="lg"
                  >
                    {actionLoading === "conclude" ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <CheckCircle className="h-4 w-4 mr-2" />
                    )}
                    {needPrescription && prescriptionItems.length > 0
                      ? "Complete Appointment & Create Prescription"
                      : "Complete Appointment"}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Lab Test Results Management */}
            {appointment?.need_lab_test && labTestItems.length > 0 && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TestTube className="h-5 w-5" />
                    Lab Test Results
                  </CardTitle>
                  <CardDescription>
                    Manage and update laboratory test results
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Completion Status */}
                  <div className="mb-4 p-3 rounded-lg bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-700">
                          Progress:
                        </span>
                        <span className="text-sm text-gray-600">
                          {
                            labTestItems.filter((item) => item.result_details)
                              .length
                          }{" "}
                          of {labTestItems.length} tests completed
                        </span>
                      </div>
                      {canCompleteLabTest() && (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Ready to Complete
                        </Badge>
                      )}
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${
                            (labTestItems.filter((item) => item.result_details)
                              .length /
                              labTestItems.length) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {labTestItems.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <div>
                              <h5 className="font-medium text-gray-900">
                                {item.test_type_details.name}
                              </h5>
                              <p className="text-sm text-gray-600">
                                {item.test_type_details.description}
                              </p>
                              <div className="flex items-center gap-4 mt-1">
                                <Badge
                                  className={cn(
                                    "text-xs",
                                    item.status === "COMPLETED"
                                      ? "bg-green-100 text-green-800"
                                      : item.status === "IN_PROGRESS"
                                      ? "bg-orange-100 text-orange-800"
                                      : "bg-blue-100 text-blue-800"
                                  )}
                                >
                                  {item.status.replace(/_/g, " ")}
                                </Badge>
                                <span className="text-sm text-green-600 font-medium">
                                  {formatPrice(item.price)} VND
                                </span>
                                {item.result_details && (
                                  <span className="text-xs text-blue-600">
                                    Result: {item.result_details.result_value}{" "}
                                    {item.result_details.unit}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                        <Button
                          onClick={() => openLabTestResultForm(item)}
                          variant={item.result_details ? "outline" : "default"}
                          size="sm"
                          className="ml-4"
                        >
                          {item.result_details ? "Update Result" : "Add Result"}
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Status Info */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-sm">Current Status</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge
                  className={cn(
                    "text-sm font-medium w-full justify-center py-2",
                    getStatusColor(appointment.status)
                  )}
                >
                  {appointment.status.replace(/_/g, " ")}
                </Badge>

                <div className="mt-4 text-xs text-gray-500 space-y-1">
                  <p>
                    <strong>Created:</strong>{" "}
                    {appointment.created_at
                      ? format(
                          parseISO(appointment.created_at),
                          "MMM d, yyyy 'at' h:mm a"
                        )
                      : "Unknown"}
                  </p>
                  <p>
                    <strong>Updated:</strong>{" "}
                    {appointment.updated_at
                      ? format(
                          parseISO(appointment.updated_at),
                          "MMM d, yyyy 'at' h:mm a"
                        )
                      : "Unknown"}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Patient & Appointment Info */}
          <div className="space-y-6">
            {/* Patient Information */}
            {appointment.patient_info && (
              <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Patient Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Name</p>
                      <p className="text-lg">
                        {appointment.patient_info.fullName}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        Date of Birth
                      </p>
                      <p className="text-lg">{appointment.patient_info.dob}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        Gender
                      </p>
                      <p className="text-lg">
                        {appointment.patient_info.gender}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-gray-500" />
                      <span>{appointment.patient_info.phone}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-gray-500" />
                      <span>{appointment.patient_info.email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-gray-500" />
                      <span>{appointment.patient_info.address}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Appointment Details */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Appointment Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700">Date</p>
                    <p className="text-lg">
                      {formatAppointmentDate(appointment.date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Time</p>
                    <p className="text-lg">
                      {formatAppointmentTime(appointment.time)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Status</p>
                    <Badge
                      className={cn(
                        "text-sm font-medium",
                        getStatusColor(appointment.status)
                      )}
                    >
                      {appointment.status.replace(/_/g, " ")}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Lab Test Required
                    </p>
                    <p className="text-lg">
                      {appointment.need_lab_test ? "Yes" : "No"}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Base Price
                    </p>
                    <p className="text-lg text-green-600">
                      {formatPrice(appointment.price)} VND
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Total Price
                    </p>
                    <p className="text-lg text-green-600 font-semibold">
                      {formatPrice(
                        appointment.total_price || appointment.price
                      )}{" "}
                      VND
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Medical Information */}
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Stethoscope className="h-5 w-5" />
                  Medical Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {appointment.diagnose && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Diagnosis
                    </p>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-gray-700">{appointment.diagnose}</p>
                    </div>
                  </div>
                )}
                {appointment.conclusion && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Conclusion
                    </p>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-gray-700">{appointment.conclusion}</p>
                    </div>
                  </div>
                )}
                {!appointment.diagnose && !appointment.conclusion && (
                  <p className="text-gray-500 italic">
                    No medical information recorded yet.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Lab Test Results */}
            {appointment.test_results &&
              appointment.test_results.length > 0 && (
                <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TestTube className="h-5 w-5" />
                      Lab Test Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {appointment.test_results.map((test, index) => (
                        <div key={index} className="bg-gray-50 p-4 rounded-lg">
                          <div className="grid grid-cols-1 gap-2">
                            <div>
                              <p className="text-sm font-medium text-gray-700">
                                Test Type
                              </p>
                              <p>{test.test_type}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-700">
                                Status
                              </p>
                              <p>{test.status}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-700">
                                Result
                              </p>
                              <p>{test.result}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-700">
                                Price
                              </p>
                              <p className="text-green-600">
                                {formatPrice(test.price)} VND
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
          </div>
        </div>

        {/* Lab Test Result Dialog */}
        <Dialog open={labTestDialogOpen} onOpenChange={setLabTestDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Lab Test Result</DialogTitle>
              <DialogDescription>
                Upload or update the test result for this lab test.
              </DialogDescription>
            </DialogHeader>
            {selectedLabTestItem && (
              <LabTestResultForm
                orderItem={selectedLabTestItem}
                onResultUpdated={handleLabTestResultUpdate}
              />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};
