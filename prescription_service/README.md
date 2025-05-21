# Prescription Service

This microservice is part of the healthcare management system and handles the creation, management, and dissemination of digital prescriptions.

## Features

- Create and manage prescriptions
- Track prescription status (draft, active, cancelled, dispensed, etc.)
- Verify prescription validity
- Role-based access control (doctors, patients, pharmacists)
- Integration with pharmacy service for medication data
- Draft prescription workflow for doctors

## API Endpoints

### Health Check
- `GET /health/` - Health check endpoint
- `GET /api/health/` - Health check endpoint (API namespace)

### Prescription Management
- `GET /api/` - List all prescriptions (filtered by user role)
- `POST /api/` - Create a new prescription (doctors only)
- `GET /api/<id>/` - Get a specific prescription
- `PUT /api/<id>/` - Update a prescription (prescribing doctor only)
- `DELETE /api/<id>/` - Cancel a prescription (prescribing doctor only)
- `GET /api/patient/<id>/` - Get all prescriptions for a patient
- `GET /api/doctor/<id>/` - Get all prescriptions by a doctor
- `POST /api/<id>/verify/` - Verify if a prescription is valid for dispensing
- `PUT /api/<id>/status/` - Update prescription status

### Draft Prescription Workflow
- `GET /api/medications/search/` - Search for medications from pharmacy service
- `POST /api/draft/` - Create a new draft prescription
- `POST /api/<id>/medications/` - Add a medication to a draft prescription
- `DELETE /api/<id>/medications/<item_id>/` - Remove a medication from a draft prescription
- `PUT /api/<id>/publish/` - Publish a draft prescription (change status from DRAFT to ACTIVE)

## Setup and Installation

### Prerequisites

- Python 3.9+
- MySQL

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the database in `prescription_service/settings.py`
4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Start the server:
   ```
   python manage.py runserver 0.0.0.0:8000
   ```

### Using Docker

1. Build and run using Docker Compose:
   ```
   docker-compose up -d
   ```

## Authentication

This service uses JWT tokens for authentication. The token should be included in the request headers:

```
Authorization: Bearer <token>
```

The JWT token should contain the following claims:
- `user_id`: The ID of the authenticated user
- `roles`: Array of user roles (e.g., ["DOCTOR", "ADMIN"])
- `username`: The username of the authenticated user

### Generating Test Tokens

For testing purposes, you can generate a JWT token using the provided script:

```
python generate_token.py --user_id 1 --username test_doctor --role DOCTOR
```

Available roles: DOCTOR, PATIENT, ADMIN, PHARMACIST

### Legacy Authentication (Deprecated)

For backward compatibility, the service also supports user information in the following headers:
- `X-User-Id`: The ID of the authenticated user
- `X-User-Roles`: JSON array of user roles

This method is deprecated and will be removed in future versions.
