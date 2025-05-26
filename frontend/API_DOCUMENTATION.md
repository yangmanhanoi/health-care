# Patient Authentication API Documentation

This document provides comprehensive API documentation for the patient authentication system, accessed through the API Gateway at `http://localhost:8080/`.

## Base URL
```
http://localhost:8080/
```

## Authentication Endpoints

### 1. Patient Login

**Endpoint:** `POST /svc-auth/api/login`

**Description:** Authenticate a patient and receive JWT tokens for accessing protected resources.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "patient_user",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response (400 Bad Request):**
```json
{
  "non_field_errors": ["Invalid credentials"]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8080/svc-auth/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "patient_user",
    "password": "securepassword123"
  }'
```

---

### 2. Patient Registration

**Endpoint:** `POST /svc-auth/api/register/patient`

**Description:** Register a new patient account. This endpoint creates both an authentication user and a patient profile.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "new_patient",
  "password": "securepassword123",
  "confirm_password": "securepassword123",
  "email": "patient@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "dob": "1990-01-15",
  "gender": "M",
  "address": "123 Main St, City, State 12345"
}
```

**Required Fields:**
- `username` (string, min 3 characters)
- `password` (string, min 6 characters)
- `confirm_password` (string, must match password)

**Optional Fields:**
- `email` (string, valid email format)
- `full_name` (string)
- `phone` (string)
- `dob` (string, YYYY-MM-DD format)
- `gender` (string, "M", "F", or "O")
- `address` (string)

**Success Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "username": "new_patient",
    "roles": ["PATIENT"]
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "username": ["This field is required."],
  "password": ["This field is required."],
  "confirm_password": ["Passwords don't match."]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8080/svc-auth/api/register/patient \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_patient",
    "password": "securepassword123",
    "confirm_password": "securepassword123",
    "email": "patient@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "dob": "1990-01-15",
    "gender": "M",
    "address": "123 Main St, City, State 12345"
  }'
```

---

## JWT Token Usage

After successful login, use the `access` token in the Authorization header for protected endpoints:

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Token Payload Example:**
```json
{
  "token_type": "access",
  "exp": 1716304600,
  "iat": 1716301000,
  "jti": "1234567890",
  "user_id": 1,
  "username": "patient_user",
  "roles": ["PATIENT"]
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Endpoint not found |
| 500 | Internal Server Error |

---

## Frontend Integration

The frontend application is built with React and integrates with these APIs through:

1. **Login Form** (`/login`) - Calls the login endpoint
2. **Registration Form** (`/register`) - Calls the patient registration endpoint
3. **Authentication Context** - Manages JWT tokens and user state
4. **Protected Routes** - Automatically redirects unauthenticated users

**Frontend URLs:**
- Login: `http://localhost:5173/login`
- Register: `http://localhost:5173/register`
- Dashboard: `http://localhost:5173/dashboard` (protected)

---

## Notes

1. **Password Requirements:** Minimum 6 characters
2. **Username Requirements:** Minimum 3 characters, must be unique
3. **Token Expiry:** Access tokens expire after 1 hour
4. **Refresh Tokens:** Valid for 1 day
5. **CORS:** Enabled for frontend development
6. **Patient Profile:** Automatically created in patient_service upon registration
7. **Role Assignment:** All registered users automatically get "PATIENT" role
