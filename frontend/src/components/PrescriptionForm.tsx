import React, { useState } from "react";
import type { Medicine, PrescriptionItem } from "../types/prescription";
import { MedicineSearch } from "./MedicineSearch";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Badge } from "./ui/badge";
import {
  Trash2,
  Pill,
  Plus,
  AlertCircle,
  DollarSign,
} from "lucide-react";
import { cn } from "../lib/utils";

interface PrescriptionFormProps {
  prescriptionItems: PrescriptionItem[];
  onItemsChange: (items: PrescriptionItem[]) => void;
  disabled?: boolean;
}

export const PrescriptionForm: React.FC<PrescriptionFormProps> = ({
  prescriptionItems,
  onItemsChange,
  disabled = false,
}) => {
  const [editingItem, setEditingItem] = useState<PrescriptionItem | null>(null);
  const [editingIndex, setEditingIndex] = useState<number>(-1);

  // Form state for editing/adding items
  const [formData, setFormData] = useState({
    quantity: 1,
    dosage: "",
    frequency: "",
    duration: "",
    route: "oral",
    note: "",
  });

  const handleMedicineSelected = (medicine: Medicine) => {
    const newItem: PrescriptionItem = {
      medication_id: medicine.id,
      medication_name: medicine.name,
      quantity: 1,
      dosage: "1 tablet",
      frequency: "twice daily",
      duration: "7 days",
      route: "oral",
      note: "",
    };

    setEditingItem(newItem);
    setEditingIndex(-1);
    setFormData({
      quantity: 1,
      dosage: "1 tablet",
      frequency: "twice daily",
      duration: "7 days",
      route: "oral",
      note: "",
    });
  };

  const handleEditItem = (item: PrescriptionItem, index: number) => {
    setEditingItem(item);
    setEditingIndex(index);
    setFormData({
      quantity: item.quantity,
      dosage: item.dosage,
      frequency: item.frequency,
      duration: item.duration,
      route: item.route,
      note: item.note || "",
    });
  };

  const handleSaveItem = () => {
    if (!editingItem) return;

    const updatedItem: PrescriptionItem = {
      ...editingItem,
      ...formData,
    };

    let newItems = [...prescriptionItems];
    if (editingIndex >= 0) {
      // Update existing item
      newItems[editingIndex] = updatedItem;
    } else {
      // Add new item
      newItems.push(updatedItem);
    }

    onItemsChange(newItems);
    setEditingItem(null);
    setEditingIndex(-1);
    setFormData({
      quantity: 1,
      dosage: "",
      frequency: "",
      duration: "",
      route: "oral",
      note: "",
    });
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    setEditingIndex(-1);
    setFormData({
      quantity: 1,
      dosage: "",
      frequency: "",
      duration: "",
      route: "oral",
      note: "",
    });
  };

  const handleRemoveItem = (index: number) => {
    const newItems = prescriptionItems.filter((_, i) => i !== index);
    onItemsChange(newItems);
  };

  const isFormValid = () => {
    return (
      formData.quantity > 0 &&
      formData.dosage.trim() &&
      formData.frequency.trim() &&
      formData.duration.trim() &&
      formData.route.trim()
    );
  };

  return (
    <div className="space-y-6">
      {/* Add Medicine Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Prescription Medicines</h3>
        <MedicineSearch
          onMedicineSelected={handleMedicineSelected}
          disabled={disabled}
        />
      </div>

      {/* Current Prescription Items */}
      {prescriptionItems.length > 0 && (
        <div className="space-y-3">
          {prescriptionItems.map((item, index) => (
            <Card key={index} className="border-l-4 border-l-blue-500">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
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
                        {item.route}
                      </Badge>
                      {item.note && (
                        <span className="text-xs text-gray-500">
                          Note: {item.note}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditItem(item, index)}
                      disabled={disabled}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveItem(index)}
                      disabled={disabled}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit/Add Item Form */}
      {editingItem && (
        <Card className="border-2 border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Pill className="h-5 w-5" />
              {editingIndex >= 0 ? "Edit Medicine" : "Add Medicine"}
            </CardTitle>
            <CardDescription>
              Configure dosage and administration details for {editingItem.medication_name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="quantity">Quantity *</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({ ...formData, quantity: parseInt(e.target.value) || 1 })
                  }
                  disabled={disabled}
                />
              </div>
              <div>
                <Label htmlFor="dosage">Dosage *</Label>
                <Input
                  id="dosage"
                  placeholder="e.g., 1 tablet, 5ml"
                  value={formData.dosage}
                  onChange={(e) =>
                    setFormData({ ...formData, dosage: e.target.value })
                  }
                  disabled={disabled}
                />
              </div>
              <div>
                <Label htmlFor="frequency">Frequency *</Label>
                <Select
                  value={formData.frequency}
                  onValueChange={(value) =>
                    setFormData({ ...formData, frequency: value })
                  }
                  disabled={disabled}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="once daily">Once daily</SelectItem>
                    <SelectItem value="twice daily">Twice daily</SelectItem>
                    <SelectItem value="three times daily">Three times daily</SelectItem>
                    <SelectItem value="four times daily">Four times daily</SelectItem>
                    <SelectItem value="every 4 hours">Every 4 hours</SelectItem>
                    <SelectItem value="every 6 hours">Every 6 hours</SelectItem>
                    <SelectItem value="every 8 hours">Every 8 hours</SelectItem>
                    <SelectItem value="every 12 hours">Every 12 hours</SelectItem>
                    <SelectItem value="as needed">As needed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="duration">Duration *</Label>
                <Select
                  value={formData.duration}
                  onValueChange={(value) =>
                    setFormData({ ...formData, duration: value })
                  }
                  disabled={disabled}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select duration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="3 days">3 days</SelectItem>
                    <SelectItem value="5 days">5 days</SelectItem>
                    <SelectItem value="7 days">7 days</SelectItem>
                    <SelectItem value="10 days">10 days</SelectItem>
                    <SelectItem value="14 days">14 days</SelectItem>
                    <SelectItem value="21 days">21 days</SelectItem>
                    <SelectItem value="30 days">30 days</SelectItem>
                    <SelectItem value="until finished">Until finished</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="route">Route *</Label>
                <Select
                  value={formData.route}
                  onValueChange={(value) =>
                    setFormData({ ...formData, route: value })
                  }
                  disabled={disabled}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select route" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="oral">Oral</SelectItem>
                    <SelectItem value="topical">Topical</SelectItem>
                    <SelectItem value="injection">Injection</SelectItem>
                    <SelectItem value="inhalation">Inhalation</SelectItem>
                    <SelectItem value="eye drops">Eye drops</SelectItem>
                    <SelectItem value="ear drops">Ear drops</SelectItem>
                    <SelectItem value="nasal">Nasal</SelectItem>
                    <SelectItem value="rectal">Rectal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="note">Additional Notes</Label>
              <Textarea
                id="note"
                placeholder="Any special instructions or notes..."
                value={formData.note}
                onChange={(e) =>
                  setFormData({ ...formData, note: e.target.value })
                }
                disabled={disabled}
                rows={2}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={handleCancelEdit}
                disabled={disabled}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveItem}
                disabled={disabled || !isFormValid()}
              >
                {editingIndex >= 0 ? "Update Medicine" : "Add Medicine"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {prescriptionItems.length === 0 && !editingItem && (
        <Card className="border-dashed border-2 border-gray-300">
          <CardContent className="p-8 text-center">
            <Pill className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">
              No medicines added to prescription yet
            </p>
            <MedicineSearch
              onMedicineSelected={handleMedicineSelected}
              disabled={disabled}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
};
