from django.db import models

# Create your models here.

class AppointmentStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    FINISHED = 'FINISHED', 'Finished'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    INVOICED = 'INVOICED', 'Invoiced'
    CANCELED = 'CANCELED', 'Canceled'
    DENIED = 'DENIED', 'Denied'
    REJECTION_REQUESTED = 'REJECTION_REQUESTED', 'Rejection Requested'
    REJECTED = 'REJECTED', 'Rejected'
    EXCHANGE_REQUESTED = 'EXCHANGE_REQUESTED', 'Exchange Requested'

    # Visit status
    DIAGNOSING = 'DIAGNOSING', 'Diagnosing'
    TESTING = 'TESTING', 'Testing'
    CONCLUDING = 'CONCLUDING', 'Concluding'

class Appointment(models.Model):
    doctor_id = models.CharField(max_length=255)
    patient_id = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=5)  # Format: HH:MM
    status = models.CharField(max_length=50, choices=AppointmentStatus.choices, default=AppointmentStatus.SCHEDULED)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100000.00)

    # Visit fields
    diagnose = models.TextField(blank=True, null=True)
    conclusion = models.TextField(blank=True, null=True)
    need_lab_test = models.BooleanField(default=False)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor_id', 'date', 'time')

    def __str__(self):
        return f"Appointment with {self.doctor_id} on {self.date} at {self.time}"