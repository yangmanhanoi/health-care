from django.db import models
from django.utils import timezone
import uuid

class Patient(models.Model):
    """Patient model that extends user information from user_service."""
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    EMERGENCY_CONTACT_RELATIONSHIP = [
        ('parent', 'Parent'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    
    # Core identification - references user_service
    user_service_id = models.UUIDField(unique=True)  # Reference to user_service User model
    auth_user_id = models.IntegerField(unique=True)  # Kept for backward compatibility (user_id from auth_service)
    
    # Medical Information
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    allergies = models.TextField(blank=True, help_text="Known allergies, comma-separated")
    chronic_conditions = models.TextField(blank=True, help_text="Chronic medical conditions, comma-separated")
    current_medications = models.TextField(blank=True, help_text="Current medications, comma-separated")
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(
        max_length=20, 
        choices=EMERGENCY_CONTACT_RELATIONSHIP, 
        blank=True
    )
    
    # Insurance Information
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    insurance_group_number = models.CharField(max_length=50, blank=True)
    
    # Medical History Tracking
    last_checkup_date = models.DateField(blank=True, null=True)
    total_appointments = models.IntegerField(default=0)
    total_prescriptions = models.IntegerField(default=0)
    
    # Preferences
    preferred_language = models.CharField(max_length=50, default='English')
    communication_preference = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('phone', 'Phone Call'),
            ('app', 'Mobile App'),
        ],
        default='email'
    )
    
    # System fields
    is_active = models.BooleanField(default=True)
    register_date = models.DateTimeField(default=timezone.now)  # Renamed from registerDate
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_patient'
        ordering = ['-register_date']
        indexes = [
            models.Index(fields=['user_service_id']),
            models.Index(fields=['auth_user_id']),
            models.Index(fields=['blood_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['register_date']),
        ]

    def __str__(self):
        return f"Patient {self.auth_user_id}"
    
    def register(self):
        """Register a new patient."""
        self.register_date = timezone.now()
        self.save()

    def updateProfile(self):
        """Update patient profile information."""
        self.updated_at = timezone.now()
        self.save()

    def getHistoryRecord(self):
        """Retrieve patient medical history records."""
        # This would typically query related models like appointments, diagnoses, etc.
        # For now, we'll return a placeholder
        return []
    
    def get_allergies_list(self):
        """Return allergies as a list."""
        if self.allergies:
            return [allergy.strip() for allergy in self.allergies.split(',')]
        return []
    
    def get_chronic_conditions_list(self):
        """Return chronic conditions as a list."""
        if self.chronic_conditions:
            return [condition.strip() for condition in self.chronic_conditions.split(',')]
        return []
    
    def get_current_medications_list(self):
        """Return current medications as a list."""
        if self.current_medications:
            return [medication.strip() for medication in self.current_medications.split(',')]
        return []
    
    def calculate_bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    def increment_appointments(self):
        """Increment total appointments count."""
        self.total_appointments += 1
        self.save(update_fields=['total_appointments'])
    
    def increment_prescriptions(self):
        """Increment total prescriptions count."""
        self.total_prescriptions += 1
        self.save(update_fields=['total_prescriptions'])
    
    def update_last_checkup(self, checkup_date=None):
        """Update last checkup date."""
        self.last_checkup_date = checkup_date or timezone.now().date()
        self.save(update_fields=['last_checkup_date'])
