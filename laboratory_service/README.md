# Laboratory Service

This microservice is part of the healthcare management system and handles the management of laboratory tests, from ordering to result reporting.

## Features

- Create and manage lab test orders
- Track lab test order status (ordered, sample collected, in progress, completed, cancelled)
- Upload and view test results
- Role-based access control (doctors, patients, lab technicians)
- Manage test types and their reference ranges

## API Endpoints

### Health Check
- `GET /health/` - Health check endpoint
- `GET /api/health/` - Health check endpoint (API namespace)

### Test Type Management
- `GET /api/testtypes/` - List all test types
- `POST /api/testtypes/` - Create a new test type (lab technicians and admins only)
- `GET /api/testtypes/<id>/` - Get a specific test type
- `PUT /api/testtypes/<id>/` - Update a test type (lab technicians and admins only)
- `DELETE /api/testtypes/<id>/` - Delete a test type (admins only)

### Lab Test Order Management
- `GET /api/` - List all lab test orders (filtered by user role)
- `POST /api/` - Create a new lab test order (doctors only)
- `GET /api/<id>/` - Get a specific lab test order
- `PUT /api/<id>/` - Update a lab test order (ordering doctor only)
- `DELETE /api/<id>/` - Cancel a lab test order (ordering doctor only)
- `GET /api/patient/<id>/` - Get all lab test orders for a patient
- `GET /api/doctor/<id>/` - Get all lab test orders by a doctor
- `PUT /api/<id>/status/` - Update lab test order status

### Appointment Integration
- `GET /api/appointment/<appointment_id>/test-items/` - Get all test items for a specific appointment with pricing information

### Test Result Management
- `POST /api/results/upload/<order_item_id>/` - Upload a test result for a specific test (lab technicians only)
- `PUT /api/results/<id>/` - Update an existing test result (lab technicians only)

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the database in `laboratory_service/settings.py`
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

2. If you encounter database connection issues, try the following:

   a. Check the logs to see what's happening:
   ```
   docker-compose logs
   ```

   b. Test the database connection directly:
   ```
   python test_db_connection.py
   ```

   c. If needed, you can manually create the database and grant permissions:
   ```
   docker-compose exec db mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS laboratory_db; GRANT ALL PRIVILEGES ON laboratory_db.* TO 'namdt25'@'%'; FLUSH PRIVILEGES;"
   ```

   d. Restart the services:
   ```
   docker-compose down
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

Available roles: DOCTOR, PATIENT, ADMIN, LAB_TECHNICIAN
