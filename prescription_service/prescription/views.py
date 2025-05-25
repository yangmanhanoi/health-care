from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .models import Prescription, PrescriptionStatus
from .serializers import PrescriptionSerializer, PrescriptionItemSerializer, PrescriptionStatusUpdateSerializer
from core.utils.request_utils import extract_user_info_from_headers
import requests
from django.db import connection
import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for service URLs
DOCTOR_SERVICE_URL = "http://service-doctor:8002/api/info"
PHARMACY_SERVICE_URL = "http://service-pharmacy:8000/api/pharmacy"  # Using service name from docker-compose

@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def search_medications(request):
    """
    Search for medications from the pharmacy service
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Only doctors can search medications for prescriptions
    if 'DOCTOR' not in roles:
        return Response({"message": "Only doctors can search medications for prescriptions"},
                        status=status.HTTP_403_FORBIDDEN)

    # Get search query from request parameters
    query = request.query_params.get('query', '').strip().lower()

    # Call pharmacy service to get the list of medications
    try:
        # First, fetch all medications from the pharmacy service
        response = requests.get(f"{PHARMACY_SERVICE_URL}/medicines/")

        if response.status_code != 200:
            return Response(
                {"message": f"Error from pharmacy service: {response.text}"},
                status=response.status_code
            )

        # Parse the response to get the list of medications
        all_medications = response.json()

        # If no query is provided, return all medications
        if not query:
            return Response(all_medications)

        # Filter medications based on the search query
        filtered_medications = []
        for medication in all_medications:
            # Search in medication name, description, and other relevant fields
            # Adjust these fields based on the actual structure of medication data
            name = medication.get('name', '').lower()
            description = medication.get('description', '').lower()
            category = medication.get('category', '').lower()

            if (query in name or
                query in description or
                query in category):
                filtered_medications.append(medication)

        return Response(filtered_medications)

    except requests.RequestException as e:
        return Response(
            {"message": f"Error connecting to pharmacy service: {str(e)}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def health_check(request):
    """
    Health check endpoint to verify the service is running correctly
    """
    # Check database connection
    db_status = "OK"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    # Return health status
    return Response({
        "status": "UP",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "prescription-service",
        "database": db_status,
        "version": "1.0.0"
    })

@api_view(['GET', 'POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def prescription_list_create(request):
    """
    List all prescriptions or create a new prescription
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        # Filter prescriptions based on user role
        if 'DOCTOR' in roles:
            prescriptions = Prescription.objects.filter(doctor_id=user_id)
        elif 'PATIENT' in roles or 'CUSTOMER' in roles:
            prescriptions = Prescription.objects.filter(patient_id=user_id)
        elif 'ADMIN' in roles or 'PHARMACIST' in roles:
            prescriptions = Prescription.objects.all()
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only doctors can create prescriptions
        if 'DOCTOR' not in roles:
            return Response({"message": "Only doctors can create prescriptions"}, status=status.HTTP_403_FORBIDDEN)

        # Set the doctor_id from the authenticated user
        data = request.data.copy()
        data['doctor_id'] = user_id

        # Set status to ACTIVE if not specified
        if 'status' not in data:
            data['status'] = 'ACTIVE'

        # Debug log
        print(f"Creating prescription with data: {data}")

        # Create the serializer with the data
        serializer = PrescriptionSerializer(data=data)

        if serializer.is_valid():
            # Save the prescription and its items
            prescription = serializer.save()

            # Debug log
            print(f"Created prescription with ID: {prescription.id}")

            # Notify pharmacy service about the new prescription (if needed)
            # This would be implemented when the pharmacy service is ready

            # Return the created prescription data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Debug log
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def prescription_detail(request, pk):
    """
    Retrieve, update or delete a prescription
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        prescription = Prescription.objects.get(pk=pk)
    except Prescription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Check permissions
    if not ('ADMIN' in roles or 'PHARMACIST' in roles or
            ('DOCTOR' in roles and prescription.doctor_id == user_id) or
            (('PATIENT' in roles or 'CUSTOMER' in roles) and prescription.patient_id == user_id)):
        return Response({"message": "You don't have permission to access this prescription"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Only the prescribing doctor can update a prescription
        if not ('DOCTOR' in roles and prescription.doctor_id == user_id):
            return Response({"message": "Only the prescribing doctor can update a prescription"},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if prescription can be updated (not dispensed or cancelled)
        if prescription.status in ['DISPENSED', 'CANCELLED']:
            return Response({"message": f"Cannot update a prescription with status: {prescription.status}"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Use save() instead of update()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only the prescribing doctor can cancel a prescription
        if not ('DOCTOR' in roles and prescription.doctor_id == user_id):
            return Response({"message": "Only the prescribing doctor can cancel a prescription"},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if prescription can be cancelled (not dispensed)
        if prescription.status == 'DISPENSED':
            return Response({"message": "Cannot cancel a dispensed prescription"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update status to CANCELLED instead of deleting
        prescription.status = 'CANCELLED'
        prescription.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return None


@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def patient_prescriptions(request, patient_id):
    """
    List all prescriptions for a specific patient
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions
    if not ('ADMIN' in roles or 'DOCTOR' in roles or
            (('PATIENT' in roles or 'CUSTOMER' in roles) and int(patient_id) == user_id)):
        return Response({"message": "You don't have permission to access these prescriptions"},
                        status=status.HTTP_403_FORBIDDEN)

    prescriptions = Prescription.objects.filter(patient_id=patient_id)
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def doctor_prescriptions(request, doctor_id):
    """
    List all prescriptions by a specific doctor
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions
    if not ('ADMIN' in roles or
            ('DOCTOR' in roles and int(doctor_id) == user_id)):
        return Response({"message": "You don't have permission to access these prescriptions"},
                        status=status.HTTP_403_FORBIDDEN)

    prescriptions = Prescription.objects.filter(doctor_id=doctor_id)
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def verify_prescription(request, pk):
    """
    Verify if a prescription is valid for dispensing
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Only pharmacists and admins can verify prescriptions
    if not ('ADMIN' in roles or 'PHARMACIST' in roles):
        return Response({"message": "Only pharmacists can verify prescriptions"},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        prescription = Prescription.objects.get(pk=pk)
    except Prescription.DoesNotExist:
        return Response({"valid": False, "message": "Prescription not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if prescription is valid
    if prescription.status == 'ACTIVE':
        return Response({
            "valid": True,
            "prescription": PrescriptionSerializer(prescription).data
        })
    else:
        return Response({
            "valid": False,
            "message": f"Prescription is not valid for dispensing. Status: {prescription.status}"
        })

@api_view(['PUT'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
def update_prescription_status(request, pk):
    """
    Update the status of a prescription
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Only pharmacists, doctors, and admins can update prescription status
    if not ('ADMIN' in roles or 'PHARMACIST' in roles or 'DOCTOR' in roles):
        return Response({"message": "You don't have permission to update prescription status"},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        prescription = Prescription.objects.get(pk=pk)
    except Prescription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PrescriptionStatusUpdateSerializer(prescription, data=request.data)
    if serializer.is_valid():
        # Additional validation based on current status and role
        current_status = prescription.status
        new_status = serializer.validated_data['status']

        # Validate status transitions
        valid_transition = True
        message = ""

        if current_status == 'CANCELLED' and new_status != 'CANCELLED':
            valid_transition = False
            message = "Cannot change status of a cancelled prescription"
        elif current_status == 'DISPENSED' and new_status != 'DISPENSED':
            valid_transition = False
            message = "Cannot change status of a dispensed prescription"
        elif new_status == 'DISPENSED' and 'PHARMACIST' not in roles:
            valid_transition = False
            message = "Only pharmacists can mark a prescription as dispensed"
        elif new_status == 'CANCELLED' and 'DOCTOR' not in roles:
            valid_transition = False
            message = "Only doctors can cancel a prescription"

        if not valid_transition:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
