from django.db import models
import uuid

# Create your models here.
class Doctor(models.Model):
    """Doctor model that extends user information from user_service."""
    
    EXPERIENCE_LEVELS = [
        ('junior', 'Junior (0-2 years)'),
        ('mid', 'Mid-level (3-7 years)'),
        ('senior', 'Senior (8-15 years)'),
        ('expert', 'Expert (15+ years)'),
    ]
    
    CONSULTATION_TYPES = [
        ('in_person', 'In Person'),
        ('online', 'Online'),
        ('both', 'Both'),
    ]
    
    # Core identification - references user_service
    user_service_id = models.UUIDField(unique=True)  # Reference to user_service User model
    auth_user_id = models.IntegerField(unique=True)  # Kept for backward compatibility
    
    # Doctor-specific information
    specialty = models.CharField(max_length=100)
    sub_specialty = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    medical_school = models.CharField(max_length=200, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='junior')
    years_of_experience = models.IntegerField(default=0)
    
    # Professional details
    hospital_affiliation = models.CharField(max_length=200, blank=True, null=True)
    clinic_address = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    consultation_types = models.CharField(max_length=20, choices=CONSULTATION_TYPES, default='both')
    
    # Availability and scheduling
    is_available = models.BooleanField(default=True)
    max_patients_per_day = models.IntegerField(default=20)
    consultation_duration = models.IntegerField(default=30)  # in minutes
    
    # Professional credentials
    certifications = models.TextField(blank=True, help_text="Comma-separated list of certifications")
    languages_spoken = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of languages")
    
    # Ratings and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    total_consultations = models.IntegerField(default=0)
    
    # System fields
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_info'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_service_id']),
            models.Index(fields=['auth_user_id']),
            models.Index(fields=['specialty']),
            models.Index(fields=['is_available']),
            models.Index(fields=['average_rating']),
        ]

    def __str__(self):
        return f"Dr. {self.license_number} ({self.specialty})"
    
    def get_specialties(self):
        """Return primary and sub-specialty."""
        specialties = [self.specialty]
        if self.sub_specialty:
            specialties.append(self.sub_specialty)
        return specialties
    
    def get_certifications_list(self):
        """Return certifications as a list."""
        if self.certifications:
            return [cert.strip() for cert in self.certifications.split(',')]
        return []
    
    def get_languages_list(self):
        """Return languages as a list."""
        if self.languages_spoken:
            return [lang.strip() for lang in self.languages_spoken.split(',')]
        return []
    
    def update_rating(self, new_rating):
        """Update average rating with new rating."""
        total_score = self.average_rating * self.total_reviews + new_rating
        self.total_reviews += 1
        self.average_rating = total_score / self.total_reviews
        self.save(update_fields=['average_rating', 'total_reviews'])
    
    def increment_consultations(self):
        """Increment total consultations count."""
        self.total_consultations += 1
        self.save(update_fields=['total_consultations'])

