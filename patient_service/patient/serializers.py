from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'user_id', 'fullName', 'dob', 'gender', 'phone',
            'address', 'email', 'registerDate'
        ]
        read_only_fields = ['id', 'registerDate']

    def validate_user_id(self, value):
        """Validate that user_id is unique when creating a new patient."""
        if self.instance is None:  # Creating new patient
            if Patient.objects.filter(user_id=value).exists():
                raise serializers.ValidationError("A patient with this user_id already exists.")
        return value

    def validate_dob(self, value):
        """Validate date of birth."""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
