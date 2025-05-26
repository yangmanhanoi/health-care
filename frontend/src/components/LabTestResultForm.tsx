import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import type {
  LabTestOrderItem,
  TestResult,
  CreateTestResultRequest,
  UpdateTestResultRequest,
} from "../types/laboratory";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import {
  TestTube,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  FileText,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "../lib/utils";

interface LabTestResultFormProps {
  orderItem: LabTestOrderItem;
  onResultUpdated?: (result: TestResult) => void;
  disabled?: boolean;
}

export const LabTestResultForm: React.FC<LabTestResultFormProps> = ({
  orderItem,
  onResultUpdated,
  disabled = false,
}) => {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreateTestResultRequest>({
    result_value: "",
    normal_range: "",
    unit: "",
    technician_notes: "",
  });

  // Check if user is a lab technician or doctor
  const canUpdateResults =
    user?.roles.includes("LAB_TECHNICIAN") ||
    user?.roles.includes("ADMIN") ||
    user?.roles.includes("DOCTOR");

  useEffect(() => {
    // Pre-fill form with existing result data if available
    if (orderItem.result_details) {
      setFormData({
        result_value: orderItem.result_details.result_value || "",
        normal_range: orderItem.result_details.normal_range || "",
        unit: orderItem.result_details.unit || "",
        technician_notes: orderItem.result_details.technician_notes || "",
      });
    } else {
      // Pre-fill with test type defaults
      setFormData({
        result_value: "",
        normal_range: orderItem.test_type_details.normal_range || "",
        unit: orderItem.test_type_details.unit || "",
        technician_notes: "",
      });
    }
  }, [orderItem]);

  const handleInputChange = (
    field: keyof CreateTestResultRequest,
    value: string
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token || !canUpdateResults) {
      toast.error("You don't have permission to update test results.");
      return;
    }

    if (!formData.result_value.trim()) {
      toast.error("Please enter a result value.");
      return;
    }

    try {
      setLoading(true);
      let result: TestResult;

      if (orderItem.result_details) {
        // Update existing result
        const updateData: UpdateTestResultRequest = {
          result_value: formData.result_value,
          normal_range: formData.normal_range,
          unit: formData.unit,
          technician_notes: formData.technician_notes,
        };
        result = await apiService.updateTestResult(
          orderItem.result_details.id,
          updateData,
          token
        );
        toast.success("Test result updated successfully!");
      } else {
        // Create new result
        result = await apiService.uploadTestResult(
          orderItem.id,
          formData,
          token
        );
        toast.success("Test result uploaded successfully!");
      }

      if (onResultUpdated) {
        onResultUpdated(result);
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to save test result.");
      console.error("Error saving test result:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ORDERED":
        return "bg-blue-100 text-blue-800";
      case "SAMPLE_COLLECTED":
        return "bg-yellow-100 text-yellow-800";
      case "IN_PROGRESS":
        return "bg-orange-100 text-orange-800";
      case "COMPLETED":
        return "bg-green-100 text-green-800";
      case "CANCELLED":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatPrice = (price: number | string | undefined) => {
    if (price == null) return "0";
    const numPrice = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(numPrice)) return "0";
    return Math.floor(numPrice).toLocaleString("de-DE");
  };

  if (!canUpdateResults) {
    return (
      <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="text-center">
            <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-400" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Access Denied
            </h3>
            <p className="text-gray-500">
              Only lab technicians and doctors can update test results.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TestTube className="h-5 w-5" />
          {orderItem.result_details
            ? "Update Test Result"
            : "Upload Test Result"}
        </CardTitle>
        <CardDescription>{orderItem.test_type_details.name}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Test Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-700">Test Type</p>
              <p className="text-lg">{orderItem.test_type_details.name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Status</p>
              <Badge
                className={cn("text-sm", getStatusColor(orderItem.status))}
              >
                {orderItem.status.replace(/_/g, " ")}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Price</p>
              <p className="text-green-600 font-medium">
                {formatPrice(orderItem.price)} VND
              </p>
            </div>
            {orderItem.test_type_details.description && (
              <div className="md:col-span-2">
                <p className="text-sm font-medium text-gray-700">Description</p>
                <p className="text-sm text-gray-600">
                  {orderItem.test_type_details.description}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Result Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Result Value *
              </label>
              <Input
                value={formData.result_value}
                onChange={(e) =>
                  handleInputChange("result_value", e.target.value)
                }
                placeholder="Enter test result value"
                disabled={disabled || loading}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Unit
              </label>
              <Input
                value={formData.unit}
                onChange={(e) => handleInputChange("unit", e.target.value)}
                placeholder="e.g., mg/dL, %, mmol/L"
                disabled={disabled || loading}
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Normal Range
            </label>
            <Input
              value={formData.normal_range}
              onChange={(e) =>
                handleInputChange("normal_range", e.target.value)
              }
              placeholder="e.g., 70-100, <5.0, Normal"
              disabled={disabled || loading}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Technician Notes
            </label>
            <Textarea
              value={formData.technician_notes}
              onChange={(e) =>
                handleInputChange("technician_notes", e.target.value)
              }
              placeholder="Additional notes or observations..."
              rows={3}
              disabled={disabled || loading}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="submit"
              disabled={disabled || loading || !formData.result_value.trim()}
              className="flex items-center gap-2"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : orderItem.result_details ? (
                <Save className="h-4 w-4" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
              {loading
                ? "Saving..."
                : orderItem.result_details
                ? "Update Result"
                : "Upload Result"}
            </Button>
          </div>
        </form>

        {/* Existing Result Display */}
        {orderItem.result_details && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="h-4 w-4 text-blue-600" />
              <h4 className="font-medium text-blue-900">Current Result</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div>
                <span className="font-medium text-blue-700">Value:</span>{" "}
                {orderItem.result_details.result_value}{" "}
                {orderItem.result_details.unit}
              </div>
              <div>
                <span className="font-medium text-blue-700">Normal Range:</span>{" "}
                {orderItem.result_details.normal_range || "Not specified"}
              </div>
              {orderItem.result_details.technician_notes && (
                <div className="md:col-span-2">
                  <span className="font-medium text-blue-700">Notes:</span>{" "}
                  {orderItem.result_details.technician_notes}
                </div>
              )}
              <div className="md:col-span-2 text-xs text-blue-600">
                Last updated:{" "}
                {new Date(orderItem.result_details.updated_at).toLocaleString()}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
