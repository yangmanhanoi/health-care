export interface PatientInfo {
  id: number;
  fullName: string;
  dob: string;
  gender: string;
  phone: string;
  address: string;
  email: string;
  user_id: number;
}

export interface Appointment {
  id: number;
  doctor_id: string;
  patient_id: string;
  date: string;
  time: string;
  status: AppointmentStatus;
  price: number;
  diagnose?: string;
  conclusion?: string;
  need_lab_test: boolean;
  created_at: string;
  updated_at: string;
  patient_info?: PatientInfo; // Optional patient information for doctor views
}

export enum AppointmentStatus {
  SCHEDULED = "SCHEDULED",
  FINISHED = "FINISHED",
  CONFIRMED = "CONFIRMED",
  INVOICED = "INVOICED",
  CANCELED = "CANCELED",
  DENIED = "DENIED",
  REJECTION_REQUESTED = "REJECTION_REQUESTED",
  REJECTED = "REJECTED",
  EXCHANGE_REQUESTED = "EXCHANGE_REQUESTED",
  DIAGNOSING = "DIAGNOSING",
  TESTING = "TESTING",
  CONCLUDING = "CONCLUDING",
}

export interface CreateAppointmentRequest {
  doctor_id: string;
  date: string;
  time: string;
}

export interface CreateAppointmentResponse {
  id: number;
  doctor_id: string;
  patient_id: string;
  date: string;
  time: string;
  status: AppointmentStatus;
  price: number;
  created_at: string;
  updated_at: string;
}

export interface TestResult {
  id: number;
  test_type: string;
  result: string;
  price: number;
  status: string;
}

export interface DetailedAppointment extends Appointment {
  patient_info?: PatientInfo;
  test_results: TestResult[];
  total_price: number;
}
