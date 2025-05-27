export enum PrescriptionStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  CANCELLED = "CANCELLED",
  PENDING_DISPENSING = "PENDING_DISPENSING",
  DISPENSED = "DISPENSED",
  EXPIRED = "EXPIRED",
}

export interface Medicine {
  id: number;
  name: string;
  description?: string;
  manufacturer?: string;
  dosage_form?: string;
  strength?: string;
  price: number;
  quantity: number;
  expiry_date?: string;
  batch_number?: string;
  created_at: string;
  updated_at: string;
}

export interface PrescriptionItem {
  id?: number;
  medication_id: number;
  medication_name: string;
  quantity: number;
  dosage: string; // e.g., "1 tablet"
  frequency: string; // e.g., "twice daily"
  duration: string; // e.g., "7 days"
  route: string; // e.g., "oral", "topical"
  note?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Prescription {
  id: number;
  patient_id: number;
  doctor_id: number;
  date: string;
  diagnose: string;
  status: PrescriptionStatus;
  items: PrescriptionItem[];
  created_at: string;
  updated_at: string;
}

export interface CreatePrescriptionRequest {
  patient_id: number;
  diagnose: string;
  status?: PrescriptionStatus;
  items: Omit<PrescriptionItem, 'id' | 'created_at' | 'updated_at'>[];
}

export interface CreatePrescriptionResponse extends Prescription {}

export interface SearchMedicationsRequest {
  query?: string;
}

export interface MedicineSearchResult extends Medicine {}
