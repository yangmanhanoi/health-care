from rest_framework import serializers
from .models import Doctor
from .services import UserServiceClient

class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model with user information from user service."""
    
    # Read-only fields from user service
    user_info = serializers.SerializerMethodField()
    specialties = serializers.ReadOnlyField(source='get_specialties')
    certifications_list = serializers.ReadOnlyField(source='get_certifications_list')
    languages_list = serializers.ReadOnlyField(source='get_languages_list')
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user_service_id', 'auth_user_id', 'specialty', 'sub_specialty',
            'license_number', 'medical_school', 'graduation_year', 'experience_level',
            'years_of_experience', 'hospital_affiliation', 'clinic_address',
            'consultation_fee', 'consultation_types', 'is_available',
            'max_patients_per_day', 'consultation_duration', 'certifications',
            'languages_spoken', 'average_rating', 'total_reviews',
            'total_consultations', 'is_verified', 'verification_date',
            'created_at', 'updated_at', 'user_info', 'specialties',
            'certifications_list', 'languages_list'
        ]
        read_only_fields = [
            'id', 'average_rating', 'total_reviews', 'total_consultations',
            'created_at', 'updated_at', 'verification_date'
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
                'profile_picture': user_data.get('profile_picture'),
                'is_verified': user_data.get('is_verified'),
                'age': user_data.get('age'),
            }
        return None


class DoctorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctors with user information."""
    
    # User information fields
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    date_of_birth = serializers.DateField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    address_line_1 = serializers.CharField(write_only=True, required=False)
    address_line_2 = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    postal_code = serializers.CharField(write_only=True, required=False)
    country = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Doctor
        fields = [
            'auth_user_id', 'specialty', 'sub_specialty', 'license_number',
            'medical_school', 'graduation_year', 'experience_level',
            'years_of_experience', 'hospital_affiliation', 'clinic_address',
            'consultation_fee', 'consultation_types', 'max_patients_per_day',
            'consultation_duration', 'certifications', 'languages_spoken',
            # User fields
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'gender', 'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country'
        ]
    
    def create(self, validated_data):
        """Create doctor with user information in user service."""
        # Extract user data
        user_data = {
            'auth_user_id': validated_data.pop('auth_user_id'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone': validated_data.pop('phone', ''),
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'gender': validated_data.pop('gender', ''),
            'address_line_1': validated_data.pop('address_line_1', ''),
            'address_line_2': validated_data.pop('address_line_2', ''),
            'city': validated_data.pop('city', ''),
            'state': validated_data.pop('state', ''),
            'postal_code': validated_data.pop('postal_code', ''),
            'country': validated_data.pop('country', 'Vietnam'),
        }
        
        # Create user in user service
        user_client = UserServiceClient()
        user_response = user_client.create_doctor_user(user_data)
        
        if not user_response:
            raise serializers.ValidationError("Failed to create user in user service")
        
        # Create doctor with user service ID
        validated_data['user_service_id'] = user_response['id']
        validated_data['auth_user_id'] = user_data['auth_user_id']
        
        return Doctor.objects.create(**validated_data)


class DoctorUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating doctor information."""
    
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
    bio = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Doctor
        fields = [
            'specialty', 'sub_specialty', 'medical_school', 'graduation_year',
            'experience_level', 'years_of_experience', 'hospital_affiliation',
            'clinic_address', 'consultation_fee', 'consultation_types',
            'is_available', 'max_patients_per_day', 'consultation_duration',
            'certifications', 'languages_spoken',
            # User fields
            'first_name', 'last_name', 'phone', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'profile_picture', 'bio'
        ]
    
    def update(self, instance, validated_data):
        """Update doctor and user information."""
        # Extract user data
        user_data = {}
        user_fields = [
            'first_name', 'last_name', 'phone', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'profile_picture', 'bio'
        ]
        
        for field in user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        # Update user information in user service
        if user_data:
            user_client = UserServiceClient()
            user_client.update_user(str(instance.user_service_id), user_data)
        
        # Update doctor information
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class DoctorBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for doctor information (for listings)."""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user_service_id', 'specialty', 'license_number',
            'experience_level', 'years_of_experience', 'consultation_fee',
            'average_rating', 'total_reviews', 'is_available',
            'user_name', 'user_email'
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

