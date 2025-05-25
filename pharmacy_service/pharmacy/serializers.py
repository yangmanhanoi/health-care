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
    medicineId = serializers.IntegerField(write_only=True)

    class Meta:
        model = DispenseItem
        fields = ['medicineId', 'quantity', 'price']


class DispenseRecordSerializer(serializers.ModelSerializer):
    dispense_items  = DispenseItemSerializer(many=True, write_only=True)


    class Meta:
        model = DispenseRecord
        fields = ['id', 'prescription_id', 'pharmacist', 'date', 'pharmacy', 'dispense_items']

    def create(self, validated_data):
        items_data = validated_data.pop('dispense_items')
        record = DispenseRecord.objects.create(**validated_data)

        for item in items_data:
            # Reduce medicine stock
            medicine = Medicine.objects.get(id=item['medicineId'])
            if medicine.quantity < item['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {medicine.name}")

            # Create DispenseItem using correct fields
            DispenseItem.objects.create(
                dispense_record=record,
                medicine=medicine,
                quantity=item['quantity'],
                price=item['price']
            )

            # DispenseItem.objects.create(dispenseRecordId=record, **item)
            
            medicine.quantity -= item['quantity']
            medicine.save()
            
           
            

        return record