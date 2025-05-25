from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer
import requests

@api_view(['POST'])
def register_patient_from_auth(request):
    """
    Register a new patient from auth_service.
    This endpoint is called by the auth_service when a new patient user is registered.
    """
    data = request.data
    
    user_id = data.get("user_id")
    email = data.get("email")
    full_name = data.get("full_name", "")
    phone = data.get("phone", "")
    
    if not user_id:
        return Response({"message": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if patient already exists
    if Patient.objects.filter(user_id=user_id).exists():
        return Response({"message": "Patient already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create patient with basic information
    patient_data = {
        'user_id': user_id,
        'fullName': full_name,
        'dob': data.get("dob", "1990-01-01"),  # Default date, should be updated later
        'gender': data.get("gender", "O"),  # Default to Other
        'phone': phone,
        'address': data.get("address", ""),
        'email': email or "",
    }
    
    serializer = PatientSerializer(data=patient_data)
    if serializer.is_valid():
        patient = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
