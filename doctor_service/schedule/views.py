from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import AvailabilitySerializer
from .models import Availability
from info.models import Doctor
import requests
import json
from core.utils.request_utils import extract_user_info_from_headers
# Create your views here.
@api_view(['GET', 'POST'])
def availability_list_create(request):
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if 'ADMIN' not in roles and 'DOCTOR' not in roles:
        return Response({"message": "You do not have permission to access this resource"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        if 'DOCTOR' in roles:
            try:
                doctor = Doctor.objects.get(user_id=user_id)
                availabilities = Availability.objects.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            availabilities = Availability.objects.all()
        serializer = AvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = AvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            # doctor_id = id trong bảng doctor
            doctor_id = request.data.get('doctor')
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                # check với user_id lấy từ token
                if doctor.user_id != user_id:
                    return Response({"message": "You do not have permission to create availability for this doctor"}, status=status.HTTP_403_FORBIDDEN)
            except Doctor.DoesNotExist:
                return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_availability_by_doctor(request, doctor_id):
    try:
        doctor = Doctor.objects.get(user_id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    availabilities = Availability.objects.filter(doctor=doctor)
    serializer = AvailabilitySerializer(availabilities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_availability_by_doctor_and_date(request, doctor_id, date):
    try:
        doctor = Doctor.objects.get(user_id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    availabilities = Availability.objects.filter(doctor=doctor, date=date)
    serializer = AvailabilitySerializer(availabilities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_availability_by_doctor_and_date_and_time(request, doctor_id, date):
    try:
        doctor = Doctor.objects.get(user_id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tham số thời gian bắt đầu và kết thúc từ query string
    start_time = request.GET.get('start_time')  # ví dụ: 09:00
    end_time = request.GET.get('end_time')      # ví dụ: 12:30
    filters = {'doctor': doctor, 'date': date}
    if start_time and end_time:
        filters['start_time__gte'] = start_time
        filters['end_time__lte'] = end_time
    availabilities = Availability.objects.filter(**filters)
    serializer = AvailabilitySerializer(availabilities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET', 'DELETE'])
def availability_detail(request, pk):

    try:
        availability = Availability.objects.get(pk=pk)
    except Availability.DoesNotExist:
        return Response({"message": "Availability not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AvailabilitySerializer(availability)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        user_id, roles, error_response = extract_user_info_from_headers(request)
        if error_response:
            return error_response
        if 'ADMIN' not in roles and availability.doctor.user_id != user_id:
            return Response({"message": "You do not have permission to access this availability"}, status=status.HTTP_403_FORBIDDEN)
        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Get appointments for the doctor from Appointment Service