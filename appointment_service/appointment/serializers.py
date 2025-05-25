from rest_framework import serializers
from .models import Appointment, AppointmentStatus
from django.utils import timezone
from datetime import datetime, time
import requests
from django.core.exceptions import ValidationError
DOCTOR_SERVICE_URL = "http://service-doctor:8002/api/"
class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.CharField(max_length=255)  # or UUIDField depending on your ID type
    patient_id = serializers.CharField(max_length=255)  # or UUIDField depending on your ID type
    status = serializers.ChoiceField(choices=AppointmentStatus.choices, default=AppointmentStatus.SCHEDULED)
    date = serializers.DateField()
    time = serializers.CharField(max_length=5)  # Format: HH:MM

    class Meta:
        model = Appointment
        fields = ['id', 'doctor_id', 'patient_id', 'status', 'date', 'time', 'price', 'diagnose', 'conclusion', 'need_lab_test']
        read_only_fields = ['status', 'price']

    def validate(self, data):
        doctor_id = data['doctor_id']
        appointment_date = data['date']
        appointment_time_str = data['time']
        if not self.validate_doctor(doctor_id=doctor_id):
            raise serializers.ValidationError("Doctor not found.")
        if not self.validate_appointment(doctor_id=data['doctor_id'], date=data['date'], time=data['time']):
            raise serializers.ValidationError("This time slot is already booked for the doctor.")
        if not self.validate_date_time(date=appointment_date, time_str=appointment_time_str, doctor_id=doctor_id):
            raise serializers.ValidationError("Invalid date or time.")
        return data

    def validate_doctor(self, doctor_id):
        try:
            response = requests.get(f"{DOCTOR_SERVICE_URL}info/doctors/{doctor_id}")
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise ValidationError("Doctor service is unavailable or returned an unexpected response.")

        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error calling doctor service: {str(e)}")

    def validate_appointment(self, doctor_id, date, time):
        try:
            time_obj = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            raise serializers.ValidationError("Time must be in HH:MM format.")
        if Appointment.objects.filter(
            doctor_id=doctor_id,
            date=date,
            time=time_obj
        ).exists():
            raise ValidationError("This time slot is already booked for the doctor")
        return True

    def validate_date_time(self, date, time_str, doctor_id):
        appointment_date = date
        appointment_time_str = time_str  # format: 'HH:MM'

        # 1. Chuyển thời gian từ chuỗi sang object
        try:
            appointment_time = datetime.strptime(appointment_time_str, "%H:%M").time()
        except ValueError:
            raise ValidationError("Time must be in HH:MM format")

        # 3. Chỉ cho phép đặt trong khung giờ hợp lệ (09:00 - 17:00)
        valid_times = [time(h, m) for h in range(9, 17) for m in (0, 30)]
        if appointment_time not in valid_times:
            raise ValidationError("Invalid time slot. Choose between 09:00 and 17:00 in 30-minute intervals")

        # 2. Không cho đặt lịch quá khứ
        now = timezone.now()
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        appointment_datetime_aware = timezone.make_aware(appointment_datetime)
        if appointment_datetime_aware < now:
            raise ValidationError("Cannot create appointment in the past")

        # 4. Kiểm tra xem thời gian có nằm trong khoảng thời gian của bác sĩ không
        try:
            response = requests.get(f"{DOCTOR_SERVICE_URL}schedule/availabilities/doctor/{doctor_id}")
            if response.status_code == 200:
                schedule = response.json()
                for slot in schedule:
                    start_time = self.parse_time(slot['start_time'])
                    end_time = self.parse_time(slot['end_time'])
                    if start_time <= appointment_time <= end_time:
                        return True
                raise ValidationError("The selected time is outside the doctor's availability.")
            else:
                raise ValidationError("Doctor service is unavailable or returned an unexpected response.")
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error calling doctor service: {str(e)}")


    def parse_time(self, time_str):
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            raise serializers.ValidationError("Time must be in HH:MM format")