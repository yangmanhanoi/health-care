import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import type { TestType, SelectedTestType } from "../types/laboratory";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import {
  TestTube,
  RefreshCw,
  AlertCircle,
  Search,
  DollarSign,
} from "lucide-react";
import { Input } from "./ui/input";

interface LabTestSelectionProps {
  onTestsSelected: (selectedTests: TestType[]) => void;
  selectedTests: TestType[];
  disabled?: boolean;
}

export const LabTestSelection: React.FC<LabTestSelectionProps> = ({
  onTestsSelected,
  selectedTests,
  disabled = false,
}) => {
  const { token } = useAuth();
  const [testTypes, setTestTypes] = useState<SelectedTestType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadTestTypes();
  }, []);

  useEffect(() => {
    // Update selected state when selectedTests prop changes
    setTestTypes((prevTests) =>
      prevTests.map((test) => ({
        ...test,
        selected: selectedTests.some((selected) => selected.id === test.id),
      }))
    );
  }, [selectedTests]);

  const loadTestTypes = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const types = await apiService.getTestTypes(token);
      const typesWithSelection = types.map((type) => ({
        ...type,
        cost: typeof type.cost === "string" ? parseFloat(type.cost) : type.cost,
        selected: selectedTests.some((selected) => selected.id === type.id),
      }));
      setTestTypes(typesWithSelection);
    } catch (err: any) {
      setError(err.message || "Failed to load test types.");
      console.error("Error loading test types:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestToggle = (testType: TestType) => {
    if (disabled) return;

    const updatedTests = testTypes.map((test) =>
      test.id === testType.id ? { ...test, selected: !test.selected } : test
    );
    setTestTypes(updatedTests);

    // Get currently selected tests
    const currentlySelected = updatedTests
      .filter((test) => test.selected)
      .map((test) => ({
        id: test.id,
        name: test.name,
        description: test.description,
        cost: typeof test.cost === "string" ? parseFloat(test.cost) : test.cost,
        unit: test.unit,
        normal_range: test.normal_range,
        created_at: test.created_at,
        updated_at: test.updated_at,
      }));

    onTestsSelected(currentlySelected);
  };

  const formatPrice = (price: number | string | undefined) => {
    if (price == null || price === undefined) return "0";
    const numPrice = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(numPrice)) return "0";
    return Math.floor(numPrice).toLocaleString("de-DE");
  };

  const getTotalCost = () => {
    return testTypes
      .filter((test) => test.selected)
      .reduce((total, test) => {
        const cost =
          typeof test.cost === "string" ? parseFloat(test.cost) : test.cost;
        return total + (isNaN(cost) ? 0 : cost);
      }, 0);
  };

  const filteredTests = testTypes.filter(
    (test) =>
      test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (test.description &&
        test.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="text-center">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-blue-500" />
            <p className="text-gray-500">Loading available tests...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="text-center">
            <AlertCircle className="h-6 w-6 mx-auto mb-2 text-red-400" />
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadTestTypes} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
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
          Select Laboratory Tests
        </CardTitle>
        <CardDescription>
          Choose the tests required for this patient's diagnosis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search tests..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
            disabled={disabled}
          />
        </div>

        {/* Selected Tests Summary */}
        {testTypes.some((test) => test.selected) && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-blue-900">Selected Tests</h4>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {testTypes.filter((test) => test.selected).length} test(s)
              </Badge>
            </div>
            <div className="flex items-center gap-2 text-sm text-blue-700">
              <DollarSign className="h-4 w-4" />
              <span>Total Cost: {formatPrice(getTotalCost())} VND</span>
            </div>
          </div>
        )}

        {/* Test List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredTests.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              {searchTerm
                ? "No tests found matching your search."
                : "No tests available."}
            </p>
          ) : (
            filteredTests.map((test) => (
              <div
                key={test.id}
                className={`border rounded-lg p-4 transition-colors ${
                  test.selected
                    ? "border-blue-200 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                } ${
                  disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
                }`}
                onClick={() => handleTestToggle(test)}
              >
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={test.selected}
                    onChange={() => handleTestToggle(test)}
                    disabled={disabled}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">{test.name}</h4>
                      <span className="text-green-600 font-medium">
                        {formatPrice(test.cost)} VND
                      </span>
                    </div>
                    {test.description && (
                      <p className="text-sm text-gray-600 mt-1">
                        {test.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      {test.unit && <span>Unit: {test.unit}</span>}
                      {test.normal_range && (
                        <span>Normal Range: {test.normal_range}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center pt-4 border-t">
          <Button
            onClick={loadTestTypes}
            variant="outline"
            size="sm"
            disabled={loading || disabled}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
            />
            Refresh Tests
          </Button>

          {testTypes.some((test) => test.selected) && (
            <div className="text-sm text-gray-600">
              {testTypes.filter((test) => test.selected).length} test(s)
              selected
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
