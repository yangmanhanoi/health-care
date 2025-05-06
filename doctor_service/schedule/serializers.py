from rest_framework import serializers
from .models import Availability
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time']
    
    def validate(self, data):
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot set availability in the past.")
        
        start = data['start_time']
        end = data['end_time']

        # Chỉ cho phép giờ từ 09:00 đến 17:00
        earliest = datetime.time(9, 0)
        latest = datetime.time(17, 0)

        if not (earliest <= start < latest):
            raise serializers.ValidationError("Start time must be between 09:00 and before 17:00.")
        if not (earliest < end <= latest):
            raise serializers.ValidationError("End time must be between after 09:00 and up to 17:00.")
        if (datetime.datetime.combine(data['date'], end) - datetime.datetime.combine(data['date'], start)).total_seconds() != 1800:
            raise serializers.ValidationError("Availability must be exactly 30 minutes long.")
        overlapping = Availability.objects.filter(
            doctor=data['doctor'],
            date=data['date'],
            start_time__lt=end,
            end_time__gt=start
        ).exists()
        if overlapping:
            raise serializers.ValidationError("This time slot overlaps with an existing availability.")
        return data