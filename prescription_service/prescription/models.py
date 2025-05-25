from django.db import models

class PrescriptionStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    ACTIVE = 'ACTIVE', 'Active'
    CANCELLED = 'CANCELLED', 'Cancelled'
    PENDING_DISPENSING = 'PENDING_DISPENSING', 'Pending Dispensing'
    DISPENSED = 'DISPENSED', 'Dispensed'
    EXPIRED = 'EXPIRED', 'Expired'

class Prescription(models.Model):
    """
    Model representing a medical prescription
    """
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    diagnose = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription {self.id} for Patient {self.patient_id} by Doctor {self.doctor_id}"

class PrescriptionItem(models.Model):
    """
    Model representing an individual medication item in a prescription
    """
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medication_id = models.IntegerField()
    medication_name = models.CharField(max_length=255)  # Cached name for display
    quantity = models.IntegerField()
    dosage = models.CharField(max_length=100)  # e.g., "1 tablet"
    frequency = models.CharField(max_length=100)  # e.g., "twice daily"
    duration = models.CharField(max_length=100)  # e.g., "7 days"
    route = models.CharField(max_length=50)  # e.g., "oral", "topical"
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"
