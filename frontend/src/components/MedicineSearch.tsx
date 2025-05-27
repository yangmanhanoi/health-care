import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import type { Medicine, MedicineSearchResult } from "../types/prescription";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Search,
  RefreshCw,
  AlertCircle,
  Plus,
  Pill,
  DollarSign,
  Package,
  X,
} from "lucide-react";
import { cn } from "../lib/utils";
import { toast } from "sonner";

interface MedicineSearchProps {
  onMedicineSelected: (medicine: Medicine) => void;
  disabled?: boolean;
}

export const MedicineSearch: React.FC<MedicineSearchProps> = ({
  onMedicineSelected,
  disabled = false,
}) => {
  const { token } = useAuth();
  const [allMedicines, setAllMedicines] = useState<MedicineSearchResult[]>([]);
  const [filteredMedicines, setFilteredMedicines] = useState<MedicineSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);

  // Load all medicines when dialog opens
  useEffect(() => {
    if (dialogOpen && allMedicines.length === 0) {
      loadAllMedicines();
    }
  }, [dialogOpen]);

  // Filter medicines when search query changes
  useEffect(() => {
    filterMedicines();
  }, [searchQuery, allMedicines]);

  const loadAllMedicines = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const results = await apiService.searchMedications(undefined, token);
      setAllMedicines(results);
    } catch (err: any) {
      setError(err.message || "Failed to load medicines.");
      console.error("Error loading medicines:", err);
      toast.error("Failed to load medicines");
    } finally {
      setLoading(false);
    }
  };

  const filterMedicines = () => {
    if (!searchQuery.trim()) {
      setFilteredMedicines(allMedicines);
      return;
    }

    const query = searchQuery.toLowerCase().trim();
    const filtered = allMedicines.filter(medicine =>
      medicine.name.toLowerCase().includes(query) ||
      (medicine.description && medicine.description.toLowerCase().includes(query)) ||
      (medicine.manufacturer && medicine.manufacturer.toLowerCase().includes(query)) ||
      (medicine.dosage_form && medicine.dosage_form.toLowerCase().includes(query))
    );
    setFilteredMedicines(filtered);
  };

  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const clearSearch = () => {
    setSearchQuery("");
  };

  const handleMedicineSelect = (medicine: Medicine) => {
    onMedicineSelected(medicine);
    setDialogOpen(false);
    toast.success(`Added ${medicine.name} to prescription`);
  };

  const formatPrice = (price: number | string | null | undefined) => {
    if (price == null) return "0";
    const numPrice = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(numPrice)) return "0";
    return Math.floor(numPrice).toLocaleString("de-DE");
  };

  return (
    <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          disabled={disabled}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Medicine
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="flex items-center gap-2">
                <Pill className="h-5 w-5" />
                Search Medicines
              </DialogTitle>
              <DialogDescription>
                Search and select medicines to add to the prescription
              </DialogDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadAllMedicines}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Summary */}
          {!loading && allMedicines.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Pill className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-900">
                    {allMedicines.length} medicines available
                  </span>
                </div>
                {searchQuery && (
                  <span className="text-sm text-blue-700">
                    {filteredMedicines.length} matching your search
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Search Bar */}
          <div className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search medicines by name, description, manufacturer..."
                value={searchQuery}
                onChange={handleSearchInputChange}
                disabled={loading}
                className="pl-10 pr-10"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearSearch}
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Error State */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <span>{error}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
              <p className="text-gray-500">Searching medicines...</p>
            </div>
          )}

          {/* Medicine Results */}
          {!loading && filteredMedicines.length > 0 && (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredMedicines.map((medicine) => {
                const isOutOfStock = medicine.quantity <= 0;
                return (
                <Card
                  key={medicine.id}
                  className={cn(
                    "transition-all duration-200 border-2 border-transparent",
                    isOutOfStock
                      ? "opacity-60 cursor-not-allowed bg-gray-50"
                      : "hover:bg-blue-50 hover:border-blue-200 cursor-pointer"
                  )}
                  onClick={() => !isOutOfStock && handleMedicineSelect(medicine)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Pill className="h-5 w-5 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 text-lg">
                              {medicine.name}
                            </h4>
                            {medicine.description && (
                              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                {medicine.description}
                              </p>
                            )}
                            <div className="flex items-center gap-3 mt-2 flex-wrap">
                              {medicine.strength && (
                                <Badge variant="secondary" className="text-xs">
                                  💊 {medicine.strength}
                                </Badge>
                              )}
                              {medicine.dosage_form && (
                                <Badge variant="outline" className="text-xs">
                                  📋 {medicine.dosage_form}
                                </Badge>
                              )}
                              {medicine.manufacturer && (
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                  🏭 {medicine.manufacturer}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="flex items-center gap-2 text-green-600 font-semibold text-lg">
                          <DollarSign className="h-5 w-5" />
                          {formatPrice(medicine.price)} VND
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <div className={cn(
                            "flex items-center gap-1 text-sm px-2 py-1 rounded-full",
                            medicine.quantity > 10
                              ? "bg-green-100 text-green-700"
                              : medicine.quantity > 0
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-red-100 text-red-700"
                          )}>
                            <Package className="h-3 w-3" />
                            Stock: {medicine.quantity}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          className="mt-2 w-full"
                          disabled={isOutOfStock}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (!isOutOfStock) {
                              handleMedicineSelect(medicine);
                            }
                          }}
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          {isOutOfStock ? "Out of Stock" : "Select"}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                );
              })}
            </div>
          )}

          {/* No Results */}
          {!loading && filteredMedicines.length === 0 && allMedicines.length > 0 && !error && (
            <div className="text-center py-8">
              <Pill className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                No medicines found matching "{searchQuery}"
              </p>
              <Button
                variant="outline"
                onClick={clearSearch}
                className="mt-2"
              >
                Clear Search
              </Button>
            </div>
          )}

          {/* Initial State */}
          {!loading && allMedicines.length === 0 && !error && (
            <div className="text-center py-8">
              <Pill className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                Loading available medicines...
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
