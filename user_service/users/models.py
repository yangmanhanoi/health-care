from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid

class User(models.Model):
    """Base User model that stores general information for all users in the system."""
    
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_user_id = models.IntegerField(unique=True, null=True, blank=True)  # Reference to auth_service user
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)  # Auto-generated from first_name + last_name
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Vietnam')
    
    # System Information
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Profile Information
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    
    class Meta:
        db_table = 'users_user'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['auth_user_id']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate full_name."""
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Return the complete formatted address."""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])
    
    def get_age(self):
        """Calculate and return the user's age."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])
    
    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def activate(self):
        """Activate the user account."""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def verify(self):
        """Mark the user as verified."""
        self.is_verified = True
        self.save(update_fields=['is_verified'])
    
    def __str__(self):
        return f"{self.full_name or self.email} ({self.user_type})"


class UserActivity(models.Model):
    """Track user activities and audit trail."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('email_change', 'Email Change'),
        ('account_verification', 'Account Verification'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_user_activity'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.activity_type} at {self.timestamp}"
