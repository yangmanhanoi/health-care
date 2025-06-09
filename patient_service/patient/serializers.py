from rest_framework import serializers
from .models import Patient
from .services import UserServiceClient
from datetime import date

class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model with user information from user service."""
    
    # Read-only fields from user service
    user_info = serializers.SerializerMethodField()
    allergies_list = serializers.ReadOnlyField(source='get_allergies_list')
    chronic_conditions_list = serializers.ReadOnlyField(source='get_chronic_conditions_list')
    current_medications_list = serializers.ReadOnlyField(source='get_current_medications_list')
    bmi = serializers.ReadOnlyField(source='calculate_bmi')
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user_service_id', 'auth_user_id', 'blood_type', 'height', 'weight',
            'allergies', 'chronic_conditions', 'current_medications',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'insurance_provider', 'insurance_policy_number', 'insurance_group_number',
            'last_checkup_date', 'total_appointments', 'total_prescriptions',
            'preferred_language', 'communication_preference', 'is_active',
            'register_date', 'created_at', 'updated_at', 'user_info',
            'allergies_list', 'chronic_conditions_list', 'current_medications_list', 'bmi'
        ]
        read_only_fields = [
            'id', 'total_appointments', 'total_prescriptions', 'register_date',
            'created_at', 'updated_at'
        ]
    
    def get_user_info(self, obj):
        """Fetch user information from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        if user_data:
            return {
                'id': user_data.get('id'),
                'full_name': user_data.get('full_name'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'email': user_data.get('email'),
                'phone': user_data.get('phone'),
                'date_of_birth': user_data.get('date_of_birth'),
                'gender': user_data.get('gender'),
                'full_address': user_data.get('full_address'),
                'profile_picture': user_data.get('profile_picture'),
                'is_verified': user_data.get('is_verified'),
                'age': user_data.get('age'),
            }
        return None


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patients with user information."""
    
    # User information fields
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    date_of_birth = serializers.DateField(write_only=True)
    gender = serializers.CharField(write_only=True)
    address_line_1 = serializers.CharField(write_only=True, required=False)
    address_line_2 = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    postal_code = serializers.CharField(write_only=True, required=False)
    country = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Patient
        fields = [
            'auth_user_id', 'blood_type', 'height', 'weight', 'allergies',
            'chronic_conditions', 'current_medications', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'insurance_provider', 'insurance_policy_number', 'insurance_group_number',
            'preferred_language', 'communication_preference',
            # User fields
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'gender', 'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country'
        ]
    
    def validate_date_of_birth(self, value):
        """Validate date of birth."""
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
    
    def validate_auth_user_id(self, value):
        """Validate that auth_user_id is unique when creating a new patient."""
        if Patient.objects.filter(auth_user_id=value).exists():
            raise serializers.ValidationError("A patient with this auth_user_id already exists.")
        return value
    
    def create(self, validated_data):
        """Create patient with user information in user service."""
        # Extract user data
        user_data = {
            'auth_user_id': validated_data.get('auth_user_id'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone': validated_data.pop('phone', ''),
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'address_line_1': validated_data.pop('address_line_1', ''),
            'address_line_2': validated_data.pop('address_line_2', ''),
            'city': validated_data.pop('city', ''),
            'state': validated_data.pop('state', ''),
            'postal_code': validated_data.pop('postal_code', ''),
            'country': validated_data.pop('country', 'Vietnam'),
        }
        
        # Create user in user service
        user_client = UserServiceClient()
        user_response = user_client.create_patient_user(user_data)
        
        if not user_response:
            raise serializers.ValidationError("Failed to create user in user service")
        
        # Create patient with user service ID
        validated_data['user_service_id'] = user_response['id']
        
        return Patient.objects.create(**validated_data)


class PatientUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating patient information."""
    
    # User information fields that can be updated
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    address_line_1 = serializers.CharField(write_only=True, required=False)
    address_line_2 = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    postal_code = serializers.CharField(write_only=True, required=False)
    country = serializers.CharField(write_only=True, required=False)
    profile_picture = serializers.URLField(write_only=True, required=False)
    
    class Meta:
        model = Patient
        fields = [
            'blood_type', 'height', 'weight', 'allergies', 'chronic_conditions',
            'current_medications', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'insurance_provider', 'insurance_policy_number',
            'insurance_group_number', 'preferred_language', 'communication_preference',
            # User fields
            'first_name', 'last_name', 'phone', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country', 'profile_picture'
        ]
    
    def update(self, instance, validated_data):
        """Update patient and user information."""
        # Extract user data
        user_data = {}
        user_fields = [
            'first_name', 'last_name', 'phone', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'profile_picture'
        ]
        
        for field in user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        # Update user information in user service
        if user_data:
            user_client = UserServiceClient()
            user_client.update_user(str(instance.user_service_id), user_data)
        
        # Update patient information
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updateProfile()
        
        return instance


class PatientBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for patient information (for listings)."""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user_service_id', 'auth_user_id', 'blood_type',
            'total_appointments', 'total_prescriptions', 'is_active',
            'register_date', 'user_name', 'user_email', 'user_age'
        ]
    
    def get_user_name(self, obj):
        """Get user name from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('full_name') if user_data else None
    
    def get_user_email(self, obj):
        """Get user email from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('email') if user_data else None
    
    def get_user_age(self, obj):
        """Get user age from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('age') if user_data else None


# Legacy serializer for backward compatibility
class PatientLegacySerializer(serializers.ModelSerializer):
    """Legacy serializer for backward compatibility with old API."""
    user_id = serializers.IntegerField(source='auth_user_id')
    fullName = serializers.SerializerMethodField()
    dob = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    registerDate = serializers.DateTimeField(source='register_date')
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user_id', 'fullName', 'dob', 'gender', 'phone',
            'address', 'email', 'registerDate'
        ]
        read_only_fields = ['id', 'registerDate']
    
    def get_fullName(self, obj):
        """Get full name from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('full_name') if user_data else ''
    
    def get_dob(self, obj):
        """Get date of birth from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('date_of_birth') if user_data else None
    
    def get_gender(self, obj):
        """Get gender from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('gender') if user_data else ''
    
    def get_phone(self, obj):
        """Get phone from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('phone') if user_data else ''
    
    def get_address(self, obj):
        """Get address from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('full_address') if user_data else ''
    
    def get_email(self, obj):
        """Get email from user service."""
        user_client = UserServiceClient()
        user_data = user_client.get_user_by_id(str(obj.user_service_id))
        return user_data.get('email') if user_data else ''
