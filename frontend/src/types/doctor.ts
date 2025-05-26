export interface Doctor {
  id: number;
  user_id: number;
  full_name: string;
  specialty: string;
  license_number: string;
  contact?: string;
  created_at: string;
}

export interface Availability {
  id: number;
  doctor: number;
  date: string;
  start_time: string;
  end_time: string;
}

export interface DoctorWithAvailability extends Doctor {
  availabilities?: Availability[];
}

export interface SearchDoctorsRequest {
  specialty?: string;
  search?: string;
}

export interface GetAvailabilityRequest {
  doctor_id: number;
  date?: string;
  start_time?: string;
  end_time?: string;
}

export interface CreateAvailabilityRequest {
  doctor: number;
  date: string;
  start_time: string;
  end_time: string;
}

export interface CreateAvailabilityResponse {
  id: number;
  doctor: number;
  date: string;
  start_time: string;
  end_time: string;
}
