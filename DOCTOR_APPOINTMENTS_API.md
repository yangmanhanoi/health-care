# Doctor Appointments API Documentation

## Overview
This document describes the new API endpoints for doctors to view and manage their patient appointments.

## Base URL
All endpoints are accessed through the API Gateway at `http://localhost:8080/svc-appointment/api/appointments/`

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get Doctor's Appointments List

**Endpoint:** `GET /doctor`

**Description:** Retrieves all appointments for the authenticated doctor with patient information included.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
[
  {
    "id": 1,
    "doctor_id": "123",
    "patient_id": "456",
    "date": "2024-01-15",
    "time": "10:30",
    "status": "SCHEDULED",
    "price": 100000.00,
    "diagnose": null,
    "conclusion": null,
    "need_lab_test": false,
    "created_at": "2024-01-10T08:00:00Z",
    "updated_at": "2024-01-10T08:00:00Z",
    "patient_info": {
      "id": 456,
      "fullName": "John Doe",
      "dob": "1990-05-15",
      "gender": "M",
      "phone": "+1234567890",
      "address": "123 Main St, City, State",
      "email": "john.doe@email.com",
      "user_id": 789
    }
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - User is not a doctor

### 2. Get Detailed Appointment Information

**Endpoint:** `GET /doctor/{appointment_id}`

**Description:** Retrieves detailed information about a specific appointment including patient details and lab test results.

**Parameters:**
- `appointment_id` (path parameter) - The ID of the appointment

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "id": 1,
  "doctor_id": "123",
  "patient_id": "456",
  "date": "2024-01-15",
  "time": "10:30",
  "status": "FINISHED",
  "price": 100000.00,
  "diagnose": "Common cold symptoms",
  "conclusion": "Patient advised rest and medication",
  "need_lab_test": true,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "total_price": 150000.00,
  "patient_info": {
    "id": 456,
    "fullName": "John Doe",
    "dob": "1990-05-15",
    "gender": "M",
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "email": "john.doe@email.com",
    "user_id": 789
  },
  "test_results": [
    {
      "id": 1,
      "test_type": "Blood Test",
      "result": "Normal",
      "price": 50000.00,
      "status": "COMPLETED"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - User is not a doctor or doesn't own this appointment
- `404 Not Found` - Appointment not found

## Frontend Integration

### New Page: Doctor Appointments
- **Route:** `/doctor/appointments`
- **Component:** `DoctorAppointmentsPage`
- **Features:**
  - View all patient appointments
  - Filter by appointment status
  - Sort by date, status, or patient name
  - View detailed appointment information in modal
  - Display patient names instead of IDs
  - Show lab test results when available

### Dashboard Integration
- Added "Patient Appointments" button for doctors
- Updated navigation to route doctors to their appointment view
- Enhanced "Next Steps" section for doctors

## Key Features

1. **Patient Information Display:**
   - Shows patient full names instead of patient IDs
   - Includes patient contact information in detailed view
   - Fallback to patient ID if patient info unavailable

2. **Comprehensive Appointment Details:**
   - Basic appointment information (date, time, status)
   - Medical information (diagnosis, conclusion)
   - Lab test results and pricing
   - Total cost calculation including lab tests

3. **Enhanced Filtering and Sorting:**
   - Filter by appointment status
   - Sort by date/time, status, or patient name
   - Real-time filtering and sorting

4. **Responsive Design:**
   - Mobile-friendly interface
   - Modern UI with gradient backgrounds
   - Consistent styling with existing pages

## Error Handling

The system gracefully handles various error scenarios:
- Patient service unavailable: Shows patient ID as fallback
- Laboratory service unavailable: Shows base appointment price
- Network timeouts: Logs errors and continues with available data
- Authentication failures: Proper error messages and redirects

## Security

- All endpoints require doctor role authentication
- Doctors can only view their own patient appointments
- Patient information is only accessible to authorized doctors
- Proper permission checks at both API and UI levels
