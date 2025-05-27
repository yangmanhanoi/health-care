export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  confirm_password: string;
  email?: string;
  full_name?: string;
  phone?: string;
  dob?: string;
  gender?: "M" | "F" | "O";
  address?: string;
}

export interface RegisterDoctorRequest {
  username: string;
  password: string;
  confirm_password: string;
  full_name: string;
  specialty: string;
  license_number: string;
  contact: string; // email
}

export interface RegisterResponse {
  message: string;
  user: {
    username: string;
    roles: string[];
  };
}

export interface User {
  username: string;
  roles: string[];
  user_id?: number;
  id?: number; // Alias for user_id for consistency
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  registerDoctor: (data: RegisterDoctorRequest) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}
