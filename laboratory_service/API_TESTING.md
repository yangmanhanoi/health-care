# Laboratory Service API Testing Guide

This document provides instructions on how to test the Laboratory Service API endpoints using curl commands.

## Prerequisites

- The Laboratory Service should be running (either locally or in Docker)
- curl should be installed on your system
- Basic understanding of REST APIs and HTTP methods

## Testing with the Script

We've provided a shell script `test_api_endpoints.sh` that contains curl commands for testing all the API endpoints in the Laboratory Service.

### Running the Script

1. Make the script executable:
   ```bash
   chmod +x test_api_endpoints.sh
   ```

2. Run the script:
   ```bash
   ./test_api_endpoints.sh
   ```

### Customizing the Script

Before running the script, you may want to customize the following:

1. **Base URL**: Update the `BASE_URL` variable if your service is running on a different host or port.

2. **JWT Tokens**: The script includes hardcoded JWT tokens for testing. For real testing, you should generate valid tokens using the `generate_token.py` script:
   ```bash
   python generate_token.py --role DOCTOR --user_id 1 --username doctor_user
   python generate_token.py --role PATIENT --user_id 2 --username patient_user
   python generate_token.py --role LAB_TECHNICIAN --user_id 3 --username lab_tech_user
   python generate_token.py --role ADMIN --user_id 4 --username admin_user
   ```

3. **IDs**: The script assumes certain IDs exist in your database (e.g., test type ID 1, lab test order ID 1). Update these IDs based on your actual database state.

## Manual Testing with curl

If you prefer to test endpoints individually, here are the curl commands for each endpoint:

### Health Check Endpoints

```bash
# Root health check
curl -X GET http://localhost:8006/health

# API health check
curl -X GET http://localhost:8006/api/health/
```

### Test Type Endpoints

```bash
# List all test types
curl -X GET http://localhost:8006/api/testtypes/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create a new test type
curl -X POST http://localhost:8006/api/testtypes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Vitamin E", "description": "Measures vitamin E levels in the blood", "cost": 55.00, "unit": "mg/L", "normal_range": "5.5-17.0"}'

# Get a specific test type
curl -X GET http://localhost:8006/api/testtypes/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update a test type
curl -X PUT http://localhost:8006/api/testtypes/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Complete Blood Count (CBC)", "description": "Updated description", "cost": 30.00, "unit": "various", "normal_range": "varies by component"}'

# Delete a test type
curl -X DELETE http://localhost:8006/api/testtypes/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Lab Test Order Endpoints

```bash
# List all lab test orders
curl -X GET http://localhost:8006/api/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create a new lab test order
curl -X POST http://localhost:8006/api/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 2, "clinical_notes": "Patient complains of fatigue", "urgency": "routine", "items": [{"test_type": 1}]}'

# Get a specific lab test order
curl -X GET http://localhost:8006/api/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update a lab test order
curl -X PUT http://localhost:8006/api/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 2, "doctor_id": 1, "clinical_notes": "Updated notes", "urgency": "urgent", "items": [{"test_type": 1}, {"test_type": 3}]}'

# Delete/Cancel a lab test order
curl -X DELETE http://localhost:8006/api/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all lab test orders for a patient
curl -X GET http://localhost:8006/api/patient/2/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all lab test orders by a doctor
curl -X GET http://localhost:8006/api/doctor/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update lab test order status
curl -X PUT http://localhost:8006/api/1/status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "SAMPLE_COLLECTED"}'
```

### Test Result Endpoints

```bash
# Upload a test result
curl -X POST http://localhost:8006/api/results/upload/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"result_value": "95", "normal_range": "70-100", "unit": "mg/dL", "technician_notes": "Normal result"}'

# Update an existing test result
curl -X PUT http://localhost:8006/api/results/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"result_value": "97", "normal_range": "70-100", "unit": "mg/dL", "technician_notes": "Updated notes"}'
```

## Authentication

All endpoints (except health checks) require authentication using JWT tokens. The token should be included in the request headers:

```
Authorization: Bearer YOUR_TOKEN
```

The JWT token should contain the following claims:
- `user_id`: The ID of the authenticated user
- `roles`: Array of user roles (e.g., ["DOCTOR", "ADMIN"])
- `username`: The username of the authenticated user

Available roles: DOCTOR, PATIENT, ADMIN, LAB_TECHNICIAN

## Role-Based Access Control

Different endpoints have different role requirements:

- **DOCTOR**: Can create lab test orders, view their own orders, and view patient orders
- **PATIENT/CUSTOMER**: Can view their own lab test orders
- **LAB_TECHNICIAN**: Can update test types, update order status, and upload test results
- **ADMIN**: Has full access to all endpoints

Make sure to use the appropriate token with the correct role when testing each endpoint.
