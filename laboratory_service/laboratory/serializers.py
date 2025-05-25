from rest_framework import serializers
from .models import TestType, LabTestOrder, LabTestOrderItem, TestResult, LabTestOrderStatus

class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = [
            'id', 'name', 'description', 'cost', 'unit',
            'normal_range', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = [
            'id', 'order_item', 'result_value', 'normal_range',
            'unit', 'technician_notes', 'result_date',
            'verified_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class LabTestOrderItemSerializer(serializers.ModelSerializer):
    test_type_details = TestTypeSerializer(source='test_type', read_only=True)
    result_details = TestResultSerializer(source='result', read_only=True)
    price = serializers.ReadOnlyField()  # Include the price property

    class Meta:
        model = LabTestOrderItem
        fields = [
            'id', 'order', 'test_type', 'test_type_details',
            'status', 'price', 'result_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'price', 'created_at', 'updated_at']
        extra_kwargs = {
            'order': {'required': False}  # Make order field not required during validation
        }

class LabTestOrderSerializer(serializers.ModelSerializer):
    items = LabTestOrderItemSerializer(many=True, required=False)

    class Meta:
        model = LabTestOrder
        fields = [
            'id', 'patient_id', 'doctor_id', 'appointment_id', 'request_date',
            'status', 'clinical_notes', 'urgency', 'collection_date',
            'completion_date', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Override to ensure items are included in the representation
        """
        representation = super().to_representation(instance)
        representation['items'] = LabTestOrderItemSerializer(instance.items.all(), many=True).data
        return representation

    def create(self, validated_data):
        # Extract items data from the validated data
        items_data = validated_data.pop('items', [])

        # Create the lab test order
        lab_test_order = LabTestOrder.objects.create(**validated_data)

        # Create lab test order items
        for item_data in items_data:
            # Ensure we don't try to pass 'order' if it's in the data
            if 'order' in item_data:
                item_data.pop('order')
            LabTestOrderItem.objects.create(order=lab_test_order, **item_data)

        return lab_test_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update lab test order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update lab test order items if provided
        if items_data is not None:
            # Clear existing items and create new ones
            instance.items.all().delete()
            for item_data in items_data:
                # Ensure we don't try to pass 'order' if it's in the data
                if 'order' in item_data:
                    item_data.pop('order')
                LabTestOrderItem.objects.create(order=instance, **item_data)

        return instance

class LabTestOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestOrder
        fields = ['status']

    def validate_status(self, value):
        # Ensure the status is valid
        if value not in [choice[0] for choice in LabTestOrderStatus.choices]:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join([choice[0] for choice in LabTestOrderStatus.choices])}")
        return value

class LabTestOrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestOrderItem
        fields = ['status']

    def validate_status(self, value):
        # Ensure the status is valid
        if value not in [choice[0] for choice in LabTestOrderStatus.choices]:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join([choice[0] for choice in LabTestOrderStatus.choices])}")
        return value

class AppointmentTestItemsSerializer(serializers.Serializer):
    """
    Serializer for appointment test items response with pricing information
    """
    appointment_id = serializers.IntegerField()
    total_test_items = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    test_items = LabTestOrderItemSerializer(many=True)