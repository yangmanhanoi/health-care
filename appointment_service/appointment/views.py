from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Appointment, AppointmentStatus
from .serializers import AppointmentSerializer
from core.utils.request_utils import extract_user_info_from_headers
ACTION_MAP = {
    "confirm": {"status": AppointmentStatus.CONFIRMED, "roles": ["staff"]},
    "deny": {"status": AppointmentStatus.DENIED, "roles": ["staff"]},
    "cancel_request": {"status": AppointmentStatus.REJECTION_REQUESTED, "roles": ["patient"]},
    "cancel_accept": {"status": AppointmentStatus.CANCELED, "roles": ["staff"]},
    "cancel_reject": {"status": AppointmentStatus.REJECTED, "roles": ["staff"]},
    "exchange_request": {"status": AppointmentStatus.EXCHANGE_REQUESTED, "roles": ["patient"]},
    "finish": {"status": AppointmentStatus.FINISHED, "roles": ["staff"]},
    "invoice": {"status": AppointmentStatus.INVOICED, "roles": ["staff"]},
}
# Create your views here.
@api_view(['GET', 'POST'])
def patient_appointment_list_create(request):
    user_id, _, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        appointments = Appointment.objects.filter(patient_id=user_id)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        data['patient_id'] = user_id
        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def check_in_appointment(request, appointment_id):
    """
    Update appointment status to DIAGNOSING when patient checks in
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can check in patients"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the doctor is the one assigned to this appointment
    if str(user_id) != str(appointment.doctor_id):
        return Response(
            {"message": "You can only check in your own appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if appointment is in a valid state to be checked in
    if appointment.status not in [AppointmentStatus.CONFIRMED, AppointmentStatus.SCHEDULED]:
        return Response(
            {"message": f"Cannot check in appointment with status {appointment.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update appointment status
    appointment.status = AppointmentStatus.DIAGNOSING
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def diagnose_appointment(request, appointment_id):
    """
    Update appointment diagnose field and change status to TESTING
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can diagnose patients"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the doctor is the one assigned to this appointment
    if str(user_id) != str(appointment.doctor_id):
        return Response(
            {"message": "You can only diagnose your own appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if appointment is in a valid state to be diagnosed
    if appointment.status != AppointmentStatus.DIAGNOSING:
        return Response(
            {"message": f"Cannot diagnose appointment with status {appointment.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get diagnose from request data
    diagnose = request.data.get('diagnose')
    if not diagnose:
        return Response(
            {"message": "Diagnose field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get need_lab_test from request data (default to False if not provided)
    need_lab_test = request.data.get('need_lab_test', False)

    # Update appointment
    appointment.diagnose = diagnose
    appointment.need_lab_test = need_lab_test

    # Set status based on need_lab_test value
    if need_lab_test:
        appointment.status = AppointmentStatus.TESTING
    else:
        appointment.status = AppointmentStatus.CONCLUDING

    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def complete_lab_test(request, appointment_id):
    """
    Update appointment status from TESTING to CONCLUDING after lab test completion
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can complete lab tests"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the doctor is the one assigned to this appointment
    if str(user_id) != str(appointment.doctor_id):
        return Response(
            {"message": "You can only complete lab tests for your own appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if appointment is in TESTING status
    if appointment.status != AppointmentStatus.TESTING:
        return Response(
            {"message": f"Cannot complete lab test for appointment with status {appointment.status}. Appointment must be in TESTING status."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update appointment status to CONCLUDING
    appointment.status = AppointmentStatus.CONCLUDING
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def conclude_appointment(request, appointment_id):
    """
    Update appointment conclusion field and change status to FINISHED
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can conclude appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the doctor is the one assigned to this appointment
    if str(user_id) != str(appointment.doctor_id):
        return Response(
            {"message": "You can only conclude your own appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if appointment is in a valid state to be concluded
    if appointment.status != AppointmentStatus.CONCLUDING:
        return Response(
            {"message": f"Cannot conclude appointment with status {appointment.status}. Appointment must be in CONCLUDING status."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get conclusion from request data
    conclusion = request.data.get('conclusion')
    if not conclusion:
        return Response(
            {"message": "Conclusion field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update appointment
    appointment.conclusion = conclusion
    appointment.status = AppointmentStatus.FINISHED
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)