import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import type { LabTestOrder, LabTestOrderItem, TestResult } from "../types/laboratory";
import { LabTestResultForm } from "../components/LabTestResultForm";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import {
  TestTube,
  RefreshCw,
  AlertCircle,
  Search,
  Filter,
  Calendar,
  User,
  FileText,
  CheckCircle,
  Clock,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "../lib/utils";

export const LabTestManagementPage: React.FC = () => {
  const { token, user } = useAuth();
  const [labTestOrders, setLabTestOrders] = useState<LabTestOrder[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<LabTestOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedOrderItem, setSelectedOrderItem] = useState<LabTestOrderItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Check if user is a lab technician
  const isLabTechnician = user?.roles.includes("LAB_TECHNICIAN") || user?.roles.includes("ADMIN");

  useEffect(() => {
    if (isLabTechnician) {
      loadLabTestOrders();
    }
  }, [isLabTechnician]);

  useEffect(() => {
    filterOrders();
  }, [labTestOrders, searchTerm, statusFilter]);

  const loadLabTestOrders = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const orders = await apiService.getLabTestOrders(token);
      setLabTestOrders(orders);
    } catch (err: any) {
      setError(err.message || "Failed to load lab test orders.");
      console.error("Error loading lab test orders:", err);
    } finally {
      setLoading(false);
    }
  };

  const filterOrders = () => {
    let filtered = labTestOrders;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(order =>
        order.id.toString().includes(searchTerm) ||
        order.patient_id.toString().includes(searchTerm) ||
        order.clinical_notes?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.items.some(item =>
          item.test_type_details.name.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by status
    if (statusFilter !== "all") {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    setFilteredOrders(filtered);
  };

  const handleResultUpdated = (result: TestResult) => {
    // Reload the orders to get updated data
    loadLabTestOrders();
    setDialogOpen(false);
    setSelectedOrderItem(null);
  };

  const openResultForm = (orderItem: LabTestOrderItem) => {
    setSelectedOrderItem(orderItem);
    setDialogOpen(true);
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ORDERED":
        return <Clock className="h-4 w-4" />;
      case "SAMPLE_COLLECTED":
        return <TestTube className="h-4 w-4" />;
      case "IN_PROGRESS":
        return <RefreshCw className="h-4 w-4" />;
      case "COMPLETED":
        return <CheckCircle className="h-4 w-4" />;
      case "CANCELLED":
        return <XCircle className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const formatPrice = (price: number | string | undefined) => {
    if (price == null) return "0";
    const numPrice = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(numPrice)) return "0";
    return Math.floor(numPrice).toLocaleString("de-DE");
  };

  if (!user || !isLabTechnician) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center">
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Access Denied
            </h3>
            <p className="text-gray-500">
              Only lab technicians can access this page.
            </p>
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
          <p className="text-gray-500">Loading lab test orders...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="container mx-auto p-6 max-w-4xl">
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-12 text-center">
              <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Error Loading Lab Test Orders
              </h3>
              <p className="text-gray-500 mb-6">{error}</p>
              <Button onClick={loadLabTestOrders}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="container mx-auto p-6 max-w-7xl">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Lab Test Management
              </h1>
              <p className="text-gray-600">
                Manage laboratory test orders and upload results
              </p>
            </div>
            <Button
              onClick={loadLabTestOrders}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </Button>
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by order ID, patient ID, or test name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="ORDERED">Ordered</SelectItem>
                <SelectItem value="SAMPLE_COLLECTED">Sample Collected</SelectItem>
                <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                <SelectItem value="COMPLETED">Completed</SelectItem>
                <SelectItem value="CANCELLED">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Orders List */}
        <div className="space-y-6">
          {filteredOrders.length === 0 ? (
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="p-12 text-center">
                <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Lab Test Orders Found
                </h3>
                <p className="text-gray-500">
                  {searchTerm || statusFilter !== "all"
                    ? "No orders match your current filters."
                    : "No lab test orders available."}
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredOrders.map((order) => (
              <Card key={order.id} className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <TestTube className="h-5 w-5" />
                        Lab Order #{order.id}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-4 mt-2">
                        <span className="flex items-center gap-1">
                          <User className="h-4 w-4" />
                          Patient ID: {order.patient_id}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {new Date(order.request_date).toLocaleDateString()}
                        </span>
                      </CardDescription>
                    </div>
                    <Badge className={cn("text-sm", getStatusColor(order.status))}>
                      {getStatusIcon(order.status)}
                      <span className="ml-1">{order.status.replace(/_/g, " ")}</span>
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  {order.clinical_notes && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-1">Clinical Notes:</p>
                      <p className="text-sm text-gray-600">{order.clinical_notes}</p>
                    </div>
                  )}

                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">Test Items:</h4>
                    {order.items.map((item) => (
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
                                <Badge className={cn("text-xs", getStatusColor(item.status))}>
                                  {item.status.replace(/_/g, " ")}
                                </Badge>
                                <span className="text-sm text-green-600 font-medium">
                                  {formatPrice(item.price)} VND
                                </span>
                                {item.result_details && (
                                  <span className="text-xs text-blue-600">
                                    Result: {item.result_details.result_value} {item.result_details.unit}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                        <Button
                          onClick={() => openResultForm(item)}
                          variant={item.result_details ? "outline" : "default"}
                          size="sm"
                          className="ml-4"
                        >
                          {item.result_details ? "Update Result" : "Upload Result"}
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Result Form Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Lab Test Result</DialogTitle>
              <DialogDescription>
                Upload or update the test result for this lab test order item.
              </DialogDescription>
            </DialogHeader>
            {selectedOrderItem && (
              <LabTestResultForm
                orderItem={selectedOrderItem}
                onResultUpdated={handleResultUpdated}
              />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};
