from rest_framework import serializers
from .models import User, UserActivity


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with full information."""
    age = serializers.ReadOnlyField(source='get_age')
    full_address = serializers.ReadOnlyField(source='get_full_address')
    
    class Meta:
        model = User
        fields = [
            'id', 'auth_user_id', 'user_type', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'gender', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state', 
            'postal_code', 'country', 'is_active', 'is_verified',
            'created_at', 'updated_at', 'last_login', 'profile_picture',
            'bio', 'age', 'full_address'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    class Meta:
        model = User
        fields = [
            'auth_user_id', 'user_type', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'profile_picture', 'bio'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 
            'phone', 'address_line_1', 'address_line_2', 'city', 
            'state', 'postal_code', 'country', 'profile_picture', 'bio'
        ]


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer for basic user information (for external services)."""
    age = serializers.ReadOnlyField(source='get_age')
    
    class Meta:
        model = User
        fields = [
            'id', 'auth_user_id', 'user_type', 'first_name', 'last_name',
            'full_name', 'email', 'phone', 'is_active', 'is_verified',
            'created_at', 'age'
        ]
        read_only_fields = ['id', 'created_at', 'full_name']


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity tracking."""
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.full_name')
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'user_name', 'activity_type',
            'description', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DoctorUserSerializer(serializers.ModelSerializer):
    """Specialized serializer for doctor users."""
    age = serializers.ReadOnlyField(source='get_age')
    
    class Meta:
        model = User
        fields = [
            'id', 'auth_user_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'email', 'phone', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'is_active', 'is_verified', 'created_at', 'profile_picture',
            'bio', 'age'
        ]
        read_only_fields = ['id', 'created_at', 'full_name']


class PatientUserSerializer(serializers.ModelSerializer):
    """Specialized serializer for patient users."""
    age = serializers.ReadOnlyField(source='get_age')
    full_address = serializers.ReadOnlyField(source='get_full_address')
    
    class Meta:
        model = User
        fields = [
            'id', 'auth_user_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'email', 'phone', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'is_active', 'is_verified', 'created_at', 'profile_picture',
            'age', 'full_address'
        ]
        read_only_fields = ['id', 'created_at', 'full_name']
