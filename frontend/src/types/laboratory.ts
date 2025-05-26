// Laboratory Service Types

export enum LabTestOrderStatus {
  ORDERED = "ORDERED",
  SAMPLE_COLLECTED = "SAMPLE_COLLECTED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
}

export interface TestType {
  id: number;
  name: string;
  description?: string;
  cost: number | string;
  unit?: string;
  normal_range?: string;
  created_at: string;
  updated_at: string;
}

export interface TestResult {
  id: number;
  order_item: number;
  result_value: string;
  normal_range?: string;
  unit?: string;
  technician_notes?: string;
  result_date: string;
  verified_by?: number;
  created_at: string;
  updated_at: string;
}

export interface LabTestOrderItem {
  id: number;
  order: number;
  test_type: number;
  test_type_details: TestType;
  status: LabTestOrderStatus;
  price: number | string;
  result_details?: TestResult;
  created_at: string;
  updated_at: string;
}

export interface LabTestOrder {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_id?: number;
  request_date: string;
  status: LabTestOrderStatus;
  clinical_notes?: string;
  urgency?: string;
  collection_date?: string;
  completion_date?: string;
  items: LabTestOrderItem[];
  created_at: string;
  updated_at: string;
}

export interface CreateLabTestOrderRequest {
  patient_id: number;
  appointment_id?: number;
  clinical_notes?: string;
  urgency?: string;
  items: CreateLabTestOrderItemRequest[];
}

export interface CreateLabTestOrderItemRequest {
  test_type: number;
}

export interface CreateTestResultRequest {
  result_value: string;
  normal_range?: string;
  unit?: string;
  technician_notes?: string;
}

export interface UpdateTestResultRequest {
  result_value?: string;
  normal_range?: string;
  unit?: string;
  technician_notes?: string;
}

export interface AppointmentTestItemsResponse {
  appointment_id: number;
  total_test_items: number;
  total_cost: number;
  test_items: LabTestOrderItem[];
}

// UI-specific types
export interface SelectedTestType extends TestType {
  selected: boolean;
}
