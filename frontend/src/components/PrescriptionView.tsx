import React from "react";
import type { Prescription } from "../types/prescription";
import { PrescriptionStatus } from "../types/prescription";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Calendar,
  User,
  Stethoscope,
  Pill,
  Clock,
  FileText,
  AlertCircle,
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { cn } from "../lib/utils";

interface PrescriptionViewProps {
  prescription: Prescription;
  showPatientInfo?: boolean;
  showDoctorInfo?: boolean;
  className?: string;
}

export const PrescriptionView: React.FC<PrescriptionViewProps> = ({
  prescription,
  showPatientInfo = false,
  showDoctorInfo = false,
  className,
}) => {
  const getStatusColor = (status: PrescriptionStatus) => {
    switch (status) {
      case PrescriptionStatus.DRAFT:
        return "text-gray-600 bg-gray-50";
      case PrescriptionStatus.ACTIVE:
        return "text-green-600 bg-green-50";
      case PrescriptionStatus.PENDING_DISPENSING:
        return "text-orange-600 bg-orange-50";
      case PrescriptionStatus.DISPENSED:
        return "text-blue-600 bg-blue-50";
      case PrescriptionStatus.CANCELLED:
        return "text-red-600 bg-red-50";
      case PrescriptionStatus.EXPIRED:
        return "text-gray-600 bg-gray-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), "EEEE, MMMM d, yyyy 'at' h:mm a");
    } catch {
      return dateString;
    }
  };

  return (
    <Card className={cn("shadow-lg border-0 bg-white/80 backdrop-blur-sm", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Prescription #{prescription.id}
            </CardTitle>
            <CardDescription>
              Created on {formatDate(prescription.created_at)}
            </CardDescription>
          </div>
          <Badge
            className={cn(
              "text-sm font-medium",
              getStatusColor(prescription.status)
            )}
          >
            {prescription.status.replace(/_/g, " ")}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-700 mb-1">Date</p>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span>{formatDate(prescription.date)}</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700 mb-1">Status</p>
            <Badge
              className={cn(
                "text-sm font-medium",
                getStatusColor(prescription.status)
              )}
            >
              {prescription.status.replace(/_/g, " ")}
            </Badge>
          </div>
          {showPatientInfo && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Patient ID</p>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-500" />
                <span>{prescription.patient_id}</span>
              </div>
            </div>
          )}
          {showDoctorInfo && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Doctor ID</p>
              <div className="flex items-center gap-2">
                <Stethoscope className="h-4 w-4 text-gray-500" />
                <span>{prescription.doctor_id}</span>
              </div>
            </div>
          )}
        </div>

        {/* Diagnosis */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Diagnosis</p>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-gray-700">{prescription.diagnose}</p>
          </div>
        </div>

        {/* Prescription Items */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-3">
            Prescribed Medicines ({prescription.items.length})
          </p>
          {prescription.items.length > 0 ? (
            <div className="space-y-3">
              {prescription.items.map((item, index) => (
                <Card key={item.id || index} className="border-l-4 border-l-blue-500">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 flex items-center gap-2">
                          <Pill className="h-4 w-4 text-blue-500" />
                          {item.medication_name}
                        </h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Quantity:</span> {item.quantity}
                          </div>
                          <div>
                            <span className="font-medium">Dosage:</span> {item.dosage}
                          </div>
                          <div>
                            <span className="font-medium">Frequency:</span> {item.frequency}
                          </div>
                          <div>
                            <span className="font-medium">Duration:</span> {item.duration}
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-2">
                          <Badge variant="outline" className="text-xs">
                            Route: {item.route}
                          </Badge>
                          {item.note && (
                            <span className="text-xs text-gray-500">
                              Note: {item.note}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <Pill className="h-8 w-8 text-gray-300 mx-auto mb-2" />
              <p>No medicines prescribed</p>
            </div>
          )}
        </div>

        {/* Timestamps */}
        <div className="border-t pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-500">
            <div>
              <span className="font-medium">Created:</span>{" "}
              {formatDate(prescription.created_at)}
            </div>
            <div>
              <span className="font-medium">Last Updated:</span>{" "}
              {formatDate(prescription.updated_at)}
            </div>
          </div>
        </div>

        {/* Status-specific Information */}
        {prescription.status === PrescriptionStatus.EXPIRED && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm font-medium">
                This prescription has expired and is no longer valid.
              </span>
            </div>
          </div>
        )}

        {prescription.status === PrescriptionStatus.CANCELLED && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm font-medium">
                This prescription has been cancelled.
              </span>
            </div>
          </div>
        )}

        {prescription.status === PrescriptionStatus.DISPENSED && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-blue-600">
              <Clock className="h-4 w-4" />
              <span className="text-sm font-medium">
                This prescription has been dispensed by the pharmacy.
              </span>
            </div>
          </div>
        )}

        {prescription.status === PrescriptionStatus.PENDING_DISPENSING && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-orange-600">
              <Clock className="h-4 w-4" />
              <span className="text-sm font-medium">
                This prescription is pending dispensing at the pharmacy.
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
