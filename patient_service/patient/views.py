from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer
from core.utils.request_utils import extract_user_info_from_headers

@api_view(['GET', 'POST'])
def patient_list_create(request):
    """
    List all patients or create a new patient.
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        # If user is a patient (not admin/doctor/staff), only show their own record
        if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
            patients = Patient.objects.filter(user_id=user_id)
        else:
            patients = Patient.objects.all()

        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Create a copy of the request data and add the user_id
        data = request.data.copy()
        data['user_id'] = user_id

        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            patient = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def patient_detail(request, patient_id):
    """
    Retrieve, update or delete a patient.
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions: patients can only access their own records
    if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
        if patient.user_id != user_id:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only admin can delete patients
        if 'ADMIN' not in roles:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        patient.delete()
        return Response({"message": "Patient deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def patient_history(request, patient_id):
    """
    Get patient medical history.
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions: patients can only access their own records
    if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
        if patient.user_id != user_id:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Get patient history (placeholder implementation)
    history = patient.getHistoryRecord()
    return Response({"patient_id": patient_id, "history": history})

@api_view(['POST'])
def register_patient(request):
    """
    Register a new patient
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Create a copy of the request data and add the user_id
    data = request.data.copy()
    data['user_id'] = user_id

    # Check if a patient record already exists for this user
    if Patient.objects.filter(user_id=user_id).exists():
        return Response(
            {"message": "A patient record already exists for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = PatientSerializer(data=data)
    if serializer.is_valid():
        patient = serializer.save()
        patient.register()  # Call the register method
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_patient_profile(request, patient_id):
    """
    Update patient profile information
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions: patients can only update their own records
    if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
        if patient.user_id != user_id:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    serializer = PatientSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        patient.updateProfile()  # Call the updateProfile method
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
