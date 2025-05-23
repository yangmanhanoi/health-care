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
    user_id, roles, error_response = extract_user_info_from_headers(request)
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