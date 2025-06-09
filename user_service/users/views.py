from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import User, UserActivity
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserBasicSerializer, UserActivitySerializer, DoctorUserSerializer,
    PatientUserSerializer
)


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # Adjust based on your auth requirements
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserBasicSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if user_type is not None:
            queryset = queryset.filter(user_type=user_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Adjust based on your auth requirements
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_auth_id(request, auth_user_id):
    """Get user by auth service user ID."""
    try:
        user = User.objects.get(auth_user_id=auth_user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_email(request, email):
    """Get user by email."""
    try:
        user = User.objects.get(email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_doctor_user(request):
    """Create a new doctor user."""
    data = request.data.copy()
    data['user_type'] = 'doctor'
    
    serializer = UserCreateSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = DoctorUserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_patient_user(request):
    """Create a new patient user."""
    data = request.data.copy()
    data['user_type'] = 'patient'
    
    serializer = UserCreateSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = PatientUserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_doctors(request):
    """Get all doctor users."""
    doctors = User.objects.filter(user_type='doctor', is_active=True)
    serializer = DoctorUserSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_patients(request):
    """Get all patient users."""
    patients = User.objects.filter(user_type='patient', is_active=True)
    serializer = PatientUserSerializer(patients, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_last_login(request, user_id):
    """Update user's last login timestamp."""
    try:
        user = User.objects.get(id=user_id)
        user.update_last_login()
        return Response({'message': 'Last login updated successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_user(request, user_id):
    """Verify a user account."""
    try:
        user = User.objects.get(id=user_id)
        user.verify()
        return Response({'message': 'User verified successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def deactivate_user(request, user_id):
    """Deactivate a user account."""
    try:
        user = User.objects.get(id=user_id)
        user.deactivate()
        return Response({'message': 'User deactivated successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def activate_user(request, user_id):
    """Activate a user account."""
    try:
        user = User.objects.get(id=user_id)
        user.activate()
        return Response({'message': 'User activated successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def log_user_activity(request):
    """Log user activity."""
    serializer = UserActivitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_activities(request, user_id):
    """Get user activities."""
    try:
        user = User.objects.get(id=user_id)
        activities = UserActivity.objects.filter(user=user)
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'service': 'user_service',
        'timestamp': timezone.now()
    })
