#!/bin/bash
# Script to test all API endpoints in the laboratory service

# Set the base URL for the laboratory service
BASE_URL="http://localhost:8006/api"
HEALTH_URL="http://localhost:8006/health"

# Generate JWT tokens for different roles
# You can use the generate_token.py script to create these tokens
# python generate_token.py --role DOCTOR --user_id 1 --username doctor_user
# python generate_token.py --role PATIENT --user_id 2 --username patient_user
# python generate_token.py --role LAB_TECHNICIAN --user_id 3 --username lab_tech_user
# python generate_token.py --role ADMIN --user_id 4 --username admin_user

# For testing purposes, we'll use hardcoded tokens
# In a real scenario, you would generate these tokens using the generate_token.py script
DOCTOR_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzA0NjAwLCJpYXQiOjE3MTYzMDEwMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImRvY3Rvcl91c2VyIiwicm9sZXMiOlsiRE9DVE9SIl19.YOUR_SECRET_KEY_SIGNATURE"
PATIENT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzA0NjAwLCJpYXQiOjE3MTYzMDEwMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InBhdGllbnRfdXNlciIsInJvbGVzIjpbIlBBVElFTlQiXX0.YOUR_SECRET_KEY_SIGNATURE"
LAB_TECH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzA0NjAwLCJpYXQiOjE3MTYzMDEwMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6ImxhYl90ZWNoX3VzZXIiLCJyb2xlcyI6WyJMQUJfVEVDSE5JQ0lBTiJdfQ.YOUR_SECRET_KEY_SIGNATURE"
ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzA0NjAwLCJpYXQiOjE3MTYzMDEwMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6ImFkbWluX3VzZXIiLCJyb2xlcyI6WyJBRE1JTiJdfQ.YOUR_SECRET_KEY_SIGNATURE"

# Function to print section headers
print_header() {
    echo ""
    echo "====================================="
    echo "$1"
    echo "====================================="
    echo ""
}

# Function to run curl command and format the output
run_curl() {
    echo "$ $1"
    eval $1
    echo ""
}

# 1. Health Check Endpoints
print_header "HEALTH CHECK ENDPOINTS"

# Root health check
run_curl "curl -X GET $HEALTH_URL"

# API health check
run_curl "curl -X GET $BASE_URL/health/"

# 2. Test Type Endpoints
print_header "TEST TYPE ENDPOINTS"

# List all test types
run_curl "curl -X GET $BASE_URL/testtypes/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Create a new test type (LAB_TECHNICIAN role)
run_curl "curl -X POST $BASE_URL/testtypes/ \\
  -H \"Authorization: Bearer $LAB_TECH_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"Vitamin E\", \"description\": \"Measures vitamin E levels in the blood\", \"cost\": 55.00, \"unit\": \"mg/L\", \"normal_range\": \"5.5-17.0\"}'"

# Create a new test type (ADMIN role)
run_curl "curl -X POST $BASE_URL/testtypes/ \\
  -H \"Authorization: Bearer $ADMIN_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"Zinc\", \"description\": \"Measures zinc levels in the blood\", \"cost\": 45.00, \"unit\": \"μg/dL\", \"normal_range\": \"70-120\"}'"

# Get a specific test type (assuming ID 1 exists)
run_curl "curl -X GET $BASE_URL/testtypes/1/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Update a test type (LAB_TECHNICIAN role)
run_curl "curl -X PUT $BASE_URL/testtypes/1/ \\
  -H \"Authorization: Bearer $LAB_TECH_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"Complete Blood Count (CBC)\", \"description\": \"Measures different components of blood including red cells, white cells, and platelets\", \"cost\": 30.00, \"unit\": \"various\", \"normal_range\": \"varies by component\"}'"

# Delete a test type (ADMIN role)
run_curl "curl -X DELETE $BASE_URL/testtypes/2/ -H \"Authorization: Bearer $ADMIN_TOKEN\""

# 3. Lab Test Order Endpoints
print_header "LAB TEST ORDER ENDPOINTS"

# List all lab test orders (DOCTOR role)
run_curl "curl -X GET $BASE_URL/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# List all lab test orders (LAB_TECHNICIAN role)
run_curl "curl -X GET $BASE_URL/ -H \"Authorization: Bearer $LAB_TECH_TOKEN\""

# Create a new lab test order (DOCTOR role)
run_curl "curl -X POST $BASE_URL/ \\
  -H \"Authorization: Bearer $DOCTOR_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"patient_id\": 2, \"clinical_notes\": \"Patient complains of fatigue\", \"urgency\": \"routine\", \"items\": [{\"test_type\": 1}]}'"

# Get a specific lab test order (assuming ID 1 exists)
run_curl "curl -X GET $BASE_URL/1/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Update a lab test order (DOCTOR role)
run_curl "curl -X PUT $BASE_URL/1/ \\
  -H \"Authorization: Bearer $DOCTOR_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"patient_id\": 2, \"doctor_id\": 1, \"clinical_notes\": \"Patient complains of fatigue and dizziness\", \"urgency\": \"urgent\", \"items\": [{\"test_type\": 1}, {\"test_type\": 3}]}'"

# Delete/Cancel a lab test order (DOCTOR role)
run_curl "curl -X DELETE $BASE_URL/2/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Get all lab test orders for a patient (DOCTOR role)
run_curl "curl -X GET $BASE_URL/patient/2/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Get all lab test orders for a patient (PATIENT role)
run_curl "curl -X GET $BASE_URL/patient/2/ -H \"Authorization: Bearer $PATIENT_TOKEN\""

# Get all lab test orders by a doctor (DOCTOR role)
run_curl "curl -X GET $BASE_URL/doctor/1/ -H \"Authorization: Bearer $DOCTOR_TOKEN\""

# Update lab test order status (LAB_TECHNICIAN role)
run_curl "curl -X PUT $BASE_URL/1/status/ \\
  -H \"Authorization: Bearer $LAB_TECH_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"status\": \"SAMPLE_COLLECTED\"}'"

# 4. Test Result Endpoints
print_header "TEST RESULT ENDPOINTS"

# Upload a test result for a specific test (LAB_TECHNICIAN role)
run_curl "curl -X POST $BASE_URL/results/upload/1/ \\
  -H \"Authorization: Bearer $LAB_TECH_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"result_value\": \"95\", \"normal_range\": \"70-100\", \"unit\": \"mg/dL\", \"technician_notes\": \"Normal result\"}'"

# Update an existing test result (LAB_TECHNICIAN role)
run_curl "curl -X PUT $BASE_URL/results/1/ \\
  -H \"Authorization: Bearer $LAB_TECH_TOKEN\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"result_value\": \"97\", \"normal_range\": \"70-100\", \"unit\": \"mg/dL\", \"technician_notes\": \"Normal result, updated\"}'"

echo ""
echo "All API endpoints tested!"
