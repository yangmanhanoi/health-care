from django.db import models
from django.utils import timezone

class Patient(models.Model):
    """Model for storing patient information related to users in auth_service."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)  # user_id from auth_service
    fullName = models.CharField(max_length=200)  # Full name as a single field
    dob = models.DateField()  # Date of birth
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    address = models.TextField()  # Address as a text field
    email = models.EmailField()
    registerDate = models.DateTimeField(default=timezone.now)

    def register(self):
        """Register a new patient."""
        self.registerDate = timezone.now()
        self.save()

    def updateProfile(self):
        """Update patient profile information."""
        self.save()

    def getHistoryRecord(self):
        """Retrieve patient medical history records."""
        # This would typically query related models like appointments, diagnoses, etc.
        # For now, we'll return a placeholder
        return []

    def __str__(self):
        return f"Patient: {self.fullName}"

    class Meta:
        db_table = 'patient_patient'
