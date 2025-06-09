# User Service API Documentation

## Overview

The User Service is a centralized service that manages general user information for all users in the healthcare system. It serves as a base service for patient and doctor services, providing a unified user management system.

## Base URL

```
http://localhost:8010/api
```

## Authentication

Currently configured with `AllowAny` permissions for development. In production, this should be restricted based on your authentication requirements.

## User Model Schema

### User Fields

- `id` (UUID): Unique identifier for the user
- `auth_user_id` (Integer): Reference to auth_service user ID
- `user_type` (String): Type of user (patient, doctor, admin, staff)
- `first_name` (String): User's first name
- `last_name` (String): User's last name
- `full_name` (String): Auto-generated full name
- `date_of_birth` (Date): User's date of birth
- `gender` (String): User's gender (M, F, O)
- `email` (Email): User's email address (unique)
- `phone` (String): User's phone number
- `address_line_1` (String): Primary address line
- `address_line_2` (String): Secondary address line
- `city` (String): City
- `state` (String): State/Province
- `postal_code` (String): Postal/ZIP code
- `country` (String): Country (default: Vietnam)
- `is_active` (Boolean): Whether user is active
- `is_verified` (Boolean): Whether user is verified
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `last_login` (DateTime): Last login timestamp
- `profile_picture` (URL): Profile picture URL
- `bio` (Text): User biography

## API Endpoints

### 1. List/Create Users

```http
GET /users/
POST /users/
```

**Query Parameters (GET):**

- `user_type`: Filter by user type (patient, doctor, admin, staff)
- `is_active`: Filter by active status (true/false)

**Response (GET):**

```json
[
  {
    "id": "uuid",
    "auth_user_id": 123,
    "user_type": "patient",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "age": 30
  }
]
```

### 2. User Detail

```http
GET /users/{id}/
PUT /users/{id}/
PATCH /users/{id}/
DELETE /users/{id}/
```

### 3. Get User by Auth ID

```http
GET /users/auth/{auth_user_id}/
```

### 4. Get User by Email

```http
GET /users/email/{email}/
```

### 5. Create Doctor User

```http
POST /users/doctors/create/
```

**Request Body:**

```json
{
  "auth_user_id": 123,
  "first_name": "Dr. Jane",
  "last_name": "Smith",
  "email": "jane.smith@hospital.com",
  "phone": "+1234567890",
  "date_of_birth": "1980-01-01",
  "gender": "F",
  "address_line_1": "123 Medical Center Dr",
  "city": "Healthcare City",
  "state": "HC",
  "postal_code": "12345",
  "country": "Vietnam"
}
```

### 6. Create Patient User

```http
POST /users/patients/create/
```

**Request Body:**

```json
{
  "auth_user_id": 456,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "M",
  "address_line_1": "456 Patient St",
  "city": "Patient City",
  "state": "PC",
  "postal_code": "67890",
  "country": "Vietnam"
}
```

### 7. Get All Doctors

```http
GET /users/doctors/
```

### 8. Get All Patients

```http
GET /users/patients/
```

### 9. Update Last Login

```http
POST /users/{user_id}/login/
```

### 10. Verify User

```http
POST /users/{user_id}/verify/
```

### 11. Activate/Deactivate User

```http
POST /users/{user_id}/activate/
POST /users/{user_id}/deactivate/
```

### 12. Log User Activity

```http
POST /activities/
```

**Request Body:**

```json
{
  "user": "user_uuid",
  "activity_type": "login",
  "description": "User logged in",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

### 13. Get User Activities

```http
GET /users/{user_id}/activities/
```

### 14. Health Check

```http
GET /health/
```

## Activity Types

- `login`: User login
- `logout`: User logout
- `profile_update`: Profile information update
- `password_change`: Password change
- `email_change`: Email address change
- `account_verification`: Account verification
- `data_access`: Data access event
- `data_modification`: Data modification event

## Integration with Other Services

### Doctor Service Integration

The doctor service should:

1. Create users via `POST /users/doctors/create/`
2. Fetch user info via `GET /users/{user_id}/`
3. Update user info via `PATCH /users/{user_id}/`

### Patient Service Integration

The patient service should:

1. Create users via `POST /users/patients/create/`
2. Fetch user info via `GET /users/{user_id}/`
3. Update user info via `PATCH /users/{user_id}/`

### Client Configuration

```python
# In doctor_service/info/services.py
class UserServiceClient:
    def __init__(self, base_url: str = "http://localhost:8010/api"):
        self.base_url = base_url.rstrip('/')
```

## Database Configuration

The user service uses PostgreSQL. Update the database configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'user_service_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Docker Setup

The service runs on port 8010 in the Docker environment and connects to the PostgreSQL database.

## Migration and Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 0.0.0.0:8001
```
