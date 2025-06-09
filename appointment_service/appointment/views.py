from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Appointment, AppointmentStatus
from .serializers import AppointmentSerializer
from core.utils.request_utils import extract_user_info_from_headers
import requests
from decimal import Decimal
import logging

# Service URL Constants
DOCTOR_SERVICE_BASE_URL = "http://service-doctor:8003/api"
PATIENT_SERVICE_BASE_URL = "http://service-patient:8004/api"
LABORATORY_SERVICE_BASE_URL = "http://service-laboratory:8005/api"

# Specific endpoint constants
DOCTOR_INFO_URL = f"{DOCTOR_SERVICE_BASE_URL}/info/doctors"
DOCTOR_SCHEDULE_URL = f"{DOCTOR_SERVICE_BASE_URL}/schedule/availabilities"
PATIENT_LIST_URL = f"{PATIENT_SERVICE_BASE_URL}/patients"
LABORATORY_TEST_ITEMS_URL = f"{LABORATORY_SERVICE_BASE_URL}/appointment"
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
            # Hardcode the price to 100000 when creating appointment
            appointment = serializer.save(price=100000.00)
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

@api_view(['GET'])
def get_appointment_total_price(request, appointment_id):
    """
    Get appointment total price including test results
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check permissions - users can only view their own appointments or doctors can view their patients' appointments
    if not ('ADMIN' in roles or
            ('DOCTOR' in roles and str(appointment.doctor_id) == str(user_id)) or
            (('PATIENT' in roles or 'CUSTOMER' in roles) and str(appointment.patient_id) == str(user_id))):
        return Response(
            {"message": "You don't have permission to view this appointment"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Initialize response data
    response_data = {
        "appointment_id": appointment_id,
        "price": float(appointment.price),
        "test_results": [],
        "totalPrice": float(appointment.price)
    }

    # Call laboratory service to get test results
    try:
        # Forward the authentication headers to the laboratory service
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')  # Convert to JSON format
        }

        lab_response = requests.get(
            f"{LABORATORY_TEST_ITEMS_URL}/{appointment_id}/test-items/",
            headers=headers,
            timeout=10
        )

        if lab_response.status_code == 200:
            lab_data = lab_response.json()
            response_data["test_results"] = lab_data.get("test_items", [])
            test_cost = lab_data.get("total_cost", 0)
            response_data["totalPrice"] = float(appointment.price) + float(test_cost)
        elif lab_response.status_code == 404:
            # No test results found - this is okay, just use appointment price
            pass
        else:
            # Log the error but don't fail the request
            print(f"Laboratory service returned status {lab_response.status_code}")

    except requests.exceptions.RequestException as e:
        # Log the error but don't fail the request - laboratory service might be down
        print(f"Error calling laboratory service: {str(e)}")
        # Continue with just the appointment price

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def doctor_appointment_list(request):
    """
    Get all appointments for the authenticated doctor with patient information
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get appointments for this doctor
    appointments = Appointment.objects.filter(doctor_id=user_id).order_by('-date', '-time')
    serializer = AppointmentSerializer(appointments, many=True)
    appointments_data = serializer.data

    # Enrich each appointment with patient information
    for appointment_data in appointments_data:
        try:
            # The patient_id in appointment is actually the user_id from auth service
            # We need to get all patients and find the one with matching user_id
            # Forward the authentication headers to the patient service
            headers = {
                'X-User-Id': str(user_id),
                'X-User-Roles': str(roles).replace("'", '"')  # Convert to JSON format
            }

            patient_response = requests.get(
                f"{PATIENT_LIST_URL}/",
                headers=headers,
                timeout=10
            )

            if patient_response.status_code == 200:
                patients_list = patient_response.json()
                logging.info(f"Retrieved {len(patients_list)} patients from patient service")

                # Find the patient with matching user_id
                patient_info = None
                for patient in patients_list:
                    logging.info(f"Checking patient user_id: {patient.get('user_id')} against appointment patient_id: {appointment_data['patient_id']}")
                    if str(patient.get('user_id')) == str(appointment_data['patient_id']):
                        patient_info = patient
                        logging.info(f"Found matching patient: {patient.get('fullName')}")
                        break

                appointment_data['patient_info'] = patient_info
                if not patient_info:
                    logging.warning(f"No patient found with user_id {appointment_data['patient_id']} in {len(patients_list)} patients")
                    # Log all available user_ids for debugging
                    available_user_ids = [str(p.get('user_id')) for p in patients_list]
                    logging.warning(f"Available user_ids: {available_user_ids}")
            else:
                appointment_data['patient_info'] = None
                logging.warning(f"Failed to get patients list: {patient_response.status_code} - {patient_response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error calling patient service: {e}")
            appointment_data['patient_info'] = None

    return Response(appointments_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def doctor_appointment_detail(request, appointment_id):
    """
    Get detailed appointment information for doctors including patient details
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is a doctor
    if 'DOCTOR' not in roles:
        return Response(
            {"message": "Only doctors can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if this doctor owns the appointment
    if str(appointment.doctor_id) != str(user_id):
        return Response(
            {"message": "You don't have permission to view this appointment"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Serialize appointment data
    appointment_data = AppointmentSerializer(appointment).data

    # Get patient information
    try:
        # The patient_id in appointment is actually the user_id from auth service
        # Forward the authentication headers to the patient service
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        patient_response = requests.get(
            f"{PATIENT_LIST_URL}/",
            headers=headers,
            timeout=10
        )

        if patient_response.status_code == 200:
            patients_list = patient_response.json()
            # Find the patient with matching user_id
            patient_info = None
            for patient in patients_list:
                if str(patient.get('user_id')) == str(appointment.patient_id):
                    patient_info = patient
                    break

            appointment_data['patient_info'] = patient_info
            if not patient_info:
                logging.warning(f"No patient found with user_id {appointment.patient_id}")
        else:
            appointment_data['patient_info'] = None
            logging.warning(f"Failed to get patients list: {patient_response.status_code} - {patient_response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling patient service: {e}")
        appointment_data['patient_info'] = None

    # Get lab test results if needed
    if appointment.need_lab_test:
        try:
            headers = {
                'X-User-Id': str(user_id),
                'X-User-Roles': str(roles).replace("'", '"')
            }

            lab_response = requests.get(
                f"{LABORATORY_TEST_ITEMS_URL}/{appointment_id}/test-items/",
                headers=headers,
                timeout=10
            )

            if lab_response.status_code == 200:
                lab_data = lab_response.json()
                appointment_data['test_results'] = lab_data.get("test_items", [])
                test_cost = lab_data.get("total_cost", 0)
                appointment_data['total_price'] = float(appointment.price) + float(test_cost)
            else:
                appointment_data['test_results'] = []
                appointment_data['total_price'] = float(appointment.price)
                logging.warning(f"Failed to get lab results for appointment {appointment_id}: {lab_response.status_code}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error calling laboratory service: {e}")
            appointment_data['test_results'] = []
            appointment_data['total_price'] = float(appointment.price)
    else:
        appointment_data['test_results'] = []
        appointment_data['total_price'] = float(appointment.price)

    return Response(appointment_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_patient_service(request):
    """
    Test endpoint to check patient service connectivity
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        patient_response = requests.get(
            f"{PATIENT_LIST_URL}/",
            headers=headers,
            timeout=10
        )

        return Response({
            "status_code": patient_response.status_code,
            "response_text": patient_response.text[:500],  # First 500 chars
            "headers_sent": headers,
            "user_id": user_id,
            "roles": roles
        }, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response({
            "error": str(e),
            "headers_sent": headers,
            "user_id": user_id,
            "roles": roles
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_doctor_info(request, doctor_id):
    """
    Get doctor information from doctor service
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        # Call doctor service to get doctor information
        doctor_response = requests.get(
            f"{DOCTOR_INFO_URL}/{doctor_id}",
            headers=headers,
            timeout=10
        )

        if doctor_response.status_code == 200:
            doctor_data = doctor_response.json()
            return Response(doctor_data, status=status.HTTP_200_OK)
        elif doctor_response.status_code == 404:
            return Response(
                {"message": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {"message": f"Error fetching doctor information: {doctor_response.status_code}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling doctor service: {e}")
        return Response(
            {"message": "Unable to connect to doctor service"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def get_patient_info(request, patient_id):
    """
    Get patient information from patient service
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions - only doctors, staff, admin, or the patient themselves can access
    if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
        # If user is a patient, they can only access their own information
        # We need to check if this patient_id corresponds to their user_id
        try:
            headers = {
                'X-User-Id': str(user_id),
                'X-User-Roles': str(roles).replace("'", '"')
            }

            patient_response = requests.get(
                f"{PATIENT_LIST_URL}/{patient_id}",
                headers=headers,
                timeout=10
            )

            if patient_response.status_code == 200:
                patient_data = patient_response.json()
                if patient_data.get('user_id') != user_id:
                    return Response(
                        {"message": "You can only access your own patient information"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {"message": "Patient not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except requests.exceptions.RequestException:
            return Response(
                {"message": "Unable to verify patient access"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        # Call patient service to get patient information
        patient_response = requests.get(
            f"{PATIENT_LIST_URL}/{patient_id}",
            headers=headers,
            timeout=10
        )

        if patient_response.status_code == 200:
            patient_data = patient_response.json()
            return Response(patient_data, status=status.HTTP_200_OK)
        elif patient_response.status_code == 404:
            return Response(
                {"message": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {"message": f"Error fetching patient information: {patient_response.status_code}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling patient service: {e}")
        return Response(
            {"message": "Unable to connect to patient service"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def get_appointment_full_details(request, appointment_id):
    """
    Get appointment with complete doctor and patient information
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {"message": "Appointment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check permissions
    if not ('ADMIN' in roles or
            ('DOCTOR' in roles and str(appointment.doctor_id) == str(user_id)) or
            (('PATIENT' in roles or 'CUSTOMER' in roles) and str(appointment.patient_id) == str(user_id))):
        return Response(
            {"message": "You don't have permission to view this appointment"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Serialize appointment data
    appointment_data = AppointmentSerializer(appointment).data

    headers = {
        'X-User-Id': str(user_id),
        'X-User-Roles': str(roles).replace("'", '"')
    }

    # Get doctor information
    try:
        doctor_response = requests.get(
            f"{DOCTOR_INFO_URL}/{appointment.doctor_id}",
            headers=headers,
            timeout=10
        )

        if doctor_response.status_code == 200:
            appointment_data['doctor_info'] = doctor_response.json()
        else:
            appointment_data['doctor_info'] = None
            logging.warning(f"Failed to get doctor info for doctor_id {appointment.doctor_id}: {doctor_response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling doctor service: {e}")
        appointment_data['doctor_info'] = None

    # Get patient information
    try:
        # First get all patients to find the one with matching user_id
        patient_response = requests.get(
            f"{PATIENT_LIST_URL}/",
            headers=headers,
            timeout=10
        )

        if patient_response.status_code == 200:
            patients_list = patient_response.json()
            patient_info = None
            for patient in patients_list:
                if str(patient.get('user_id')) == str(appointment.patient_id):
                    patient_info = patient
                    break

            appointment_data['patient_info'] = patient_info
            if not patient_info:
                logging.warning(f"No patient found with user_id {appointment.patient_id}")
        else:
            appointment_data['patient_info'] = None
            logging.warning(f"Failed to get patients list: {patient_response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling patient service: {e}")
        appointment_data['patient_info'] = None

    # Get lab test results if needed
    if appointment.need_lab_test:
        try:
            lab_response = requests.get(
                f"{LABORATORY_TEST_ITEMS_URL}/{appointment_id}/test-items/",
                headers=headers,
                timeout=10
            )

            if lab_response.status_code == 200:
                lab_data = lab_response.json()
                appointment_data['test_results'] = lab_data.get("test_items", [])
                test_cost = lab_data.get("total_cost", 0)
                appointment_data['total_price'] = float(appointment.price) + float(test_cost)
            else:
                appointment_data['test_results'] = []
                appointment_data['total_price'] = float(appointment.price)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error calling laboratory service: {e}")
            appointment_data['test_results'] = []
            appointment_data['total_price'] = float(appointment.price)
    else:
        appointment_data['test_results'] = []
        appointment_data['total_price'] = float(appointment.price)

    return Response(appointment_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_doctors(request):
    """
    Search doctors for appointment booking
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Get search parameters
    specialty = request.query_params.get('specialty', None)
    search = request.query_params.get('search', None)

    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        # Build query parameters
        params = {}
        if specialty:
            params['specialty'] = specialty
        if search:
            params['search'] = search

        # Call doctor service to search doctors
        doctor_response = requests.get(
            f"{DOCTOR_INFO_URL}/",
            headers=headers,
            params=params,
            timeout=10
        )

        if doctor_response.status_code == 200:
            doctors_data = doctor_response.json()

            # For each doctor, also get their availability information
            for doctor in doctors_data:
                try:
                    # Get doctor's availability from schedule service
                    availability_response = requests.get(
                        f"{DOCTOR_SCHEDULE_URL}/doctor/{doctor['user_id']}",
                        headers=headers,
                        timeout=5
                    )

                    if availability_response.status_code == 200:
                        doctor['availabilities'] = availability_response.json()
                    else:
                        doctor['availabilities'] = []

                except requests.exceptions.RequestException:
                    doctor['availabilities'] = []
                    logging.warning(f"Could not fetch availability for doctor {doctor['user_id']}")

            return Response(doctors_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": f"Error searching doctors: {doctor_response.status_code}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling doctor service: {e}")
        return Response(
            {"message": "Unable to connect to doctor service"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def get_patient_history(request, patient_id):
    """
    Get patient medical history from patient service
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check permissions - only doctors, staff, admin, or the patient themselves can access
    if not any(role in ['ADMIN', 'DOCTOR', 'STAFF'] for role in roles):
        # If user is a patient, they can only access their own history
        try:
            headers = {
                'X-User-Id': str(user_id),
                'X-User-Roles': str(roles).replace("'", '"')
            }

            patient_response = requests.get(
                f"{PATIENT_LIST_URL}/{patient_id}",
                headers=headers,
                timeout=10
            )

            if patient_response.status_code == 200:
                patient_data = patient_response.json()
                if patient_data.get('user_id') != user_id:
                    return Response(
                        {"message": "You can only access your own medical history"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {"message": "Patient not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except requests.exceptions.RequestException:
            return Response(
                {"message": "Unable to verify patient access"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    try:
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Roles': str(roles).replace("'", '"')
        }

        # Call patient service to get patient history
        history_response = requests.get(
            f"{PATIENT_LIST_URL}/{patient_id}/history",
            headers=headers,
            timeout=10
        )

        if history_response.status_code == 200:
            history_data = history_response.json()

            # Also get appointment history for this patient
            try:
                # Get patient's user_id first
                patient_response = requests.get(
                    f"{PATIENT_LIST_URL}/{patient_id}",
                    headers=headers,
                    timeout=10
                )

                if patient_response.status_code == 200:
                    patient_data = patient_response.json()
                    patient_user_id = patient_data.get('user_id')

                    # Get appointments for this patient
                    appointments = Appointment.objects.filter(
                        patient_id=patient_user_id,
                        status__in=[AppointmentStatus.FINISHED, AppointmentStatus.INVOICED]
                    ).order_by('-date', '-time')

                    appointment_history = []
                    for appointment in appointments:
                        appointment_data = AppointmentSerializer(appointment).data

                        # Get doctor info for each appointment
                        try:
                            doctor_response = requests.get(
                                f"{DOCTOR_INFO_URL}/{appointment.doctor_id}",
                                headers=headers,
                                timeout=5
                            )
                            if doctor_response.status_code == 200:
                                appointment_data['doctor_info'] = doctor_response.json()
                        except requests.exceptions.RequestException:
                            appointment_data['doctor_info'] = None

                        appointment_history.append(appointment_data)

                    history_data['appointment_history'] = appointment_history
                else:
                    history_data['appointment_history'] = []

            except Exception as e:
                logging.error(f"Error getting appointment history: {e}")
                history_data['appointment_history'] = []

            return Response(history_data, status=status.HTTP_200_OK)
        elif history_response.status_code == 404:
            return Response(
                {"message": "Patient history not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {"message": f"Error fetching patient history: {history_response.status_code}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling patient service: {e}")
        return Response(
            {"message": "Unable to connect to patient service"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def get_all_appointments_enriched(request):
    """
    Get all appointments with doctor and patient information (Admin only)
    """
    user_id, roles, error_response = extract_user_info_from_headers(request)
    if error_response:
        return error_response

    # Check if user is admin
    if 'ADMIN' not in roles:
        return Response(
            {"message": "Only administrators can access all appointments"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get query parameters for filtering
    status_filter = request.query_params.get('status', None)
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)
    doctor_id = request.query_params.get('doctor_id', None)

    # Build query
    appointments_query = Appointment.objects.all()

    if status_filter:
        appointments_query = appointments_query.filter(status=status_filter)
    if date_from:
        appointments_query = appointments_query.filter(date__gte=date_from)
    if date_to:
        appointments_query = appointments_query.filter(date__lte=date_to)
    if doctor_id:
        appointments_query = appointments_query.filter(doctor_id=doctor_id)

    appointments = appointments_query.order_by('-date', '-time')
    appointments_data = AppointmentSerializer(appointments, many=True).data

    headers = {
        'X-User-Id': str(user_id),
        'X-User-Roles': str(roles).replace("'", '"')
    }

    # Enrich each appointment with doctor and patient information
    for appointment_data in appointments_data:
        # Get doctor information
        try:
            doctor_response = requests.get(
                f"{DOCTOR_INFO_URL}/{appointment_data['doctor_id']}",
                headers=headers,
                timeout=5
            )
            if doctor_response.status_code == 200:
                appointment_data['doctor_info'] = doctor_response.json()
            else:
                appointment_data['doctor_info'] = None
        except requests.exceptions.RequestException:
            appointment_data['doctor_info'] = None

        # Get patient information
        try:
            patient_response = requests.get(
                f"{PATIENT_LIST_URL}/",
                headers=headers,
                timeout=5
            )
            if patient_response.status_code == 200:
                patients_list = patient_response.json()
                patient_info = None
                for patient in patients_list:
                    if str(patient.get('user_id')) == str(appointment_data['patient_id']):
                        patient_info = patient
                        break
                appointment_data['patient_info'] = patient_info
            else:
                appointment_data['patient_info'] = None
        except requests.exceptions.RequestException:
            appointment_data['patient_info'] = None

    return Response({
        "total_count": len(appointments_data),
        "appointments": appointments_data
    }, status=status.HTTP_200_OK)