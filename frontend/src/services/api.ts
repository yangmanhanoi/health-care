import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterDoctorRequest,
  RegisterResponse,
  ApiError,
} from "../types/auth";
import type {
  Doctor,
  Availability,
  SearchDoctorsRequest,
  GetAvailabilityRequest,
  CreateAvailabilityRequest,
  CreateAvailabilityResponse,
} from "../types/doctor";
import type {
  Appointment,
  CreateAppointmentRequest,
  CreateAppointmentResponse,
  DetailedAppointment,
} from "../types/appointment";
import type {
  TestType,
  LabTestOrder,
  TestResult,
  CreateLabTestOrderRequest,
  CreateTestResultRequest,
  UpdateTestResultRequest,
  AppointmentTestItemsResponse,
} from "../types/laboratory";
import type {
  Medicine,
  Prescription,
  CreatePrescriptionRequest,
  CreatePrescriptionResponse,
  SearchMedicationsRequest,
  MedicineSearchResult,
} from "../types/prescription";

const API_BASE_URL = "http://localhost:8080";

class ApiService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultHeaders = {
      "Content-Type": "application/json",
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = "An error occurred";
        let errors: Record<string, string[]> | undefined;

        try {
          const errorData = await response.json();

          // Handle Django REST Framework error formats
          if (
            errorData.non_field_errors &&
            Array.isArray(errorData.non_field_errors)
          ) {
            errorMessage = errorData.non_field_errors[0];
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (typeof errorData === "string") {
            errorMessage = errorData;
          } else {
            // If it's a field-specific error object, extract the first error
            const firstError = Object.values(errorData)[0];
            if (Array.isArray(firstError) && firstError.length > 0) {
              errorMessage = firstError[0];
            }
          }

          errors = errorData.errors || errorData;
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }

        const apiError: ApiError = { message: errorMessage, errors };
        throw apiError;
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          "Network error. Please check your connection and try again."
        );
      }
      throw error;
    }
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return this.makeRequest<LoginResponse>("/svc-auth/api/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return this.makeRequest<RegisterResponse>(
      "/svc-auth/api/register/patient",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  }

  async registerDoctor(data: RegisterDoctorRequest): Promise<RegisterResponse> {
    return this.makeRequest<RegisterResponse>("/svc-auth/api/register/doctor", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Doctor endpoints
  async searchDoctors(params?: SearchDoctorsRequest): Promise<Doctor[]> {
    const searchParams = new URLSearchParams();
    if (params?.specialty) searchParams.append("specialty", params.specialty);
    if (params?.search) searchParams.append("search", params.search);

    const queryString = searchParams.toString();
    const endpoint = `/svc-doctor/api/info/doctors/${
      queryString ? `?${queryString}` : ""
    }`;

    return this.makeRequest<Doctor[]>(endpoint, {
      method: "GET",
    });
  }

  async getDoctorAvailabilities(
    params: GetAvailabilityRequest
  ): Promise<Availability[]> {
    const { doctor_id, date, start_time, end_time } = params;
    let endpoint = `/svc-doctor/api/schedule/availabilities/doctor/${doctor_id}`;

    if (date) {
      endpoint += `/${date}`;
      const searchParams = new URLSearchParams();
      if (start_time) searchParams.append("start_time", start_time);
      if (end_time) searchParams.append("end_time", end_time);
      const queryString = searchParams.toString();
      if (queryString) endpoint += `?${queryString}`;
    }

    return this.makeRequest<Availability[]>(endpoint, {
      method: "GET",
    });
  }

  // Doctor profile endpoints
  async getDoctorProfile(user_id: number): Promise<Doctor> {
    return this.makeRequest<Doctor>(
      `/svc-doctor/api/info/doctors/profile/${user_id}`,
      {
        method: "GET",
      }
    );
  }

  async getDoctorByUserId(user_id: number): Promise<Doctor> {
    return this.makeRequest<Doctor>(`/svc-doctor/api/info/doctors/${user_id}`, {
      method: "GET",
    });
  }

  // Doctor schedule management endpoints
  async getMyAvailabilities(token: string): Promise<Availability[]> {
    return this.makeRequest<Availability[]>(
      "/svc-doctor/api/schedule/availabilities",
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  async createAvailability(
    data: CreateAvailabilityRequest,
    token: string
  ): Promise<CreateAvailabilityResponse> {
    return this.makeRequest<CreateAvailabilityResponse>(
      "/svc-doctor/api/schedule/availabilities",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );
  }

  async deleteAvailability(id: number, token: string): Promise<void> {
    return this.makeRequest<void>(
      `/svc-doctor/api/schedule/availabilities/${id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  // Appointment endpoints
  async createAppointment(
    data: CreateAppointmentRequest,
    token: string
  ): Promise<CreateAppointmentResponse> {
    return this.makeRequest<CreateAppointmentResponse>(
      "/svc-appointment/api/appointments/patient",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );
  }

  async getPatientAppointments(token: string): Promise<Appointment[]> {
    return this.makeRequest<Appointment[]>(
      "/svc-appointment/api/appointments/patient",
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  // Doctor appointment endpoints
  async getDoctorAppointments(token: string): Promise<Appointment[]> {
    return this.makeRequest<Appointment[]>(
      "/svc-appointment/api/appointments/doctor",
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  async getDoctorAppointmentDetail(
    appointmentId: number,
    token: string
  ): Promise<DetailedAppointment> {
    return this.makeRequest<DetailedAppointment>(
      `/svc-appointment/api/appointments/doctor/${appointmentId}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  // Appointment status change endpoints
  async checkInAppointment(
    appointmentId: number,
    token: string
  ): Promise<Appointment> {
    return this.makeRequest<Appointment>(
      `/svc-appointment/api/appointments/${appointmentId}/check-in`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({}),
      }
    );
  }

  async diagnoseAppointment(
    appointmentId: number,
    diagnose: string,
    needLabTest: boolean,
    token: string
  ): Promise<Appointment> {
    return this.makeRequest<Appointment>(
      `/svc-appointment/api/appointments/${appointmentId}/diagnose`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          diagnose,
          need_lab_test: needLabTest,
        }),
      }
    );
  }

  async completeLabTest(
    appointmentId: number,
    token: string
  ): Promise<Appointment> {
    return this.makeRequest<Appointment>(
      `/svc-appointment/api/appointments/${appointmentId}/complete-lab-test`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({}),
      }
    );
  }

  async concludeAppointment(
    appointmentId: number,
    conclusion: string,
    token: string
  ): Promise<Appointment> {
    return this.makeRequest<Appointment>(
      `/svc-appointment/api/appointments/${appointmentId}/conclusion`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          conclusion,
        }),
      }
    );
  }

  async getAppointmentTotalPrice(
    appointmentId: number,
    token: string
  ): Promise<{ total_price: number; test_results: TestResult[] }> {
    return this.makeRequest<{
      total_price: number;
      test_results: TestResult[];
    }>(`/svc-appointment/api/appointments/${appointmentId}/total-price`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  setAuthToken(token: string) {
    // This method can be used to set the auth token for future requests
    // For now, we'll store it in localStorage in the AuthContext
    console.log("Setting auth token:", token);
  }

  removeAuthToken() {
    // Remove auth token
  }

  // Laboratory Service endpoints
  async getTestTypes(token: string): Promise<TestType[]> {
    return this.makeRequest<TestType[]>("/svc-laboratory/api/testtypes/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async createLabTestOrder(
    data: CreateLabTestOrderRequest,
    token: string
  ): Promise<LabTestOrder> {
    return this.makeRequest<LabTestOrder>("/svc-laboratory/api/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  }

  async getAppointmentTestItems(
    appointmentId: number,
    token: string
  ): Promise<AppointmentTestItemsResponse> {
    return this.makeRequest<AppointmentTestItemsResponse>(
      `/svc-laboratory/api/appointment/${appointmentId}/test-items/`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  // Lab Test Result endpoints
  async uploadTestResult(
    orderItemId: number,
    data: CreateTestResultRequest,
    token: string
  ): Promise<TestResult> {
    return this.makeRequest<TestResult>(
      `/svc-laboratory/api/results/upload/${orderItemId}/`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );
  }

  async updateTestResult(
    resultId: number,
    data: UpdateTestResultRequest,
    token: string
  ): Promise<TestResult> {
    return this.makeRequest<TestResult>(
      `/svc-laboratory/api/results/${resultId}/`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );
  }

  async getLabTestOrders(token: string): Promise<LabTestOrder[]> {
    return this.makeRequest<LabTestOrder[]>("/svc-laboratory/api/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getLabTestOrder(orderId: number, token: string): Promise<LabTestOrder> {
    return this.makeRequest<LabTestOrder>(`/svc-laboratory/api/${orderId}/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // Prescription endpoints
  async searchMedications(
    params?: SearchMedicationsRequest,
    token?: string
  ): Promise<MedicineSearchResult[]> {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.append("query", params.query);

    const queryString = searchParams.toString();
    const endpoint = `/svc-prescription/api/medications/search/${
      queryString ? `?${queryString}` : ""
    }`;

    const headers: Record<string, string> = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return this.makeRequest<MedicineSearchResult[]>(endpoint, {
      method: "GET",
      headers,
    });
  }

  async createPrescription(
    data: CreatePrescriptionRequest,
    token: string
  ): Promise<CreatePrescriptionResponse> {
    console.log(`Creating prescription for patient ID: ${data.patient_id}`, data);
    try {
      const result = await this.makeRequest<CreatePrescriptionResponse>("/svc-prescription/api/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      console.log(`Successfully created prescription:`, result);
      return result;
    } catch (error) {
      console.error(`Error creating prescription:`, error);
      throw error;
    }
  }

  async getPatientPrescriptions(
    patientId: number,
    token: string
  ): Promise<Prescription[]> {
    console.log(`Fetching prescriptions for patient ID: ${patientId}`);
    try {
      const result = await this.makeRequest<Prescription[]>(
        `/svc-prescription/api/patient/${patientId}/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log(`Successfully fetched ${result.length} prescriptions for patient ${patientId}`);
      return result;
    } catch (error) {
      console.error(`Error fetching prescriptions for patient ${patientId}:`, error);
      throw error;
    }
  }

  async getDoctorPrescriptions(
    doctorId: number,
    token: string
  ): Promise<Prescription[]> {
    return this.makeRequest<Prescription[]>(
      `/svc-prescription/api/doctor/${doctorId}/`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  async getPrescriptionDetail(
    prescriptionId: number,
    token: string
  ): Promise<Prescription> {
    return this.makeRequest<Prescription>(
      `/svc-prescription/api/${prescriptionId}/`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  async getAllPrescriptions(token: string): Promise<Prescription[]> {
    return this.makeRequest<Prescription[]>("/svc-prescription/api/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }
}

export const apiService = new ApiService();
