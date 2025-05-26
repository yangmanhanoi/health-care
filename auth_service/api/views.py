from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LoginSerializer, RegisterSerializer
from .models import User, Role
from django.contrib.auth.hashers import make_password
import requests

DOCTOR_SERVICE_URL = 'http://service-doctor:8002/api/info/'
PATIENT_SERVICE_URL = 'http://service-patient:8004/api/patients'
# Create your views here.
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterPatientView(CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Call patient_service to create patient record
            try:
                patient_payload = {
                    "user_id": user.id,
                    "email": request.data.get("email", ""),
                    "full_name": request.data.get("full_name", ""),
                    "phone": request.data.get("phone", ""),
                    "dob": request.data.get("dob", "1990-01-01"),
                    "gender": request.data.get("gender", "O"),
                    "address": request.data.get("address", "")
                }
                response = requests.post(f"{PATIENT_SERVICE_URL}/auth/register", json=patient_payload, timeout=5)
                response.raise_for_status()
            except Exception as e:
                print("Error contacting patient_service:", e)
                # Continue even if patient service call fails

            return Response({
                "message": "User registered successfully",
                "user": {
                    "username": user.username,
                    "roles": [role.name for role in user.roles.all()]
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def register_doctor(request):
    data = request.data

    username = data.get("username")
    email = data.get("contact")
    password = data.get("password")
    full_name = data.get("full_name")
    specialty = data.get("specialty")
    license_number = data.get("license_number")

    if User.objects.filter(username=username).exists():
        return Response({"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    role = Role.objects.filter(name="DOCTOR").first()

    if not role:
        return Response({"message": "Role 'doctor' not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user = User.objects.create_user(username=username, password=password)
    user.save()
    user.roles.add(role)

    # Gửi request tạo hồ sơ bác sĩ sang doctor_service
    try:
        doctor_payload = {
            "user_id": user.id,
            "full_name": full_name,
            "specialty": specialty,
            "license_number": license_number,
            "contact": email,
        }
        response = requests.post(DOCTOR_SERVICE_URL, json=doctor_payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print("Error contacting doctor_service:", e)

    return Response({"message": "Doctor account created successfully"}, status=status.HTTP_201_CREATED)
