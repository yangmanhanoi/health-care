# pharmacy/serializers.py

from rest_framework import serializers
from .models import Pharmacy, Pharmacist, Medicine, DispenseRecord, DispenseItem

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

class PharmacistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacist
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class DispenseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispenseItem
        fields = '__all__'

class DispenseRecordSerializer(serializers.ModelSerializer):
    dispense_items  = DispenseItemSerializer(many=True, read_only=True)


    class Meta:
        model = DispenseRecord
        fields = ['id', 'prescriptionId', 'pharmacistId', 'date', 'pharmacyId', 'dispense_items']

    def create(self, validated_data):
        items_data = validated_data.pop('dispense_items')
        record = DispenseRecord.objects.create(**validated_data)

        for item in items_data:
            DispenseItem.objects.create(dispenseRecordId=record, **item)
            # Reduce medicine stock
            medicine = Medicine.objects.get(id=item['medicineId'])
            medicine.quantity -= item['quantity']
            medicine.save()

        return record