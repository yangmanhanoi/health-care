from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'user_id', 'full_name', 'specialty', 'license_number', 'contact', 'created_at']

