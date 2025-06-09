# Appointment Service API Documentation

## Overview

This document describes the API endpoints in the appointment service that communicate with doctor and patient services to retrieve comprehensive information.

## Base URL

All endpoints are accessed through the API Gateway at `http://localhost:8080/svc-appointment/api/appointments/`

## Authentication

All endpoints require authentication via headers:

```
X-User-Id: <user_id>
X-User-Roles: ["ROLE1", "ROLE2"]
```

## New API Endpoints

### 1. Get Doctor Information

**Endpoint:** `GET /doctor-info/{doctor_id}`

**Description:** Retrieves detailed doctor information from the doctor service.

**Parameters:**

- `doctor_id` (path): The user_id of the doctor

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 123,
  "full_name": "Dr. John Smith",
  "specialty": "Cardiology",
  "license_number": "MD12345",
  "contact": "+1234567890",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**

- `404 Not Found`: Doctor not found
- `503 Service Unavailable`: Cannot connect to doctor service

---

### 2. Get Patient Information

**Endpoint:** `GET /patient-info/{patient_id}`

**Description:** Retrieves detailed patient information from the patient service.

**Parameters:**

- `patient_id` (path): The ID of the patient record

**Permissions:**

- Doctors, staff, and admins can access any patient information
- Patients can only access their own information

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 456,
  "fullName": "Jane Doe",
  "dob": "1990-05-15",
  "gender": "F",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "email": "jane.doe@email.com",
  "registerDate": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**

- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Patient not found
- `503 Service Unavailable`: Cannot connect to patient service

---

### 3. Get Appointment Full Details

**Endpoint:** `GET /{appointment_id}/full-details`

**Description:** Retrieves complete appointment information including doctor details, patient details, and lab test results.

**Parameters:**

- `appointment_id` (path): The ID of the appointment

**Permissions:**

- Doctors can access their own appointments
- Patients can access their own appointments
- Admins can access any appointment

**Response (200 OK):**

```json
{
  "id": 1,
  "doctor_id": "123",
  "patient_id": "456",
  "date": "2024-01-15",
  "time": "10:30",
  "status": "FINISHED",
  "price": 100000.0,
  "diagnose": "Common cold symptoms",
  "conclusion": "Patient advised rest and medication",
  "need_lab_test": true,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "total_price": 150000.0,
  "doctor_info": {
    "id": 1,
    "user_id": 123,
    "full_name": "Dr. John Smith",
    "specialty": "Cardiology",
    "license_number": "MD12345",
    "contact": "+1234567890"
  },
  "patient_info": {
    "id": 1,
    "user_id": 456,
    "fullName": "Jane Doe",
    "dob": "1990-05-15",
    "gender": "F",
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "email": "jane.doe@email.com"
  },
  "test_results": [
    {
      "id": 1,
      "test_type": "Blood Test",
      "result": "Normal",
      "price": 50000.0,
      "status": "COMPLETED"
    }
  ]
}
```

---

### 4. Search Doctors

**Endpoint:** `GET /search-doctors`

**Description:** Search for doctors with optional filtering by specialty and name, including their availability information.

**Query Parameters:**

- `specialty` (optional): Filter by doctor specialty
- `search` (optional): Search by doctor name

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 123,
    "full_name": "Dr. John Smith",
    "specialty": "Cardiology",
    "license_number": "MD12345",
    "contact": "+1234567890",
    "availabilities": [
      {
        "id": 1,
        "date": "2024-01-15",
        "start_time": "09:00",
        "end_time": "17:00",
        "is_available": true
      }
    ]
  }
]
```

---

### 5. Get Patient History

**Endpoint:** `GET /patient-history/{patient_id}`

**Description:** Retrieves comprehensive patient medical history including past appointments and medical records.

**Parameters:**

- `patient_id` (path): The ID of the patient record

**Permissions:**

- Doctors, staff, and admins can access any patient history
- Patients can only access their own history

**Response (200 OK):**

```json
{
  "patient_id": 1,
  "history": "Previous medical history from patient service",
  "appointment_history": [
    {
      "id": 1,
      "doctor_id": "123",
      "patient_id": "456",
      "date": "2024-01-10",
      "time": "10:30",
      "status": "FINISHED",
      "diagnose": "Common cold",
      "conclusion": "Rest and medication",
      "doctor_info": {
        "full_name": "Dr. John Smith",
        "specialty": "Cardiology"
      }
    }
  ]
}
```

---

### 6. Get All Appointments Enriched (Admin Only)

**Endpoint:** `GET /all-enriched`

**Description:** Retrieves all appointments with complete doctor and patient information. Admin access only.

**Query Parameters:**

- `status` (optional): Filter by appointment status
- `date_from` (optional): Filter appointments from this date (YYYY-MM-DD)
- `date_to` (optional): Filter appointments to this date (YYYY-MM-DD)
- `doctor_id` (optional): Filter by doctor user_id

**Permissions:**

- Admin only

**Response (200 OK):**

```json
{
  "total_count": 2,
  "appointments": [
    {
      "id": 1,
      "doctor_id": "123",
      "patient_id": "456",
      "date": "2024-01-15",
      "time": "10:30",
      "status": "FINISHED",
      "price": 100000.0,
      "diagnose": "Common cold symptoms",
      "conclusion": "Patient advised rest and medication",
      "need_lab_test": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z",
      "doctor_info": {
        "id": 1,
        "user_id": 123,
        "full_name": "Dr. John Smith",
        "specialty": "Cardiology",
        "license_number": "MD12345",
        "contact": "+1234567890"
      },
      "patient_info": {
        "id": 1,
        "user_id": 456,
        "fullName": "Jane Doe",
        "dob": "1990-05-15",
        "gender": "F",
        "phone": "+1234567890",
        "address": "123 Main St, City, State",
        "email": "jane.doe@email.com"
      }
    }
  ]
}
```

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "message": "Error description"
}
```

Common HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External service unavailable

## Service Dependencies

These APIs depend on the following services:

- **Doctor Service**: `http://service-doctor:8003/api/info/`
- **Patient Service**: `http://service-patient:8004/api/`
- **Laboratory Service**: `http://service-laboratory:8005/api/`

## Usage Examples

### Get doctor information for appointment booking:

```bash
curl -X GET "http://localhost:8080/svc-appointment/api/appointments/doctor-info/123" \
  -H "X-User-Id: 456" \
  -H "X-User-Roles: [\"PATIENT\"]"
```

### Search for cardiologists:

```bash
curl -X GET "http://localhost:8080/svc-appointment/api/appointments/search-doctors?specialty=Cardiology" \
  -H "X-User-Id: 456" \
  -H "X-User-Roles: [\"PATIENT\"]"
```

### Get complete appointment details:

```bash
curl -X GET "http://localhost:8080/svc-appointment/api/appointments/1/full-details" \
  -H "X-User-Id: 123" \
  -H "X-User-Roles: [\"DOCTOR\"]"
```

### Get patient medical history:

```bash
curl -X GET "http://localhost:8080/svc-appointment/api/appointments/patient-history/1" \
  -H "X-User-Id: 123" \
  -H "X-User-Roles: [\"DOCTOR\"]"
```

### Get all appointments with filters (Admin only):

```bash
curl -X GET "http://localhost:8080/svc-appointment/api/appointments/all-enriched?status=FINISHED&date_from=2024-01-01" \
  -H "X-User-Id: 1" \
  -H "X-User-Roles: [\"ADMIN\"]"
```
