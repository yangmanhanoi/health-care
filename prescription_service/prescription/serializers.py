from rest_framework import serializers
from .models import Prescription, PrescriptionItem, PrescriptionStatus

class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medication_id', 'medication_name', 'quantity',
            'dosage', 'frequency', 'duration', 'route', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient_id', 'doctor_id', 'date', 'diagnose',
            'status', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Override to ensure items are included in the representation
        """
        representation = super().to_representation(instance)
        representation['items'] = PrescriptionItemSerializer(instance.items.all(), many=True).data
        return representation

    def create(self, validated_data):
        # Extract items data from the validated data
        items_data = validated_data.pop('items', [])

        # Create the prescription
        prescription = Prescription.objects.create(**validated_data)

        # Create prescription items
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)

        return prescription

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update prescription items if provided
        if items_data is not None:
            # Clear existing items and create new ones
            instance.items.all().delete()
            for item_data in items_data:
                PrescriptionItem.objects.create(prescription=instance, **item_data)

        return instance

class PrescriptionStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['status']

    def validate_status(self, value):
        # Ensure the status is valid
        if value not in [choice[0] for choice in PrescriptionStatus.choices]:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join([choice[0] for choice in PrescriptionStatus.choices])}")
        return value
