from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import DoctorSerializer
from .models import Doctor
import json

@api_view(['GET'])
def list_doctors(request):
    """
    List all doctors with optional search by specialty
    """
    specialty = request.query_params.get('specialty', None)
    search = request.query_params.get('search', None)

    doctors = Doctor.objects.all()

    if specialty:
        doctors = doctors.filter(specialty__icontains=specialty)

    if search:
        doctors = doctors.filter(full_name__icontains=search)

    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_doctor(request, doctor_id):
    try:
        doctor = Doctor.objects.get(user_id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)
# Create your views here.
@api_view(['POST'])
def create_doctor(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_doctor_profile(request, user_id):
    try:
        doctor = Doctor.objects.get(user_id=user_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor profile not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)

# api update profile chỉ với quyền admin hoặc chính doctor đó
@api_view(['PUT', 'PATCH'])
def update_doctor_profile(request, user_id):
    request_user_id = request.headers.get("X-User-Id")
    roles_raw = request.headers.get('X-User-Roles')

    if not request_user_id:
        return Response({"message": "Missing X-User-Id"}, status=status.HTTP_401_UNAUTHORIZED)


    try:
        roles = json.loads(roles_raw) if roles_raw else []
        request_user_id = int(request_user_id)
    except json.JSONDecodeError:
        return Response({"error": "Invalid roles format"}, status=status.HTTP_403_FORBIDDEN)
    if 'ADMIN' not in roles and request_user_id != user_id:
        return Response({"message": "You do not have permission to update this profile"}, status=status.HTTP_403_FORBIDDEN)

    try:
        doctor = Doctor.objects.get(user_id=user_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorSerializer(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)