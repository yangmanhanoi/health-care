from rest_framework import serializers
from .models import User, Role
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user and user.check_password(data['password']):
            refresh = RefreshToken.for_user(user)
            refresh['roles'] = [role.name for role in user.roles.all()]
            refresh['username'] = user.username
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        raise serializers.ValidationError("Invalid credentials")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)

        # Gán role PATIENT mặc định
        patient_role = Role.objects.get(name="PATIENT")
        user.roles.add(patient_role)
        user.save()
        return user